#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <filesystem>
#include <fstream>
#include <string>
#include <cstring>
#include <scssdk_telemetry.h>
#include <common/scssdk_telemetry_common_configs.h>
#include <common/scssdk_telemetry_common_gameplay_events.h>

namespace {
scs_telemetry_unregister_from_event_t unregister_event = nullptr;
std::string cargo = "ETS2 cargo delivery", source_city, destination_city;
const scs_named_value_t* find(const scs_named_value_t* v, const char* key) {
  if (!v) return nullptr;
  for (; v->name; ++v) if (std::strcmp(v->name,key)==0) return v;
  return nullptr;
}
std::string str(const scs_named_value_t* v,const char* key) {
  auto p=find(v,key);
  return p && p->value.type==SCS_VALUE_TYPE_string && p->value.value_string.value ? p->value.value_string.value : "";
}
double num(const scs_named_value_t* v,const char* key) {
  auto p=find(v,key); if(!p) return 0;
  switch(p->value.type) {
    case SCS_VALUE_TYPE_s64:return double(p->value.value_s64.value);
    case SCS_VALUE_TYPE_u64:return double(p->value.value_u64.value);
    case SCS_VALUE_TYPE_s32:return double(p->value.value_s32.value);
    case SCS_VALUE_TYPE_u32:return double(p->value.value_u32.value);
    case SCS_VALUE_TYPE_float:return p->value.value_float.value;
    case SCS_VALUE_TYPE_double:return p->value.value_double.value;
    default:return 0;
  }
}
std::string escape(const std::string& s) {
  std::string o;
  for(char c:s) { if(c=='"'||c=='\\') {o+='\\';o+=c;} else if(c=='\n') o+="\\n"; else if(c=='\r') o+="\\r"; else if((unsigned char)c>=32)o+=c; }
  return o;
}
void callback(const scs_event_t event,const void* info,const scs_context_t) {
  if(!info) return;
  if(event==SCS_TELEMETRY_EVENT_configuration) {
    auto c=static_cast<const scs_telemetry_configuration_t*>(info);
    if(!c->id || std::strcmp(c->id,SCS_TELEMETRY_CONFIG_job)!=0)return;
    auto v=str(c->attributes,SCS_TELEMETRY_CONFIG_ATTRIBUTE_cargo); if(!v.empty())cargo=v;
    v=str(c->attributes,SCS_TELEMETRY_CONFIG_ATTRIBUTE_source_city); if(!v.empty())source_city=v;
    v=str(c->attributes,SCS_TELEMETRY_CONFIG_ATTRIBUTE_destination_city); if(!v.empty())destination_city=v;
    return;
  }
  if(event!=SCS_TELEMETRY_EVENT_gameplay)return;
  auto e=static_cast<const scs_telemetry_gameplay_event_t*>(info);
  if(!e->id || std::strcmp(e->id,SCS_TELEMETRY_GAMEPLAY_EVENT_job_delivered)!=0)return;
  double revenue=num(e->attributes,SCS_TELEMETRY_GAMEPLAY_EVENT_ATTRIBUTE_revenue);
  double distance=num(e->attributes,SCS_TELEMETRY_GAMEPLAY_EVENT_ATTRIBUTE_distance_km);
  if(revenue<0||distance<=0)return;
  wchar_t* local=nullptr; size_t size=0;
  if(_wdupenv_s(&local,&size,L"LOCALAPPDATA")!=0||!local)return;
  std::filesystem::path dir=std::filesystem::path(local)/L"TruckRacingCareer"/L"inbox"; free(local);
  try {
    std::filesystem::create_directories(dir);
    auto ticks=GetTickCount64();
    auto temp=dir/(L"ets2-"+std::to_wstring(ticks)+L".tmp");
    auto target=dir/(L"ets2-"+std::to_wstring(ticks)+L".json");
    std::ofstream f(temp,std::ios::binary);
    if(!f)return;
    f<<"{\"schema_version\":1,\"event\":\"job.delivered\",\"job_id\":\"ets2-"<<ticks
     <<"\",\"cargo\":\""<<escape(cargo)<<"\",\"source_city\":\""<<escape(source_city)
     <<"\",\"destination_city\":\""<<escape(destination_city)<<"\",\"revenue_eur\":"<<revenue
     <<",\"distance_km\":"<<distance<<",\"earned_xp\":"<<num(e->attributes,SCS_TELEMETRY_GAMEPLAY_EVENT_ATTRIBUTE_earned_xp)
     <<",\"cargo_damage\":"<<num(e->attributes,SCS_TELEMETRY_GAMEPLAY_EVENT_ATTRIBUTE_cargo_damage)<<"}\n";
    f.close(); if(f) std::filesystem::rename(temp,target);
  } catch(...) {}
}
}
__declspec(dllexport) SCSAPI_RESULT scs_telemetry_init(const scs_u32_t version,const scs_telemetry_init_params_t* const params) {
  if(version!=SCS_TELEMETRY_VERSION_1_01)return SCS_RESULT_unsupported;
  if(!params)return SCS_RESULT_invalid_parameter;
  auto p=static_cast<const scs_telemetry_init_params_v101_t*>(params);
  if(!p->common.game_id||std::strcmp(p->common.game_id,"eut2")!=0)return SCS_RESULT_unsupported;
  unregister_event=p->unregister_from_event;
  if(p->register_for_event(SCS_TELEMETRY_EVENT_configuration,callback,nullptr)!=SCS_RESULT_ok)return SCS_RESULT_generic_error;
  if(p->register_for_event(SCS_TELEMETRY_EVENT_gameplay,callback,nullptr)!=SCS_RESULT_ok) {
    if(unregister_event)unregister_event(SCS_TELEMETRY_EVENT_configuration);
    return SCS_RESULT_generic_error;
  }
  return SCS_RESULT_ok;
}
__declspec(dllexport) SCSAPI_VOID scs_telemetry_shutdown(void) {
  if(unregister_event){unregister_event(SCS_TELEMETRY_EVENT_configuration);unregister_event(SCS_TELEMETRY_EVENT_gameplay);}
}
