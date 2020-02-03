## iam-key-notify

This is iam-key-notify. You are running this because you have a lot of users in your AWS account that all have IAM names
that match their slack usernames. They also have IAM keys that are older then 90 days.

### Install

Install pipenv to your Python user directory.
> pip install --user pipenv

Run to get your pipenv environment setup.
> pipenv --three

Install dependices for this utility.
> pipenv install

### Run

Do a dry run on your account with the following.
> pipenv run python main.py --dry-run

Notify users with IAM keys over 90 days old with the following.
NOTE: You will need a slack webhook.
> export SLACK_URL=https://hooks.slack.com/services/#########/###########/###############
> pipenv run python main.py --slack-user your.username
