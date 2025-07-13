import os
import sys
import shutil
import logging
from python_terraform import Terraform
import subprocess


def check_terraform_installed():
    """Check if Terraform is installed and accessible."""
    if not shutil.which("terraform"):
        raise RuntimeError(
            "Terraform is not installed or not in PATH. "
            "Please install Terraform and try again."
        )


def run_terraform():
    """Run Terraform commands to deploy the infrastructure."""
    # Pre-flight checks
    check_terraform_installed()

    # Setup Terraform with proper working directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generated_dir = os.path.join(base_dir, "generated")

    def run_command(command, timeout=300):  # 5 minutes timeout
        """Run a command and return its output."""
        try:
            process = subprocess.Popen(
                command,
                cwd=generated_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Print output in real-time with a simple progress indicator
            logging.info(f"Running command: {' '.join(command)}")
            print("Progress: ", end="", flush=True)

            
            stdout_lines = []
            stderr_lines = []
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line:
                    stdout_lines.append(stdout_line)
                    if "Creating..." in stdout_line or "Modifying..." in stdout_line:
                        print("🔄", end="", flush=True)
                    elif "Creation complete" in stdout_line or "Modifications complete" in stdout_line:
                        print("✅", end="", flush=True)
                
                if stderr_line:
                    stderr_lines.append(stderr_line)
                    if "Error:" in stderr_line:
                        print("❌", end="", flush=True)

                
                if not stdout_line and not stderr_line and process.poll() is not None:
                    break

            logging.info("")  # New line after progress indicators
            
            process.wait(timeout=timeout)
            
            # Create a result object similar to subprocess.run
            result = type('Result', (), {
                'returncode': process.returncode,
                'stdout': ''.join(stdout_lines),
                'stderr': ''.join(stderr_lines)
            })

            if result.stdout:
                logging.info(f"Command output:\n{result.stdout}")
            if result.stderr:
                logging.error(f"Command error:\n{result.stderr}")
                
            return result

        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception(f"Command timed out after {timeout} seconds: {' '.join(command)}")
        except Exception as e:
            raise Exception(f"Command failed: {' '.join(command)}\nError: {str(e)}")

    logging.info(f"Working directory: {generated_dir}")
    
    try:
        # Initialize Terraform (quick operation)
        logging.info("\nInitializing Terraform...")
        init_result = run_command(["terraform", "init"], timeout=60)
        if init_result.returncode != 0:
            raise Exception("Terraform init failed")

        # Plan the changes (medium operation)
        logging.info("\nPlanning Terraform changes...")
        plan_result = run_command(["terraform", "plan", "-out=tfplan"], timeout=120)
        if plan_result.returncode != 0:
            raise Exception("Terraform plan failed")

        # Show the plan in detail
        if "No changes" not in plan_result.stdout:
            logging.info("\nShowing detailed plan...")
            show_result = run_command(["terraform", "show", "tfplan"], timeout=30)
            if show_result.returncode != 0:
                raise Exception("Failed to show plan")

        # Apply the changes (longest operation)
        logging.info("\nApplying Terraform changes...")
        logging.info("This might take a few minutes as resources are being created...")
        apply_result = run_command(["terraform", "apply", "-auto-approve"], timeout=600)  # 10 minutes
        if apply_result.returncode != 0:
            raise Exception("Terraform apply failed")

        logging.info("\n✨ Deployment completed successfully! ✨")
        
        # Get the outputs (quick operation)
        output_result = run_command(["terraform", "output", "-json"], timeout=30)
        return output_result.stdout if output_result.returncode == 0 else "{}"

    except Exception as e:
        logging.error(f"Terraform operation failed: {str(e)}")
        raise
