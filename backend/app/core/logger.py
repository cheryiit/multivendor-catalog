import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name):
    log_dir = '/app/logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'app_{today}.log')
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # RotatingFileHandler kullanarak log dosyasının boyutunu sınırlayalım
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def log_step(logger, step, message):
    logger.info(f"STEP {step}: {message}")

def archive_old_logs(log_dir, days_to_keep=30):
    import shutil
    from datetime import timedelta

    today = datetime.now()
    for filename in os.listdir(log_dir):
        if filename.startswith('app_') and filename.endswith('.log'):
            file_date_str = filename[4:14]  # Extract date from filename
            file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
            if (today - file_date).days > days_to_keep:
                src = os.path.join(log_dir, filename)
                dst = os.path.join(log_dir, 'archive', filename)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(src, dst)

# Her gün bir kez çalıştırılacak bir fonksiyon
def daily_log_maintenance():
    log_dir = '/app/logs'
    archive_old_logs(log_dir)