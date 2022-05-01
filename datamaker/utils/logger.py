from decimal import Decimal

from django.utils import timezone

from datamaker.exceptions import ClientError


class Logger:
    progress_records = {}
    logs_queue = []

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
            self.logs_queue.append({
                'task_id': self.task.request.id,
                'action': action,
                'data': data,
                'datetime': timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S.%f')
            })
            try:
                self.client.log(self.logs_queue)
                self.logs_queue.clear()
            except ClientError:
                pass
