## DEPLOY LAMBDA FUNCTION TO CREATE WEEKLY EC2 AMI BACKUP


## Goal
The goals of this project are to create weekly EC2 AMI backups of all EC2 instances running in the us-east-1 region and to delete AMIs older than 30 days.

## Pre-Requisites
01. Deploy Lambda Function as per the architecture shown above with required IAM roles.
02. Schedule Lambda Function to run weekly once Sunday 5 AM EST using cloudwatch event as Lambda trigger.
03. Create an SNS topic and subscribe email to receive notifications.

## Automation
01. Write Python code as per the below high level requirement create AMI and delete old AMIs.
- Describe list of all EC2 instances in the us-east-1 region.
- Get the list of EC2 Instance IDs as list data type
- Get the EC2 Tag having key “Name”
- Loop the list of Instance IDs and create AMI
- Add tags to the AMI – Assign the EC2 Name tag to the AMI to identify which AMI belongs to which EC2 instance.
- Add description to the AMI to understand which AMI belongs to which server.
- Add name to the AMI – Name includes server name (Get from Instance Tag) append with the date when the AMI was created.
- Delete the old unused AMIs whichever is older than 30 days from the date of AMI creation.
- Ensure that only unused AMIs are deleted, Skip the AMIs that are in use.
- Print the AMIs that are deleted.
- Print exceptions if any issues in creating or deleting AMI
- Notify the SNS topic if there are any exceptions in creating or deleting AMI.

02. Deploy Python code to Lambda Function.

## Validation
Run Lambda Function and verify AMI copy created for all EC2 instances with tags and deleted unused AMIs older than 30 days.


## LET'S DO IT
To achieve the goal of creating weekly EC2 AMI backups and deleting AMIs older than 30 days, follow these steps:

## Architecture Overview
01. AWS Lambda: The core of the automation, running Python code to handle AMI creation and deletion.
02. AWS IAM Roles: Provide the necessary permissions for the Lambda function to interact with EC2, CloudWatch, and SNS.
03. AWS CloudWatch Events: Trigger the Lambda function weekly.
04. AWS SNS: Send notifications about the Lambda function’s execution status.


## Pre-Requisites
01.	IAM Role for Lambda: Create an IAM role with the following permissions:
- ec2:DescribeInstances
- ec2:CreateImage
- ec2:DescribeImages
- ec2:DeregisterImage
- sns:Publish
02.	CloudWatch Event Rule: Schedule the Lambda function to run every Sunday at 5 AM EST.
03.	EC2 Instances: Ensure you have at least 5 EC2 instances  with the tags
04.	SNS Topic: Create an SNS topic and subscribe to an email address for notifications.

## Step-by-Step Guide to Create and Deploy a Valid Lambda Function ZIP File
01. Write the Python Code
First, create a Python file named lambda_function.py with the following content. Lambda Function Code. Below is the Python code to be deployed in the Lambda function:

```bash
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
```
02. Create a ZIP File
   1. Create a Directory:
- Create a new directory to store your Lambda function code.
- Place your lambda_function.py file in this directory.
   2. Zip the Directory:
- Open a terminal or command prompt and navigate to the directory containing your lambda_function.py.
- Run the following command to create a ZIP file:
```bash
zip -r function.zip lambda_function.py
```
Ensure that the function.zip file is not empty and contains the lambda_function.py

## NOTE
If the zip utility is not installed on your system. You need to install it to create ZIP files. Here are the steps to install the zip utility on different operating systems:
For Linux (Debian/Ubuntu):
```bash
sudo apt-get update
sudo apt-get install zip -y
```
For Linux (CentOS/RHEL):
```bash
sudo yum install zip -y
```
For macOS:
If you are using Homebrew (recommended), you can install zip with:
```bash
brew install zip
```

For Windows:
If you are using Git Bash or a similar environment that supports Unix commands, you might need to install the zip utility. Otherwise, you can use built-in Windows tools or third-party software like 7-Zip.
Once the zip utility is installed, you can create the ZIP file as follows:
## Creating the ZIP file
01. Create a Directory:
- Create a new directory to store your Lambda function code.
- Place your lambda_function.py file in this directory.
02 Zip the Directory:
- Open a terminal or command prompt and navigate to the directory containing your lambda_function.py.
- Run the following command to create a ZIP file:
 Create a directory (if not already created):
```bash
mkdir my_lambda_function
```
 Move the lambda_function.py file into the directory
```bash
mv lambda_function.py my_lambda_function/
```
Navigate to the directory
```bash
cd my_lambda_function
```
Create the ZIP file
```bash
zip -r function.zip lambda_function.py
```
After running these commands, you should have a function.zip file that you can upload to AWS Lambda.

You can install the zip utility using PowerShell on Windows by leveraging a package manager such as choco (Chocolatey) or winget (Windows Package Manager). Here are the steps to install zip using these methods:

