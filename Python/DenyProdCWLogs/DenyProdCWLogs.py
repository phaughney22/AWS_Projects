# Things to do for this script to work:
#   1. Set appropriate groups for allowed_groups
#   2. Create IAM role that restricts appropriate logs and set it to restricted_group_to_add
#   3. Set trigger for lambda function. The trigger should be a CloudWatch trigger that points to the CloudWatch group that contains the CloudTrail logs.
#   4. Set the filter on the trigger to only send IAMUser type logs (prevents infinite loop of lambda function) and to check for the appropriate ClowdWatch logsgroups
#   Example for the trigger filter: { $.requestParameters.logGroupName = "ProductionSensativeData" && $.userIdentity.type = "IAMUser" }
#
#   Example for cooresponding IAM restriction role.
#
#{
#    "Version": "2012-10-17",
#    "Statement": [
#        {
#            "Sid": "VisualEditor0",
#            "Effect": "Deny",
#            "Action": [
#                "logs:DescribeQueries",
#                "logs:GetLogRecord",
#                "logs:PutDestinationPolicy",
#                "logs:StopQuery",
#                "logs:TestMetricFilter",
#                "logs:DeleteDestination",
#                "logs:CreateLogGroup",
#                "logs:GetLogDelivery",
#                "logs:ListLogDeliveries",
#                "logs:CreateLogDelivery",
#                "logs:DeleteResourcePolicy",
#                "logs:PutResourcePolicy",
#                "logs:DescribeExportTasks",
#                "logs:GetQueryResults",
#                "logs:UpdateLogDelivery",
#                "logs:CancelExportTask",
#                "logs:DeleteLogDelivery",
#                "logs:PutDestination",
#                "logs:DescribeResourcePolicies",
#                "logs:DescribeDestinations"
#            ],
#            "Resource": "*"
#        },
#        {
#            "Sid": "VisualEditor1",
#            "Effect": "Deny",
#            "Action": "logs:*",
#            "Resource": [
#                "arn:aws:logs:us-east-1:123456789101:log-group:ProductionSensativeData:*"
#            ]
#        }
#    ]
#}

import gzip
import base64
import json
import boto3

iam_resource = boto3.resource('iam')

#Whitelist of IAM groups allowed to access prod logs. Also include the restricted group in order to reduce number of API calls.
allowed_groups = ['Developers', 'Admin']
restricted_group_to_add = 'Developers'

def lambda_handler(event, context):
    #Decodes the compressed cloudwatch event
    cw_data = event['awslogs']['data']
    compressed_payload = base64.b64decode(cw_data)
    uncompressed_payload = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed_payload)
    log_events = payload['logEvents']
    for log_event in log_events:
        message = log_event['message']
        print('Message: ' + message)

        # Turn event into JSON
        event_details = json.loads(message)
        print(type(event_details))

        # Obtain user making DescribeLogStreams call
        user_identity = event_details['userIdentity']
        user_type = user_identity['type']

        # Obtain logstream the user is requesting
        request_params = event_details['requestParameters']
        logstream = request_params['logGroupName']

        if user_type != 'IAMUser':
            print('API call was not made by IAM user. Quitting.')
        if (logstream != 'ProductionSensativeData'):
            print('API call not made to restricted production logs. Quitting.')
        else:
            user_name = str(user_identity['userName'])
            user = iam_resource.User(user_name)
            group_iterator = user.groups.all()
            groups_of_user = []
            print(user.name)
            for group in group_iterator:
                groups_of_user.append(group)
            for groups in groups_of_user:
                group_name = groups.name
                print(groups_of_user)
            if len(groups_of_user) < 1:
                print('Groups of user were not found')
            else:
                if group_name in allowed_groups:
                    print('User has Admin rights. No action required.')
                else:
                    print('User is not part of admin group...need to revoke privlidges.')
                    user.add_group(GroupName=restricted_group_to_add)
