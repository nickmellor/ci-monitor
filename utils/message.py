# OS-agnostic message-handling utilities


def summarise_text(text, summary_size=20):
    # return first 10 and last 10 lines of a text with ellipsis for longer files
    message_lines = text.splitlines()
    # if it's a short text show all of it
    if len(message_lines) < summary_size:
        message = message_lines
    else:
        # print head and tail of the text with ellipsis for the middle section
        message = message_lines[:summary_size // 2 - 1] + ['   [...]'] + message_lines[-summary_size // 2:]
    summary_text = os.linesep.join(message)
    # if last line of text was not blank add a newline to avoid line collisions with later messages
    return summary_text + os.linesep if message[-1] else summary_text