Method 1: Using Chocolatey
Step 1: Install Chocolatey
If you don't have Chocolatey installed, you can install it using the following command in an elevated PowerShell window (Run as Administrator):
```bash
Set-ExecutionPolicy Bypass -Scope Process -Force; `
[System.Net.ServicePointManager]::SecurityProtocol = `
[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
Step 2: Install zip Utility:
```bash
choco install zip -y
```
Step 3: Verify Installation:
```bash
zip --version
```
By following these steps, you should be able to install the zip utility on Windows using PowerShell, and then use it in Git Bash or any other command line environment.


## Deploying the Lambda Function
1. Create IAM Role for Lambda
Using AWS Management Console:
	1.	Open the IAM console at https://console.aws.amazon.com/iam/.
	2.	In the navigation pane, choose Roles and then Create roles.
	3.	Choose AWS service and then Lambda. Click Next: Permissions.
	4.	Attach the necessary policies:
	•	AmazonEC2FullAccess
	•	AmazonSNSFullAccess
	•	CloudWatchLogsFullAccess
	•	AmazonEC2ReadOnlyAccess (for ec2:Describe* actions)
	5.	Click Next: Tags and then Next: Review.
	6.	Enter a Role name (e.g., LambdaAMIBackupRole) and click Create role.


2. Create Lambda Function
Using AWS Management Console:
	1.	Open the Lambda console at https://console.aws.amazon.com/lambda/.
	2.	Click Create function.
	3.	Choose an Author from scratch.
	•	Function name: WeeklyAMIBackup
	•	Runtime: Python 3.8
	•	Role: Choose an existing role (LambdaAMIBackupRole)
	4.	Click Create function.
	5.	In the Function code section, replace the default code with the provided Python code.
	6.	Click Deploy.

Upload the ZIP File to AWS Lambda
Using AWS Management Console:
    1. Open the Lambda console at https://console.aws.amazon.com/lambda/.
    2. Select your function WeeklyAMIBackup.
    3. In the Function code section, choose Upload from > .zip file.
    4. Click Upload, select the function.zip file you created, and click Save.

Using AWS CLI:
```bash
aws lambda update-function-code \
    --function-name WeeklyAMIBackup \
    --zip-file fileb://function.zip
```

Using Terraform:
```bash
resource "aws_iam_role" "lambda_role" {
  name = "LambdaAMIBackupRole"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}


resource "aws_lambda_function" "weekly_ami_backup" {
  filename         = "function.zip"
  function_name    = "WeeklyAMIBackup"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("function.zip")
  runtime          = "python3.8"
}
```
3. Schedule with CloudWatch Events
Using AWS Management Console:
	1.	Open the CloudWatch console at https://console.aws.amazon.com/cloudwatch/.
	2.	In the navigation pane, choose Rules and then Create rules.
	3.	For Event Source, choose Event Source and then Schedule.
	4.	For Fixed rate of expression, choose Cron expression and enter 0 5 ? * 1 * (every Sunday at 5 AM EST).
	5.	Click Add target, choose Lambda function, and select WeeklyAMIBackup.
	6.	Click Create rule.


Using AWS CLI:
```bash
aws events put-rule \
    --name "WeeklyAMIBackupRule" \
    --schedule-expression "cron(0 5 ? * 1 *)"


aws events put-targets \
    --rule "WeeklyAMIBackupRule" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:WeeklyAMIBackup"
```
4. Create SNS Topic and Subscribe
Using AWS Management Console:
	1.	Open the Amazon SNS console at https://console.aws.amazon.com/sns/.
	2.	Click Create topic.
	•	Type: Standard
	•	Name: AMIBackupNotifications
	3.	Click Create topic.
	4.	Select the topic, click Create subscription.
	•	Protocol: Email
	•	Endpoint: Enter your email address
	5.	Click Create subscription and confirm the subscription in your email.


Using AWS CLI:
```bash
aws sns create-topic --name AMIBackupNotifications
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:AMIBackupNotifications --protocol email --notification-endpoint you@example.com
```

## Validation

1. Run the Lambda Function
Manually Invoke Lambda Function:
	1.	Open the Lambda console.
	2.	Select WeeklyAMIBackup and click Test
	3.	Configure test event and click Create.
	4.	Click Test again to invoke the function.
Verify AMIs:
	1.	Open the EC2 console..
	2.	In the navigation pane, choose AMIs.
	3.	Check that AMIs are created with the expected names and tags.
Check Old AMIs Deletion:
	1.	Verify that AMIs older than 30 days are deleted, except for those in use.
SNS Notifications:
	1.	Check your email for notifications from SNS about the Lambda function execution status.


2. Monitor Scheduled Runs
Using CloudWatch Logs:
	1.	Open the CloudWatch console.
	2.	Navigate to Logs and select the log group for your Lambda function.
	3.	Select the log group for the Lambda function and monitor the logs for any issues.
    4.  Verify the logs to ensure the function executed correctly.


Check CloudWatch Events:
	1.	Ensure the scheduled rule is triggering the Lambda function weekly.
	2.	Monitor SNS notifications for any issues.


## Increase Lambda Timeout Using AWS Management Console

In case you have this error message Task timed out after 3.00 seconds indicates that your AWS Lambda function execution time exceeded the default timeout limit of 3 seconds. To fix this, you need to increase the timeout setting for your Lambda function.
Here's how you can increase the timeout setting:

01. Open the AWS Lambda Console:
- Go to the AWS Management Console, and navigate to the Lambda service.
02. Select Your Lambda Function:
- Choose the Lambda function that you created for the AMI backup.
03. Modify Timeout Setting:
- In the Configuration tab, choose the "General configuration" section.
- Click the "Edit" button.
- Increase the "Timeout" value to an appropriate duration. Since AMI creation can take a bit longer, you might want to set it to 5 minutes (300 seconds) or more.
04. Save Changes:
- Click the "Save" button to apply the new settings.


Re-Run Your Lambda Function

After increasing the timeout setting, manually invoke the Lambda function again to verify that it completes successfully without timing out.
By increasing the timeout setting and using this refined code, your Lambda function should be able to handle the AMI creation and deletion process more effectively.


By following these steps and examples, you should be able to deploy, validate, and monitor your Lambda function for creating weekly EC2 AMI backups and managing old AMIs effectively.



