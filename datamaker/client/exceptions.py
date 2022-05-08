class ClientError(Exception):
    status = None
    reason = None

    def __init__(self, status, reason, *args):
        self.status = status
        self.reason = reason
        super().__init__(status, reason, *args)

    def as_validation_error(self):
        if self.status == 400:
            error = self.reason
        else:
            error = str(self)

        return {'backend_errors': error}
