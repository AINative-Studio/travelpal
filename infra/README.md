# Infrastructure as Code

This directory contains Terraform configurations for deploying TravelPal's infrastructure.

## Structure

```
infra/
└── terraform/
    ├── k8s/      # Kubernetes cluster and application deployments
    ├── db/        # Database configurations (PostgreSQL)
    └── storage/  # Persistent storage configurations
```

## Prerequisites

- Terraform 1.5+
- AWS/GCP/Azure CLI configured with appropriate permissions
- kubectl (for Kubernetes deployments)

## Usage

1. Navigate to the desired environment directory:
   ```bash
   cd infra/terraform/<environment>
   ```

2. Initialize Terraform:
   ```bash
   terraform init
   ```

3. Review the execution plan:
   ```bash
   terraform plan
   ```

4. Apply the configuration:
   ```bash
   terraform apply
   ```

## Environments

- **staging**: Non-production environment for testing
- **production**: Production environment

## Backend State

Remote state is stored in an S3 bucket (or equivalent for your cloud provider) with state locking using DynamoDB.
