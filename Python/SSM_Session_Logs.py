#Un-finished/tested. Reomoving/storing from environment being depricated. 

import json
import boto3

#Boto3 clients required
ec2_client = boto3.client('ec2')
ssm_client = boto3.client('ssm')

#Get working list of all instances in the environment.
running_instance_list = []
filters = [
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
all_instances = ec2_client.describe_instances(Filters=filters)
for reservations in all_instances['Reservations']:
    for instance in reservations['Instances']:
        running_instance_list.append(instance['InstanceId'])

for running_instance in running_instance_list:
    ssm_client.send_command(
        InstanceIds=[running_instance],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': ['last']},
        )
    command_id = response['Command']['CommandId']
    output = ssm_client.get_command_invocation(
      CommandId=command_id,
      InstanceId=running_instance,
    )
def lambda_handler(event, context):
    print(running_instance_list)
