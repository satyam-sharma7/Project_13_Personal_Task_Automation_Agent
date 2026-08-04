from Functions import gmail_tools

TOOL_REGISTRY = {
    "read_mail": {
        "func": gmail_tools.read_mail,
        "reversibility": "read",
    },
    "send_mail": {
        "func": gmail_tools.send_mail,
        "reversibility": "irreversible",
    },
    # "create_event": {"func": calendar_tools.create_event, "reversibility": "reversible"},
}
