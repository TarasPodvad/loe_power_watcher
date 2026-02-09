from config import STATE_FILE

def load_state():
    if STATE_FILE.exists():
        return STATE_FILE.read_text().strip()
    return None

def save_state(value):
    STATE_FILE.write_text(value)
