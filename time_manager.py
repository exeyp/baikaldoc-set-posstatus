import os
import json
import logging
from datetime import datetime, timedelta, timezone

class TimeManager:
    def __init__(self, state_path, utc_offset_hours):
        self.state_path = state_path
        self.local_tz = timezone(timedelta(hours=utc_offset_hours))
    
    def read_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            return state.get('lastRunTime')
        return None

    def write_state(self, last_run_time):
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump({"lastRunTime": last_run_time}, f, ensure_ascii=False, indent=4)

    def get_start_time(self, max_date_range_days, fixed_start_time=None):
        try:
            if fixed_start_time:
                start_time = datetime.strptime(fixed_start_time, '%Y-%m-%d %H:%M:%S').astimezone(self.local_tz).isoformat()
            else:
                saved_start_time = self.read_state()
                if saved_start_time:
                    start_time = (datetime.fromisoformat(saved_start_time) - timedelta(minutes=5)).astimezone(self.local_tz).isoformat()
                else:
                    start_time = (datetime.now(self.local_tz) - timedelta(days=max_date_range_days)).isoformat()
        except ValueError as e:
            logging.error(f"Ошибка при преобразовании времени начала периода: {e}")
            raise SystemExit()
        return start_time

    def get_end_time(self, fixed_end_time=None):
        try:
            if fixed_end_time:
                end_time = datetime.strptime(fixed_end_time, '%Y-%m-%d %H:%M:%S').astimezone(self.local_tz).isoformat()
            else:
                end_time = datetime.now(self.local_tz).isoformat()
        except ValueError as e:
            logging.error(f"Ошибка при преобразовании времени окончания периода: {e}")
            raise SystemExit()
        return end_time

    def adjust_date_range(self, start_time, end_time, max_date_range_days):
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        if (end_dt - start_dt).days > max_date_range_days:
            new_start_time = (end_dt - timedelta(days=max_date_range_days)).astimezone(self.local_tz).isoformat()
            logging.info(f"Диапазон дат превышает {max_date_range_days} дней. Использован диапазон: {new_start_time} - {end_time}")
            return new_start_time, end_time
        return start_time, end_time
