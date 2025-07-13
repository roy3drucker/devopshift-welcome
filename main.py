import logging
from scripts.user_input import get_user_input
from scripts.render_template import render_template
from scripts.terraform_runner import run_terraform


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    """Main entry point of the application."""
    setup_logging()
    
    try:
        # Get and validate user input
        config = get_user_input()
        logging.info("Configuration collected successfully:")
        logging.info(f"AMI: {config.ami}")
        logging.info(f"Instance Type: {config.instance_type}")
        logging.info(f"Region: {config.region}")
        logging.info(f"Availability Zone: {config.availability_zone}")
        logging.info(f"Load Balancer Name: {config.lb_name}")
        
        # Generate Terraform configuration
        render_template(config)
        logging.info("Terraform configuration generated successfully")
        
        # Run Terraform
        output = run_terraform()
        logging.info("Terraform Output:")
        logging.info(output)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise



if __name__ == "__main__":
    main()

