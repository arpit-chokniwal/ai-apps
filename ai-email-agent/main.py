import imaplib
from dotenv import load_dotenv
import os
from enum import Enum

class EmailStatus(Enum):
    SEEN = "SEEN"
    UNSEEN = "UNSEEN" 
    ALL = "ALL"


load_dotenv()


def get_inbox():
    try:
        user, password = os.getenv("user"), os.getenv("password")
        imap_url = 'imap.gmail.com'
        mail = imaplib.IMAP4_SSL(imap_url, 993)
        mail.login(user, password)
        mail.select('inbox')
        return mail
    except Exception as e:
        print(e)

def emails(status: EmailStatus, inbox):
    try:
        status, search_data = inbox.search(None, status.value)
        
        if status != 'OK':
            return {
                "error": "Failed to fetch emails",
                "status": status
            }

        return list(map(int, search_data[0].decode('ascii').split()))

    except Exception as e:
        print(e)


if __name__ == "__main__":
    inbox = get_inbox()
    all_emails = emails(EmailStatus.ALL, inbox)

