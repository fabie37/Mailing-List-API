"""
    This file contains API exceptions that maybe raised through calling certain functions.
"""
def generate_error_response(message, http_code):
    """
        Creates the format suitable for flask to process errors
    """
    return {"success": False, "error":message}, http_code

def flask_parameter_validation_error_handler(error):
    """
        Using this library, we can change the default validation paramter.
    """
    return {
        "error": str(error),
        "status": False
    }

class APIAuthError(Exception):
    """
        Exception raised for failed API checks.

        Attributes:
            message -- explains error
            http_code -- http return code
    """
    def __init__(self, message="API Auth Error", http_code=400):
        self.message = message
        self.http_code = http_code
        super().__init__(self.message)


