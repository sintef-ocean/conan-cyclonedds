/****************************************************************

  Generated by Eclipse Cyclone DDS IDL to C Translator
  File name: HelloWorldData.c
  Source: HelloWorldData.idl
  Cyclone DDS: V0.8.2

*****************************************************************/
#include "HelloWorldData.h"

static const dds_key_descriptor_t HelloWorldData_Msg_keys[1] =
{
  { "userID", 0 }
};

static const uint32_t HelloWorldData_Msg_ops [] =
{
  DDS_OP_ADR | DDS_OP_TYPE_4BY | DDS_OP_FLAG_SGN | DDS_OP_FLAG_KEY, offsetof (HelloWorldData_Msg, userID),
  DDS_OP_ADR | DDS_OP_TYPE_STR, offsetof (HelloWorldData_Msg, message),
  DDS_OP_RTS
};

const dds_topic_descriptor_t HelloWorldData_Msg_desc =
{
  sizeof (HelloWorldData_Msg),
  sizeof (char *),
  DDS_TOPIC_NO_OPTIMIZE | DDS_TOPIC_FIXED_KEY,
  1u,
  "HelloWorldData::Msg",
  HelloWorldData_Msg_keys,
  3,
  HelloWorldData_Msg_ops,
  ""
};
