import imaplib, os, datetime, email
from dotenv import load_dotenv
from enum import Enum
from utils import findAllEmailsInString

class EmailStatus(Enum):
    SEEN = "SEEN"
    UNSEEN = "UNSEEN" 
    ALL = "ALL"


load_dotenv()


def get_inbox():
    try:
        user, password, imap_url = os.getenv("user"), os.getenv("password"), os.getenv("imap_url")
        mail = imaplib.IMAP4_SSL(imap_url, 993)
        mail.login(user, password)
        # here we are selecting inbox, if you have some lable and all add that insted of inbox 
        mail.select('inbox')
        return mail
    except Exception as e:
        print(e)

def emails(status: EmailStatus, filter: str, inbox):
    try:
        status, search_data = inbox.search(None, status.value, filter)
        if status != 'OK':
            return {
                "error": "Failed to fetch emails",
                "status": status
            }
        return list(map(int, search_data[0].decode('ascii').split()))
    except Exception as e:
        print(e)


def get_email_details(email_id, inbox):
    try:
        data = inbox.fetch(str(email_id).encode('ascii'), '(RFC822)')[1]
        email_message = email.message_from_bytes(data[0][1])
        time_row = email.utils.parsedate_to_datetime(email_message['date']).isoformat()
    except Exception as e:
        print(f'Invalid position {email_id}: {e}')
        return f"Position {email_id} not valid"

    email_data = {
        'date': time_row,
        'to': [],
        'cc': [],
        'from': None,
        'subject': email_message['subject'],
        'body': None,
        'attachments': []
    }

    for header in ['to', 'cc', 'from']:
        header_value = email_message[header]
        if not header_value:
            continue
            
        emails = findAllEmailsInString(header_value)
        if header == 'from':
            email_data[header] = emails[0] if emails else None
        else:
            email_data[header] = emails

    for part in email_message.walk():
        content_type = part.get_content_type()
        try:
            if content_type == "text/plain":
                email_data['body'] = part.get_payload(decode=True).decode().replace("\n", " ").replace("\r", "")
            
            if (part.get_content_maintype() != 'multipart' and 
                  part.get('Content-Disposition') and 
                  part.get_filename() and 
                  part.get_filename().lower().endswith(('.pdf', '.txt', '.docx'))):
                file_data = part.get_payload(decode=True)
                email_data['attachments'].append({
                    'filename': part.get_filename(),
                    'content_type': content_type,
                    'data': file_data
                })
        except Exception as e:
            print(f"Error processing {content_type} at position {email_id}: {e}")

    return email_data

if __name__ == "__main__":
    inbox = get_inbox()
    date = datetime.date.today().strftime("%d-%b-%Y")
    daily_emails = emails(EmailStatus.ALL, f'(SENTSINCE {date})', inbox)
    data = []
    for email_id in daily_emails:
        email_details = get_email_details(email_id, inbox)
        data.append(email_details)
    print(data[3])

        

