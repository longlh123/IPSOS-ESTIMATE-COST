def proper(text: str) -> str:
    if not text:
        return ""
    return text[0].upper() + text[1:]

def shortten_string(s, max_length=30):
    """Shorten string to max_length with ellipsis."""
    if len(s) > max_length:
        return s[:max_length - 3] + "..."
    return s