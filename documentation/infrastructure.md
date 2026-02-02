# Infrastructure

## Overview
The infrastructure used within the DocDigest application.
Mainly used AWS tools and services.

## Services
### IAM
Using IAM policies to allow for services to perform specific tasks and interactions between other services.

#### ecsTaskExecutionRolePolicy
**Allows ECS tasks to interact with other AWS services**
- Pulling docker images from ECR
- Write logs to cloudwatch

**Policies**
- AmazonECSTaskExecutionRolePolicy

#### docdigest-app-task-role
**Allows ECS tasks to interact with other AWS services**
- Get and Put objects in S3 bucket
- Get, Put and Update items in DynamoDB

**Policies**
- docdigest-app-task-policy
