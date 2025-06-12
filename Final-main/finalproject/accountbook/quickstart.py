import base64
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import re
from .models import GmailTransaction
from datetime import datetime
from django.conf import settings


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MONEY_REGEX = r'(¥?\d{1,3}(?:,\d{3})*円?|¥\d+)'
TARGET_SENDER = 'statement@vpass.ne.jp'

def fetch_and_save_gmail_data():
    service = get_gmail_service()
    messages = get_emails_from_sender(service, TARGET_SENDER)

    for msg in messages:
        msg_id = msg['id']

        # すでに保存済みならスキップ（重複防止）
        if GmailTransaction.objects.filter(message_id=msg_id).exists():
            continue

        html_body = extract_email_body(service, msg_id)
        usage_data = extract_amounts_from_html(html_body)

        for usage_date_str, amount_str in usage_data:
            # 日時パース（例："2024/06/01 12:34" → datetime）
            try:
                usage_datetime = datetime.strptime(usage_date_str, "%Y/%m/%d %H:%M")
            except ValueError:
                continue  # パースできなければ無視

            # 金額変換（例："1,234円" → 1234）
            amount_clean = int(re.sub(r'[^\d]', '', amount_str))

            GmailTransaction.objects.create(
                usage_datetime=usage_datetime,
                amount=amount_clean,
                message_id=msg_id
            )

def extract_amounts_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    amounts = []
    for td in soup.find_all('td'):
        text = td.get_text(strip=True)
        if re.match(r'^[\d,]+円$', text):
            amounts.append(text)

    usage_dates = []
    for td in soup.find_all('td'):
        text = td.get_text(strip=True)
        if text.startswith('ご利用日時：'):
            date_match = re.search(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}', text)
            if date_match:
                usage_dates.append(date_match.group())

    # 金額と日時をペアにする（件数が一致する前提）
    usage_data = list(zip(usage_dates, amounts))
    return usage_data

def get_gmail_service():
    creds = None
    flow = InstalledAppFlow.from_client_secrets_file(settings.CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=8080)
    return build('gmail', 'v1', credentials=creds)

def get_emails_from_sender(service, sender_email, max_results=10):
    query = f'from:{TARGET_SENDER}'
    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])
    return messages

def extract_email_body(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message['payload']

    def get_body(parts):
        for part in parts:
            if part['mimeType'] == 'text/html':
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8')
            elif part['mimeType'].startswith('multipart/'):
                return get_body(part.get('parts', []))
        return ""

    return get_body(payload.get('parts', []))

def extract_amounts(text):
    return re.findall(MONEY_REGEX, text)

def main():
    service = get_gmail_service()
    messages = get_emails_from_sender(service, TARGET_SENDER)

    for msg in messages:
        msg_id = msg['id']
        html_body = extract_email_body(service, msg_id)
        amounts = extract_amounts_from_html(html_body)
        print(f"Email ID: {msg_id}")
        print("Extracted Amounts:", amounts)

if __name__=='__main__':
    main()

