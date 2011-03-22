class APIException(Exception):
    """Base exception class for these API bindings."""
    pass

class APIWarning(UserWarning):
    """Base exception class for these API bindings."""
    pass

class BadCaptcha(APIException):
    """An exception for when an incorrect captcha error is returned."""
    def __str__(self):
        return "Incorrect captcha entered."

class NotLoggedInException(APIException):
    """An exception for when a Reddit user isn't logged in."""
    def __str__(self):
        return "You need to login to do that!"

class InvalidUserPass(APIException):
    """An exception for failed logins."""
    def __str__(self):
        return "Invalid username/password."
