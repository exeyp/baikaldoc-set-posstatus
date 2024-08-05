import os
import json
from datetime import datetime, timedelta, timezone

class TimeManager:
    def __init__(self, state_path, utc_offset_hours):
        self.state_path = state_path
        self.local_tz = timezone(timedelta(hours=utc_offset_hours))

    def read_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('lastRunTime', '')
        return ''

    def write_state(self, last_run_time):
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump({"lastRunTime": last_run_time}, f, ensure_ascii=False, indent=4)

    def get_start_time(self):
        saved_start_time = self.read_state()
        if saved_start_time:
            start_time = (datetime.fromisoformat(saved_start_time) - timedelta(minutes=5)).astimezone(self.local_tz).isoformat()
        else:
            start_time = (datetime.now(self.local_tz) - timedelta(minutes=5)).isoformat()
        return start_time

    def get_end_time(self):
        return datetime.now(self.local_tz).isoformat()

    def is_date_range_valid(self, start_time, end_time, max_days=14):
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        return (end_dt - start_dt).days <= max_days
