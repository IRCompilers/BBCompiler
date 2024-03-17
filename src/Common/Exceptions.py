class InvalidTransitionException(Exception):
    def __init__(self, message):
        super().__init__(message)


class LexerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ParserError(Exception):
    def __init__(self, message):
        super().__init__(message)
