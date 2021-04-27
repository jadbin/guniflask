class RequestValidationError(AssertionError):
    @property
    def error(self):
        return self.args[0]
