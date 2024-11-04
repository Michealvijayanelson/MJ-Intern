import boto3
from PIL import Image
import io

s3 = boto3.client('s3')
sns = boto3.client('sns')
ses = boto3.client('ses')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Get the image from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_content = response['Body'].read()
    image = Image.open(io.BytesIO(image_content))

    # Resize the image
    image = image.resize((800, 800))  # Resize to 800x800

    # Save to a bytes buffer
    buffer = io.BytesIO()
    image.save(buffer, 'JPEG')
    buffer.seek(0)
    # Upload resized image back to S3
    s3.put_object(Bucket='resized-images-bucket', Key=key, Body=buffer)
    # Send notification through SNS
    sns.publish(
        TopicArn='arn:aws:sns:REGION:ACCOUNT_ID:YourSNSTopic',
        Message=f'Image {key} has been resized and saved to S3.',
        Subject='Image Processing Notification'
    )
    # Send email through SES
    ses.send_email(
        Source='your_verified_email@example.com',
        Destination={'ToAddresses': ['user_email@example.com']},
        Message={
            'Subject': {'Data': 'Image Processed'},
            'Body': {
                'Text': {'Data': f'Your image {key} has been processed and is available in the resized-images bucket.'}
            }
        }
    )
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ImageMetadataTable')

def store_metadata(key):
    table.put_item(
        Item={
            'ImageKey': key,
            'Status': 'Processed',
            'Timestamp': str(datetime.datetime.now())
        }
    )

