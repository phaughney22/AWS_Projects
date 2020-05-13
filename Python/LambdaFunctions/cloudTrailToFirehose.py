import json
import boto3
import gzip
import base64

# Initialize Constants/Boto3 CLients
firehose_client = boto3.client('firehose')

# Set this constant to the exact name of the Firehose steam.
delivery_stream = ''

# Main/Lambda Handler
def lambda_handler(event, context):

    # Grab CloudWatch log and decode/decompress
    cloudwatch_log = event["awslogs"]["data"]
    decode_base64 = base64.b64decode(cloudwatch_log)
    decompress_data = gzip.decompress(decode_base64)
    log_data = json.loads(decompress_data)
    final_data = log_data['logEvents']

    # Cloudwatch logs come in batches, this individualizes each event
    for message in final_data:
        message_for_firehose = message['message']

        # This print statement can be removed but helpful for debugging what is being sent to Firehose
        print(message_for_firehose)

        # Send to Firehose
        send_to_firehose(message_for_firehose)

# This function sends whatever data passed to it to firehose input stream
def send_to_firehose(borrowedData):
    putrecord = firehose_client.put_record(
        DeliveryStreamName = delivery_stream,
        Record={
            'Data':borrowedData + '\n'
        }
    )
