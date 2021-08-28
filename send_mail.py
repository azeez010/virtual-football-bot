import boto3, os
from botocore.exceptions import ClientError

def send_mail(recipient, subject, message):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "VFL Notification service <dataslid@gmail.com>"

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = recipient

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = subject #"Bet9ja Virtual League Notification"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = message 
    # ("Automated message from Amazon SES (Python)\r\n"
    #             "This email was sent with Amazon SES using the "
    #             "AWS SDK for Python (Boto)."
    #             )


    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
    <h1>{subject}</h1>
    <p>{message}</p>
    <a href="dataslid.pythonanywhere.com">Courtey of Dataslid tech </a>
    </body>
    </html>
                """            

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    email_key = os.environ.get("aws_key")
    email_secret = os.environ.get("aws_secret")
    
    # print(recipient, RECIPIENT, email_secret, email_key, AWS_REGION)
    client = boto3.client('ses', region_name=AWS_REGION, aws_access_key_id=email_key, aws_secret_access_key=email_secret)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        pass
        # print(e.response['Error']['Message'])
    else:
        print("Email sent!"),