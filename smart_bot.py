def get_bot_response(message):

    message = message.lower()

    if "hello" in message or "hi" in message:
        return "Hello! I am your Finance Advisor."

    elif "save" in message:
        return "Try saving at least 20% of your income."

    elif "investment" in message:
        return "Consider Mutual Funds or SIP for long term."

    elif "expense" in message:
        return "Track daily expenses to control spending."

    else:
        return "Please ask finance related question."