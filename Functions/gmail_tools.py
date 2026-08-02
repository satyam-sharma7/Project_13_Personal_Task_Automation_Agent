from email.message import EmailMessage
import base64

from Functions.google_auth import gmail_service


def read_mail(n=5):
    results = (
        gmail_service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
    )
    messages = results.get("messages", [])
    for message in messages:
        if n>0:
            print(f'Message ID: {message["id"]}')
            msg = (
                gmail_service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            print(f'  Subject: {msg["snippet"]}')
            n -=1


def send_mail(to, subject, body):
    message = EmailMessage()
    message.set_content(body)
    message['to'] = to
    message['subject'] = subject
    
    # Gmail API requires base64 encoding
    encoded_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    gmail_service.users().messages().send(userId="me", body=encoded_message).execute()
    print(f"Message Sent to: {to}")


def search_mail():
    pass




read_mail_schema = {
    "type": "function",
    "function":{
        "name": "read_mail",
        "description": "Read the most recent n messages from the inbox.",
        "parameters": {
            "type": "object",
            "properties": {
                "n": {
                    "type": "integer",
                    "description": "The number of recent messages to retrieve. Defaults to 5 if omitted.",
                }
            }
        }
    }
}


send_mail_schema = {
    "type": "function",
    "function":{
        "name": "send_mail",
        "description": "Send a mail",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "The mail address of recipient whom message is to be sent.",
                },
                "subject": {
                    "type": "string",
                    "description": "The topic of the Mail. Should be intresting so recipient's don't ignore the mail.",
                },
                "body": {
                    "type": "string",
                    "description": "The message that you want to send.",
                }
            },
            "required": ["sign"],
        }
    }
}
