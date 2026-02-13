"""
Custom Exception Hierarchy

Provides type-safe error handling with HTTP status code mapping.
All application exceptions should inherit from BaseApplicationException.
"""


class BaseApplicationException(Exception):
    """
    Base exception for all application-specific errors.
    
    Attributes:
        message: Human-readable error message
        status_code: HTTP status code for API responses
    """
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(BaseApplicationException):
    """
    Raised when input validation fails.
    
    Examples:
        - Invalid topic length
        - Invalid post type
        - Missing required fields
    """
    
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class AuthenticationError(BaseApplicationException):
    """
    Raised when authentication fails.
    
    Examples:
        - Missing access token
        - Expired access token
        - Invalid credentials
    """
    
    def __init__(self, message: str):
        super().__init__(message, status_code=401)


class AuthorizationError(BaseApplicationException):
    """
    Raised when user lacks required permissions.
    
    Examples:
        - Attempting to access another user's data
        - Missing required scopes
    """
    
    def __init__(self, message: str):
        super().__init__(message, status_code=403)


class ResourceNotFoundError(BaseApplicationException):
    """
    Raised when a requested resource doesn't exist.
    
    Examples:
        - User not found
        - Post not found
        - Credential not found
    """
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} not found: {resource_id}"
        super().__init__(message, status_code=404)


class ExternalServiceError(BaseApplicationException):
    """
    Raised when external service calls fail.
    
    Examples:
        - LinkedIn API errors
        - Gemini API errors
        - Network timeouts
    """
    
    def __init__(self, service: str, message: str):
        full_message = f"{service} error: {message}"
        super().__init__(full_message, status_code=502)


class WorkflowError(BaseApplicationException):
    """
    Raised when workflow execution fails.
    
    Examples:
        - Workflow state corruption
        - Max retries exceeded
        - Invalid workflow state
    """
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ConfigurationError(BaseApplicationException):
    """
    Raised when configuration is invalid or missing.
    
    Examples:
        - Missing required environment variables
        - Invalid configuration values
    """
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
