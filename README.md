# Auto Draft - Email Automation System with Mendable AI

## Description
This project provides an automated email handling system using the Gmail API and [Mendable.ai](https://mendable.ai). It is able to categorize emails and automatically draft replies to it. It also create alerts using various APIs and tools, ensuring that your inbox is smartly managed.

## How it works?
Currently the system is able to read your inbox and determined which emails are of a customer support nature. It then uses Mendable AI to draft a reply to the email. If the reply is satisfactory, it will be saved as a draft in your Gmail account.

The system also uses Slack to send alerts to the user for manual review or intervention as needed.

# Current Features
- [x] Authenticate and Interact with Gmail API
- [x] AI Classification (Customer Support)
- [x] Draft Replies
- [x] Slack Alerts
- [ ] Add webhook to listen to incoming emails
## Prerequisites

Google Cloud Platform (GCP) Project: Create a project and enable the Gmail API.
OAuth 2.0: Set up OAuth 2.0 as a Desktop app and download the client configuration to get your credentials (a `credentials.json`` file). This will allow the script to authenticate with the Gmail API.


Also ensure you have the following installed:
- Python 3.8 or later
- PIP


## Installation & Setup
1. **Clone the Repository**
    ```bash
    git clone [Your Repo Link]
    cd [Your Repo Name]
    ```
2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3. **Environment Variables**
   Create a `.env` file in the root directory and define the following variables:
    ```env
    MENDABLE_SERVER_API_KEY=your_key_here
    OPENAI_API_KEY=your_key_here
    SLACK_WEBHOOK_URL=your_webhook_url_here
    ```
   Replace the placeholder values with your actual API keys and URL.

## Usage
Ensure all prerequisite steps are completed before running the script:

```bash
python app.py
``` 


## How it Works

Authenticate and Interact with Gmail API: Retrieves and manages emails.
AI Analysis: Evaluates email content to generate auto-responses and categorize email types.
Draft Replies: Formulates reply drafts for emails and saves them in Gmail.
Alerts: Sends alerts to Slack for manual review or intervention as needed.

## Note
Ensure you have enabled Gmail API and have the credentials.json file for authenticating.
If modifying scopes in the code, make sure to delete the token.json to re-authenticate and validate the new scopes.
Ensure that all sensitive data, such as API keys and secrets, are kept secure and not exposed in the code or public repositories.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.