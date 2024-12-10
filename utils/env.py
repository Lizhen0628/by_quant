import os
from pathlib import Path

DATA_DIR = Path.home() / '.quant'
DAILY_DIR = DATA_DIR / 'daily'
LOCAL_DAILY_FILE = DAILY_DIR / "k_daily_all.csv"
LOCAL_ADJUSTMENT_FILE = DAILY_DIR / "stock_adjustments.csv"
MINUTE_DIR = DATA_DIR / 'minute'

SECRET = os.getenv("BY_QUANT_KEY",default="your_secret_key_here")