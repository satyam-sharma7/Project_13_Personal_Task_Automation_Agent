from openai import OpenAI
from dotenv import load_dotenv
import os
import tomllib 

from function_call import select_service
from Functions.gmail_tools import read_mail_schema, send_mail_schema


load_dotenv()

with open("config.toml", 'rb') as f:
    config = tomllib.load(f)

LLM_MODEL = config['models'][config['LLM_MODEL']]

client = OpenAI(
    base_url=LLM_MODEL['url'],
    api_key=os.getenv(LLM_MODEL['api'])
)

SYSTEM_PROMPT = """"
You are an helpful assistant. You have access to tools you can complete the task using the appopriate tools.
choose right tools to complete the work. 
"""

response = client.chat.completions.create(
    model=LLM_MODEL['name'],
    messages=[
        {"role":"system", "content":SYSTEM_PROMPT},
        {"role":"user", "content":"read 7 recent messages"}
    ],
    tools=[read_mail_schema, send_mail_schema],
    tool_choice='auto'
)

if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        select_service(tool_call.function)

        print(tool_call.function.name)
        print(tool_call.function.arguments)

