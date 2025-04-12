import imaplib, os, datetime, email, base64
from dotenv import load_dotenv
from enum import Enum
from utils import findAllEmailsInString
from email.header import decode_header
from llm import call_llm

load_dotenv()


class EmailStatus(Enum):
    SEEN = "SEEN"
    UNSEEN = "UNSEEN" 
    ALL = "ALL"


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

def get_emails(status: EmailStatus, filter: str, inbox):
    try:
        status, search_data = inbox.search(None, status.value, filter)
        if status != 'OK':
            return {
                "error": "Failed to fetch emails",
                "status": status
            }
        return list(map(int, search_data[0].decode('ascii').split())) if search_data else []
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

    subject = email_message['subject']
    if subject:
        decoded_header = decode_header(subject)
        decoded_parts = []
        for content, encoding in decoded_header:
            if isinstance(content, bytes):
                decoded_parts.append(content.decode(encoding or 'utf-8', errors='replace'))
            else:
                decoded_parts.append(content)
        subject = ''.join(decoded_parts)

    email_data = {
        'date': time_row,
        'to': [],
        'cc': [],
        'from': None,
        'subject': subject,
        'body': None,
        'html_body': None,
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
            
            if content_type == "text/html":
                email_data['html_body'] = part.get_payload(decode=True).decode().replace("\n", " ").replace("\r", "")
            
            if (part.get_content_maintype() != 'multipart' and 
                  part.get('Content-Disposition') and 'image' in content_type):
                # you can store this file to s3 and map it to email_id
                file_data = part.get_payload(decode=True)
                email_data['attachments'].append({
                    'filename': part.get_filename(),
                    'content_type': content_type,
                    'base64': base64.b64encode(file_data).decode('utf-8')
                })
        except Exception as e:
            print(f"Error processing {content_type} at position {email_id}: {e}")
    return email_data



def main():
    try:
        inbox = get_inbox()
        date = datetime.date.today().strftime("%d-%b-%Y")
        daily_emails = get_emails(EmailStatus.ALL, f'(SENTSINCE {date})', inbox) or []
        data = []

        for email_id in daily_emails:
            email_details = get_email_details(email_id, inbox)
            # some times plain text is not available, so we use html body
            text = f"Subject: {email_details['subject']}\n\nBody:\n{email_details['body'] or email_details['html_body']}"
            tag = None
            if len(email_details['attachments']) > 0:
                attachment = email_details['attachments']
                image_urls = []
                for att in attachment:
                    image_urls.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{att['content_type']};base64,{att['base64']}"
                        }
                    })
                tag = call_llm(text, image_urls)
            else:
                tag = call_llm(text)
            email_details['tag'] = tag
            data.append(email_details)
            print(f"According to the email content, the tag is: {tag} for email id: {email_id}\n\n")

        # here is emails data with tags do what ever you want with it : )
        return data
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()