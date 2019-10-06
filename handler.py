import boto3
import logging
import os
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('logs')

RETENTION = int(os.environ['RETENTION'])
NO_RETENTION_TAG = os.environ['NO_RETENTION_TAG']


def get_retention_list():
    logger.info("start function: {}".format(sys._getframe().f_code.co_name))

    next_token = ''
    log_groups = []
    log_group = {}

    while True:
        if not next_token:
            responses = client.describe_log_groups(limit=1)
        else:
            responses = client.describe_log_groups(
                nextToken=next_token, limit=1)

        log_group['log_group_name'] = responses['logGroups'][0]['logGroupName']
        log_group['retention'] = responses['logGroups'][0].get(
            'retentionInDays')
        log_group['no_changa_flg'] = check_exclude_log_group(
            log_group['log_group_name'])
        log_group['size'] = responses['logGroups'][0].get('storedBytes')

        log_groups.append(log_group.copy())
        next_token = responses.get('nextToken')

        if next_token is None:
            break

    for log_group in log_groups:
        if log_group['no_changa_flg']:
            logger.info(
                'GroupName:{} Retention:{} size:{} {}:{}'.format(
                    log_group['log_group_name'],
                    log_group['retention'],
                    log_group['size'],
                    NO_RETENTION_TAG,
                    log_group['no_changa_flg']))
        else:
            logger.info(
                'GroupName:{} Retention:{} size:{}'.format(
                    log_group['log_group_name'],
                    log_group['retention'],
                    log_group['size']))

    return log_groups


def check_exclude_log_group(log_group_name):

    response = client.list_tags_log_group(logGroupName=log_group_name)

    for tag, value in response['tags'].items():
        if tag == NO_RETENTION_TAG and value == 'True':
            return True
    return False


def chnage_retention(log_group_name, set_retention=14):

    client.put_retention_policy(
        logGroupName=log_group_name,
        retentionInDays=set_retention
    )
    logger.info(
        'change: GroupName:{} Retention:{}'.format(
            log_group_name, set_retention))


def delete_log_group(log_group_name, size):

    client.delete_log_group(logGroupName=log_group_name)
    logger.info(
        'delete: GroupName:{} Size:{}'.format(
            log_group_name, size))


def lambda_handler(event, context):
    logger.info("start function: {}".format(sys._getframe().f_code.co_name))

    try:
        return_values = {}

        logger.info('--- before chage ---')
        log_groups = get_retention_list()

        logger.info('--- chage ---')

        for log_group in log_groups:
            log_group_name = log_group['log_group_name']
            retention = log_group['retention']
            size = log_group['size']
            set_retention = RETENTION

            if check_exclude_log_group(log_group_name) == False:
                if retention is None or retention > set_retention:
                    chnage_retention(
                        log_group_name, set_retention=set_retention)

            if size == 0:
                delete_log_group(log_group_name, size)

        logger.info('--- after chage ---')
        log_groups = get_retention_list()

        return return_values

    except Exception as e:
        logger.error("error ocured {}".format(e))
        return_values['error_desc'] = str(e)
        return return_values
