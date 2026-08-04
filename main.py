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
MAX_LOOP = config["MAX_LOOP"]

client = OpenAI(
    base_url=LLM_MODEL['url'],
    api_key=os.getenv(LLM_MODEL['api'])
)

SYSTEM_PROMPT = """"
You are an helpful assistant. You have access to tools you can complete the task using the appopriate tools.
choose right tools to complete the work. 
Tell user about task completion if completed the task or summarize the end result.
"""


messages = [{"role":"system", "content":SYSTEM_PROMPT}, {"role":"user", "content":str(input("Prompt: "))}]
# send birthday invite message to satyamn8n@gmail.com from raghav birthday venue is raghav's house at 8 pm


while MAX_LOOP >= 0:
    print(MAX_LOOP)
    if MAX_LOOP == 0:
        messages[0]["content"] += "Last attempt exhausted tell user why task couldn't be completed."
    response = client.chat.completions.create(
        model=LLM_MODEL['name'],
        messages= messages,
        tools=[read_mail_schema, send_mail_schema],
        tool_choice='auto'
    )
    assistant_message = response.choices[0].message
    messages.append(assistant_message.model_dump(exclude_unset=True))

    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            tool_result = select_service(tool_call.function)
            messages.append({
                "role":"tool",
                "tool_call_id":tool_call.id,
                "content": str(tool_result)
            })
        
    if response.choices[0].finish_reason == "stop":
        break


    MAX_LOOP -= 1

            

print(messages)
