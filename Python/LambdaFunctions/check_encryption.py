#Checks root volume for encryption. Prints outcome. Will amend for future RDK rule

#Import required libraries
import boto3

#Begin AWS Lambda function
def lambda_handler(event, context):
    #Set client and resource variables.
    ec2_resource = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')

    #List all snappshots belonging to account.
    list_snaps = ec2_client.describe_snapshots(
        OwnerIds=[
            'self'
        ]
    )
    
    #Begin encryption check
    for id in list_snaps['Snapshots']:
        snap_id = id['SnapshotId']
        test_encrypt = ec2_resource.Snapshot(str(snap_id)).encrypted
        print('Snapshot with ID of '+ str(snap_id) + ' is returning a value of ' + str(test_encrypt) + ' for an encryption value.')
        if test_encrypt == False:
            print("I cant beleive you've done this! Alerting Mom!")
        elif test_encrypt == True:
            print('Good enough for government work, carry on.')
        else:
            print('Houston we have a problem')
    return
