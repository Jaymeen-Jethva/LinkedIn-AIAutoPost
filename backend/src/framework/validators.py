"""
Centralized Input Validation

Extracts validation logic from controllers following DRY principle.
All validation methods should raise ValidationError on failure.
"""
from typing import List
from src.framework.exceptions import ValidationError


class PostValidator:
    """Validator for post-related inputs"""
    
    # Validation constants
    MIN_TOPIC_LENGTH = 5
    MAX_TOPIC_LENGTH = 500
    ALLOWED_POST_TYPES = [
        "AI News",
        "Career Advice",
        "Product Launch",
        "Thought Leadership",
        "Personal Branding",
        "AI Tutorials",
        "ML Research Summary"
    ]
    
    @staticmethod
    def validate_topic(topic: str) -> str:
        """
        Validate post topic length and content.
        
        Args:
            topic: The post topic string
            
        Returns:
            Cleaned topic string
            
        Raises:
            ValidationError: If topic fails validation
        """
        if not topic or not topic.strip():
            raise ValidationError("Topic cannot be empty")
        
        topic = topic.strip()
        
        if len(topic) < PostValidator.MIN_TOPIC_LENGTH:
            raise ValidationError(
                f"Topic must be at least {PostValidator.MIN_TOPIC_LENGTH} characters"
            )
        
        if len(topic) > PostValidator.MAX_TOPIC_LENGTH:
            raise ValidationError(
                f"Topic must not exceed {PostValidator.MAX_TOPIC_LENGTH} characters"
            )
        
        return topic
    
    @staticmethod
    def validate_post_type(post_type: str) -> str:
        """
        Validate post type against allowed values.
        
        Args:
            post_type: The post type string
            
        Returns:
            Validated post type
            
        Raises:
            ValidationError: If post type is not allowed
        """
        if not post_type or not post_type.strip():
            raise ValidationError("Post type cannot be empty")
        
        post_type = post_type.strip()
        
        if post_type not in PostValidator.ALLOWED_POST_TYPES:
            allowed_list = "', '".join(PostValidator.ALLOWED_POST_TYPES)
            raise ValidationError(
                f"Invalid post type. Allowed types: '{allowed_list}'"
            )
        
        return post_type
    
    @staticmethod
    def validate_user_id(user_id: str | None) -> None:
        """
        Validate user ID presence.
        
        Args:
            user_id: The user ID string
            
        Raises:
            ValidationError: If user ID is missing
        """
        if not user_id or not user_id.strip():
            raise ValidationError("User ID is required")
    
    @staticmethod
    def get_allowed_post_types() -> List[str]:
        """
        Get list of allowed post types.
        
        Returns:
            List of allowed post type strings
        """
        return PostValidator.ALLOWED_POST_TYPES.copy()


class OAuthValidator:
    """Validator for OAuth-related inputs"""
    
    @staticmethod
    def validate_callback_code(code: str | None) -> str:
        """
        Validate OAuth callback authorization code.
        
        Args:
            code: The authorization code from OAuth callback
            
        Returns:
            Validated authorization code
            
        Raises:
            ValidationError: If code is missing or invalid
        """
        if not code or not code.strip():
            raise ValidationError("Authorization code is required")
        
        return code.strip()
    
    @staticmethod
    def validate_state(state: str | None, expected_pattern: str | None = None) -> str:
        """
        Validate OAuth state parameter.
        
        Args:
            state: The state parameter from OAuth callback
            expected_pattern: Optional expected state value for CSRF protection
            
        Returns:
            Validated state
            
        Raises:
            ValidationError: If state is missing or doesn't match expected
        """
        if not state or not state.strip():
            raise ValidationError("State parameter is required")
        
        state = state.strip()
        
        # If expected pattern provided, validate against it
        if expected_pattern and state != expected_pattern:
            raise ValidationError("Invalid state parameter (CSRF protection)")
        
        return state
