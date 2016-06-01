

class EarlyExit(Exception):

    def __init__(self, message='', exit_code=0):
        super(EarlyExit, self).__init__(message)
        self.exit_code = exit_code
