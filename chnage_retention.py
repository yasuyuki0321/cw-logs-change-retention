import boto3

client = boto3.client('logs')


def get_retention_list():
    next_token = ''
    log_groups = []
    retentions = []

    while True:
        if not next_token:
            responses = client.describe_log_groups(limit=1)
        else:
            responses = client.describe_log_groups(nextToken=next_token, limit=1)

        log_group = responses['logGroups'][0]['logGroupName']
        retention = responses['logGroups'][0].get('retentionInDays')

        log_groups.append(log_group)
        retentions.append(retention)

        next_token = responses.get('nextToken')

        if next_token is None:
            break

    for log_group, retention in zip(log_groups, retentions):
        print('GroupName:{} Retention:{}'.format(log_group, retention))


def chnage_retention(set_retention=7):
    next_token = ''
    while True:
        if not next_token:
            responses = client.describe_log_groups(limit=1)
        else:
            responses = client.describe_log_groups(nextToken=next_token, limit=1)

        log_group = responses['logGroups'][0]['logGroupName']
        retention = responses['logGroups'][0].get('retentionInDays')

        if retention is None or retention > retention:
            client.put_retention_policy(
                logGroupName=log_group,
                retentionInDays=set_retention
            )
            print('change: GroupName:{} Retention:{}'.format(log_group, set_retention))

        next_token = responses.get('nextToken')

        if next_token is None:
            break


if __name__ == '__main__':
    print('--- before chage ---')
    get_retention_list()
    chnage_retention()
    print('--- after chage ---')
    get_retention_list()
