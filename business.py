import datetime
import os
import time

from dotenv import load_dotenv

load_dotenv()
payload = {
    'login': os.getenv('ZTU_LOGIN'),
    'password': os.getenv('ZTU_PASSWORD')
}


def is_numeric(value):
    try:
        float(value)
    except ValueError:
        return False
    return True