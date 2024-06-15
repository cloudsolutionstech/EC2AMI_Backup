import boto3
from datetime import datetime, timedelta
import logging

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2')
sns_client = boto3.client('sns')

def lambda_handler(event, context):
    try:
        # Describe EC2 instances
        instances = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['dpt-web-server']}])
        instance_ids = [instance['InstanceId'] for reservation in instances['Reservations'] for instance in reservation['Instances']]
        
        # Create AMIs
        for instance_id in instance_ids:
            instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
            instance_name = [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'][0]
            ami_name = f"{instance_name}-{datetime.now().strftime('%Y-%m-%d')}"
            
            response = ec2_client.create_image(
                InstanceId=instance_id,
                Name=ami_name,
                Description=f"AMI of {instance_name} created on {datetime.now().strftime('%Y-%m-%d')}",
                NoReboot=True
            )
            
            ami_id = response['ImageId']
            ec2_client.create_tags(Resources=[ami_id], Tags=instance['Tags'])
            logger.info(f"Created AMI {ami_id} for instance {instance_id}")

        # Delete old AMIs
        delete_date = datetime.now() - timedelta(days=30)
        images = ec2_client.describe_images(Owners=['self'])['Images']
        
        for image in images:
            creation_date = datetime.strptime(image['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if creation_date < delete_date:
                ec2_client.deregister_image(ImageId=image['ImageId'])
                logger.info(f"Deregistered AMI {image['ImageId']} created on {creation_date}")
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        sns_client.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:YourSNSTopic',
            Subject='Error in AMI Backup Lambda Function',
            Message=str(e)
        )

    return {
        'statusCode': 200,
        'body': 'AMI backup and cleanup process completed successfully.'
    }

