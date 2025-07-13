from .aws_config import AWSConfig


def get_user_input() -> AWSConfig:
    """
    Get and validate user input for AWS configuration.
    
    Returns:
        AWSConfig: Validated configuration object
    """
    print("=== AWS EC2 Deployment Configurator ===")
    return AWSConfig.from_user_input()