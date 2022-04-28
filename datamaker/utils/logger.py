from decimal import Decimal


class Logger:
    progress_records = {}

    def __init__(self, client=None, task=None):
        self.client = client
        self.task = task

    def set_progress(self, current, total, category=''):
        percent = 0
        if total > 0:
            percent = (Decimal(current) / Decimal(total)) * Decimal(100)
            percent = float(round(percent, 2))

        self.progress_records[category] = {
            'current': current,
            'total': total,
            'percent': percent
        }
        if self.task:
            self.task.update_state(
                state='PROGRESS',
                meta=self.progress_records
            )

    def log(self, action, data):
        if self.client and self.task:
            self.client.log(self.task.request.id, action, data)
