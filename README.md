# AWS CI/CD Platform — GitHub Actions & ECS Fargate

An end-to-end, production-style AWS deployment project demonstrating containerization, Infrastructure as Code, automated CI/CD, image security scanning, and secure application-to-database connectivity. The application is packaged with Docker, stored in Amazon ECR, and deployed to Amazon ECS on Fargate through GitHub Actions. Terraform provisions the AWS infrastructure.


## Architecture

![AWS architecture diagram](docs/architecture.png)


### Request and data flow

1. Users access the application through the internet-facing Application Load Balancer (ALB) on HTTP port `80`.
2. The ALB forwards requests to the ECS Fargate service on container port `8000`.
3. Fargate tasks run in private subnets without public IP addresses. The service security group accepts application traffic only from the ALB security group.
4. The application connects to private Amazon RDS for PostgreSQL on port `5432`. The database security group accepts traffic only from the ECS security group.
5. ECS retrieves database settings from AWS Secrets Manager. The task execution role is scoped to the required secret.
6. ECS pulls the container image from Amazon ECR and sends application logs to CloudWatch Logs.

> RDS is private and is not directly reachable from the public internet. The current database configuration is single-AZ (`db.t4g.micro`, 20 GB).

## CI/CD pipeline

```mermaid
flowchart TD
    A[Developer pushes code or opens PR] --> B[GitHub Actions]
    B --> C[Python compile check]
    C --> D[Build Docker image]
    D --> E[Trivy image scan]
    E --> F{Event and scan result}
    F -->|PR| G[CI result — no AWS deployment]
    F -->|Push to main, scan passes| H[Authenticate to AWS with GitHub OIDC]
    H --> I[Login to Amazon ECR]
    I --> J[Push image tagged with Git SHA]
    J --> K[Read current ECS task definition]
    K --> L[Update image and register new revision]
    L --> M[Deploy to ECS Fargate]
    M --> N[Wait for ECS service stability]
    E -->|HIGH/CRITICAL finding| X[Fail workflow]
    N -->|Deployment does not stabilize| Y[Fail workflow]
```





## Security considerations

- Keep ECS tasks and RDS in private subnets.
- Restrict ALB-to-ECS and ECS-to-RDS traffic using security-group references.
- Use GitHub OIDC rather than storing long-lived AWS access keys in GitHub.
- Scope IAM permissions to the required ECR, ECS, logging, and secret resources.
- Store database credentials in Secrets Manager; never hard-code them in source code or the Docker image.
- Scan container images with Trivy before deployment.
- Keep `.tfstate`, `.tfvars` containing secrets, `.env` files, and credentials out of Git.





