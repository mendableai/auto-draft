import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from mendable import ChatApp

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# If modifying these SCOPES, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]


def service_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Call the Gmail API
    return build("gmail", "v1", credentials=creds)


def get_emails(service):
    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], maxResults=10)
        .execute()
    )
    messages = results.get("messages", [])

    emails = []
    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        payload = msg["payload"]
        headers = payload["headers"]

        email_data = {"id": message["id"]}  # Adding the message ID to email_data

        for header in headers:
            name = header["name"]
            if name in [
                "From",
                "Subject",
                "Message-ID",
            ]:  # Adding 'Message-ID' if you need it later
                email_data[name] = header["value"]

        # Get the body of the email
        parts = payload.get("parts", [])
        for part in parts:
            if part["mimeType"] == "text/plain":
                data = part["body"]["data"]
                email_data["Body"] = base64.urlsafe_b64decode(data).decode("UTF-8")
                break

        emails.append(email_data)

    return emails


def create_draft_reply(service, to, subject, body, original_email_id):
    """
    Create and save a draft reply.

    Args:
    service: Authorized Gmail API service instance.
    to: Email address of the receiver.
    subject: The subject of the email message.
    body: The text of the email message.
    original_email_id: The id of the email to reply to.

    Returns:
    Draft object, including draft id and message details.
    """
    # Get the original email
    original_email = (
        service.users()
        .messages()
        .get(userId="me", id=original_email_id, format="full")
        .execute()
    )

    # Extract the original email's Message-ID
    message_id = [
        header["value"]
        for header in original_email["payload"]["headers"]
        if header["name"] == "Message-ID"
    ][0]

    # Create the message as a reply
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    message["In-Reply-To"] = message_id
    message["References"] = message_id
    msg = MIMEText(body)
    message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {"message": {"raw": raw}}

    # Create the draft
    draft = service.users().drafts().create(userId="me", body=body).execute()

    print(f'Draft id: {draft["id"]}')
    print(draft)
    return draft


def respondQuestion(question):
    my_docs_bot = ChatApp(api_key=os.environ.get("MENDABLE_SERVER_API_KEY"))
    answer = my_docs_bot.query(question)
    return answer


def isSupportQuestionEmail(question, answer):

    # get key from environment variable
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    chat = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=openai_api_key)

    prompt = f"Question: {question}\nAnswer: {answer}\nClassify this question in Yes or No, if it is a quesiton that would be asked to support, maybe it could be a coding questions, a question about the product or a request.\n Start:"

    # get response from model
    response = chat([HumanMessage(content=prompt)])
    answer = response.content.lower()
    if "yes" in answer:
        return True
    return False


def isGoodEnoughToDraft(question, answer):

    # get key from environment variable
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    chat = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=openai_api_key)

    prompt = f"Question: {question}\nAnswer: {answer}\nClassify this question in Yes or No, if it was an accurate, resonable response to the user's query\n Start:"

    # get response from model
    response = chat([HumanMessage(content=prompt)])
    answer = response.content.lower()
    if "yes" in answer:
        return True
    return False


def alert_on_slack(text):
    import requests
    import json

    # URL from the curl request
    url = os.environ.get("SLACK_WEBHOOK_URL")

    # Headers from the curl request
    headers = {
        "Content-type": "application/json",
    }

    # Data from the curl request
    data = {"text": text}

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check the response
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.status_code}, {response.text}")


def start():
    gmail_service = service_gmail()
    emails = get_emails(gmail_service)

    # Example: Drafting a reply to the first retrieved email
    for email in emails:
        email_id = email["id"]
        email_from = email["From"]
        email_subject = email["Subject"]
        email_body = email.get("Body", None)

        if email_body is None:
            continue

        if not isSupportQuestionEmail(email_subject, email_body):
            continue

        reply = respondQuestion(email_body)
        if not isGoodEnoughToDraft(email_body, reply):
            continue

        intro = f"Hi there,\n\n"
        outro = f"\n\nBest,\nNick\nThis email was generated by Mendable AI."

        a = create_draft_reply(
            gmail_service,
            to=email_from,
            subject="Re: " + email_subject,
            body=intro + reply + outro,
            original_email_id=email_id,
        )
        alert_on_slack(
            f"Drafted a reply to {email_from} regarding their request. Check your email!"
        )


start()
