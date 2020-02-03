import boto3
import datetime
import json
import requests
import time
import argparse
import os

account_number = boto3.client('sts').get_caller_identity().get('Account')


def post_message(slack_url, slack_user, dry_run, user, key_name, key_age):
    message = 'Your AWS CLI Key in AWS Account %s with ID of %s is %s days old, please rotate it on the following account '\
              'https://%s.signin.aws.amazon.com/console. If you have any issues please reach out to @%s' % (
        account_number,
        key_name,
        key_age.days,
        account_number,
        slack_user
    )
    slack_data = {
        'text': message,
        'channel': user,
        'username': 'AWS_Notifications',
        'icon_emoji': ':sadcloud:',
    }
    if not dry_run:
        response = requests.post(
            slack_url, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            print('Having issues notifying user, fall back to myself.')
            slack_data['text'] = '%s\'s AWS CLI Key in AWS Account %s with ID of %s is %s days old.' % (
                user,
                account_number,
                key_name,
                key_age.days
            )
            slack_data['channel'] = '@patrick.pierson'
            requests.post(
                slack_url, data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'}
            )
    else:
        print('Would have notified %s\n' % user)


def main(slack_url, slack_user, dry_run):
    if dry_run:
        print('This will be a dry run.')
    time_now = datetime.datetime.now()
    client = boto3.client('iam')
    response = client.list_users(MaxItems=500)
    users = []
    for i in response.get('Users'):
        users.append(i.get('UserName'))
    notified_users = []
    for i in users:
        response = client.list_access_keys(UserName=i)
        for j in response.get('AccessKeyMetadata'):
            key_age = time_now - j.get('CreateDate').replace(tzinfo=None)
            if key_age.days > 90:
                notified_users.append(i)
                print('Username: %s' % i)
                print('Key ID is %s' % j.get('AccessKeyId'))
                print('Key is %s days old' % key_age .days)
                post_message(slack_url, slack_user, dry_run, '@%s' % i, j.get('AccessKeyId'), key_age)
                if not dry_run:
                    time.sleep(1)
    print('Notified %s users' % len(notified_users))


if __name__== "__main__":
    parser = argparse.ArgumentParser(description='Notify users in an AWS account that their IAM Access Key is over 90 days old.')
    parser.add_argument('--slack-url', default=os.environ.get('SLACK_URL'), help='Slack webhook to push to slack')
    parser.add_argument('--slack-user', default=os.environ.get('SLACK_USER'), help='Slack Username for reach out message, dont include @')
    parser.add_argument('--dry-run', action="store_true", default=False, help='If set no slack message is sent')
    args = parser.parse_args()
    main(args.slack_url, args.slack_user, args.dry_run)
