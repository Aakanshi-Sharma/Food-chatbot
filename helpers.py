import re


def extract_session_id(session_id: str):
    pattern = r'/sessions/(.*?)/contexts/'
    match = re.search(pattern, session_id)
    if match:
        extracted_session_id = match.group(1)
        return extracted_session_id
    else:
        return ""
