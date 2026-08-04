import json
from tool_registry import TOOL_REGISTRY


def format_preview(tool_name, args_dict):
    """Human-readable summary of what's about to happen."""
    if tool_name == "send_mail":
        return (f"Send email to {args_dict.get('to')}\n"
                f"Subject: {args_dict.get('subject')}\n"
                f"Body: {args_dict.get('body')}")
    # fallback for any other irreversible tool you add later
    return f"Call {tool_name} with args: {args_dict}"


def ask_approval(tool_name, args_dict):
    preview = format_preview(tool_name, args_dict)
    print("\n--- APPROVAL NEEDED ---")
    print(preview)
    answer = input("Proceed? [y/n]: ").strip().lower()
    return answer == "y"


def select_service(function_call_part):
    tool_name = function_call_part.name
    args_dict = json.loads(function_call_part.arguments)

    entry = TOOL_REGISTRY.get(tool_name)
    if entry is None:
        return f"Error: unknown tool '{tool_name}'"

    if entry["reversibility"] == "irreversible":
        if not ask_approval(tool_name, args_dict):
            return f"User rejected the action: {tool_name}({args_dict})"

    return entry["func"](**args_dict)

