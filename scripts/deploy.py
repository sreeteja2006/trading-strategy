import os
import argparse
import boto3
from botocore.exceptions import ClientError

def deploy_to_aws(region="us-east-1"):
    """Deploy the application to AWS ECS"""
    try:
        # Initialize AWS clients
        ecr = boto3.client('ecr', region_name=region)
        ecs = boto3.client('ecs', region_name=region)
        
        # Create ECR repository if it doesn't exist
        try:
            ecr.create_repository(repositoryName='trading-strategy')
        except ClientError as e:
            if e.response['Error']['Code'] != 'RepositoryAlreadyExistsException':
                raise
        
        # Build and push Docker image
        os.system(f"""
            aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.{region}.amazonaws.com
            docker build -t trading-strategy .
            docker tag trading-strategy:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.{region}.amazonaws.com/trading-strategy:latest
            docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.{region}.amazonaws.com/trading-strategy:latest
        """)
        
        # Update ECS service
        ecs.update_service(
            cluster='trading-cluster',
            service='trading-service',
            forceNewDeployment=True
        )
        
        print("Deployment successful!")
        
    except Exception as e:
        print(f"Deployment failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    args = parser.parse_args()
    deploy_to_aws(args.region)