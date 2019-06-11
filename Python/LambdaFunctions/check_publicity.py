#Checks if AMI is publicly available. Prints outcome. Will amend for future RDK rule

#Import libraries.
import boto3

#Begin AWS Lambda function
def lambda_handler(event, context):
    #Set client and resource variables.
    ec2_resource = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')

    #List all images belonging to account.
    all_images = ec2_client.describe_images(
        Owners=[
            'self'
        ]
    )

    #Begin publicity check
    for image in all_images['Images']:
        image_id = image['ImageId']
        image_publicity =  ec2_resource.Image(str(image_id)).public
        print('AMI with image ID of ' + str(image_id) + ' is returning a value of ' + str(image_publicity) + ' for if it is publicly available or not.')
        if image_publicity == True:
            print("I cant beleive you've done this! Alerting Mom!")
        elif image_publicity == False:
            print('Good enough for government work, carry on.')
        else:
            print('Houston we have a problem')
    return
