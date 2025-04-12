import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001")


class EmailTagEnum(Enum):
    WORK = "WORK"
    PERSONAL = "PERSONAL"
    PROMOTION = "PROMOTION"
    INVOICE = "INVOICE"
    NEWSLETTER = "NEWSLETTER"
    OTHER = "OTHER"


class EmailTag(BaseModel):
    '''You are a helpful assistant that categorizes emails into tags.'''
    tag: EmailTagEnum = Field(description="The tag of the email, based on the content of the email")


def call_llm (text: str, image_urls=None):
    # Update the system prompt according to your needs
    messages = [
        (
            "system",
            f"You are a helpful assistant that categorizes emails into tags. You are given a subject and body of an email. You need to categorize the email into one of the following tags: {', '.join([tag.value for tag in EmailTagEnum])}",
        )
    ]
    content = [{"type": "text", "text": text}]
    if image_urls:
        content.extend(image_urls)
    
    messages.append(HumanMessage(content=content))
    structured_output = llm.with_structured_output(EmailTag).invoke(messages)
    return structured_output.tag.value
