from Functions import gmail_tools
import json



def select_service(function_call_part):
    service = function_call_part.name
    args_dict = json.loads(function_call_part.arguments)

    if service.endswith("mail"):
        if service == "read_mail":
            gmail_tools.read_mail(**args_dict)
        if service == "send_mail":
            gmail_tools.send_mail(**args_dict)







# select_service(service="read_mail")
