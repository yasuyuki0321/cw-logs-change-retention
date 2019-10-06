#!/bin/sh

ACTION=$1
LOG_GROUP=$2
VALUE=$3

return_val=0

get_log_group() {
  aws logs describe-log-groups --query logGroups[].[logGroupName] --output text

  if [[ $? != 0 ]]; then
    return 1
  fi
}

check_log_group_exists() {
  exists=1
  log_group_name=$1
  
  get_log_group | grep -qx $log_group_name
  
  if [[ $? != 0 ]]; then
    return 1
  fi
}

describe_log_group() {
  log_group_name=$1

  check_log_group_exists $log_group_name

  if [[ $? == 0 ]]; then
    tag=`get_tags $log_group_name`
    echo "log_group: $log_group_name tags: $tag"
    return 0
  else
    echo "$log_group_name dose not exists."
    return 1
  fi
}
get_tags() {
  log_group_name=$1
  tag=`aws logs list-tags-log-group --log-group-name $log_group_name | jq -r ".tags"`
  
  if [[ $? != 0 ]]; then
    return 1
  fi
  echo $tag
}

add_tag() {
  log_group_name=$1
  tag_name=$2
  tag_value=$3

  aws logs tag-log-group --log-group-name $log_group_name --tags $tag_name=$tag_value

  if [[ $? != 0 ]]; then
    return 1
  fi
}

delete_tag() {
  log_group_name=$1
  tag_name=$2

  aws logs untag-log-group --log-group-name $log_group_name --tags $tag_name

  if [[ $? != 0 ]]; then
    return 1
  fi
}

# main
if [ $ACTION = 'list' ]; then
  get_log_group
  return_val=0
elif [ $ACTION = 'describe' ]; then
  describe_log_group $LOG_GROUP
  if [[ $? == 0 ]]; then
    return_val=0
  else
    return_val=1
  fi
elif [ $ACTION = 'add' ]; then
  add_tag $LOG_GROUP NoChangeRetention 'True'
  describe_log_group $LOG_GROUP
  if [[ $? != 0 ]]; then
    return_val=1
  fi
elif [ $ACTION = 'delete' ]; then
  describe_log_group $LOG_GROUP
  if [[ $? == 0 ]]; then
    get_tags $LOG_GROUP | grep -wq NoChangeRetention
    if [[ $? == 0 ]]; then
      delete_tag $LOG_GROUP NoChangeRetention
      delete_tag $LOG_GROUP test
      delete_tag $LOG_GROUP retention
      if [[ $? != 0 ]]; then
        return_val=1
      fi
      describe_log_group $LOG_GROUP
      if [[ $? != 0 ]]; then
        return_val=1
      fi
    else
      return_val=1
    fi
  fi
fi

