import boto3
import json
import logging
import os
from botocore.exceptions import ClientError

def get_terraform_outputs(generated_dir):
    import subprocess
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=generated_dir,
            check=True,
            capture_output=True,
            text=True
        )
        outputs = json.loads(result.stdout)
        return {k: v['value'] for k, v in outputs.items()}
    except Exception as e:
        logging.error(f"Failed to get terraform outputs: {e}")
        return {}

def validate_aws_resources(instance_id, lb_dns_name, region="us-east-2"):
    ec2 = boto3.client("ec2", region_name=region)
    elbv2 = boto3.client("elbv2", region_name=region)
    result = {
        "instance_id": None,
        "instance_state": None,
        "public_ip": None,
        "load_balancer_dns": None
    }

    try:
        resp = ec2.describe_instances(InstanceIds=[instance_id])
        reservations = resp.get("Reservations", [])
        if reservations and reservations[0]["Instances"]:
            instance = reservations[0]["Instances"][0]
            result["instance_id"] = instance.get("InstanceId")
            result["instance_state"] = instance.get("State", {}).get("Name")
            result["public_ip"] = instance.get("PublicIpAddress")
            logging.info(f"EC2 instance {instance_id} state: {result['instance_state']}")
        else:
            logging.error(f"Instance {instance_id} not found.")
    except ClientError as e:
        logging.error(f"Error fetching EC2 instance: {e}")

    try:
        lbs = elbv2.describe_load_balancers()["LoadBalancers"]
        lb_found = next((lb for lb in lbs if lb["DNSName"] == lb_dns_name), None)
        if lb_found:
            result["load_balancer_dns"] = lb_found["DNSName"]
            logging.info(f"Load balancer found: {lb_found['DNSName']}")
        else:
            logging.error(f"Load balancer {lb_dns_name} not found.")
    except ClientError as e:
        logging.error(f"Error fetching load balancer: {e}")

    return result

def save_validation_json(data, path="aws_validation.json"):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Validation results saved to {path}")
    except Exception as e:
        logging.error(f"Failed to save validation json: {e}")

def main():
    logging.basicConfig(level=logging.INFO)
    try:
        generated_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated")
        outputs = get_terraform_outputs(generated_dir)
        logging.info(f"Terraform Outputs: {outputs}")

        instance_id = outputs.get("instance_id")
        lb_dns_name = outputs.get("load_balancer_dns")

        if not instance_id or not lb_dns_name:
            logging.error("Missing instance_id or load_balancer_dns in terraform outputs.")
            return

        validation_results = validate_aws_resources(instance_id, lb_dns_name)
        save_validation_json(validation_results)
    except Exception as e:
        logging.error(f"Validation failed: {e}")

if __name__ == "__main__":
    main()
