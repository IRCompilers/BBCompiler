class InvalidTransitionException(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnknownSymbolException(Exception):
    def __init__(self, message):
        super().__init__(message)
