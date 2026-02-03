# Infrastructure

## Overview
The infrastructure used within the DocDigest application.
Mainly uses AWS serverless services for cost efficiency and automatic scaling.

## Services

### IAM
Using IAM policies to allow services to perform specific tasks and interactions between other services.

#### ecsTaskExecutionRole
**Allows ECS to pull images and write logs**
- Pulling Docker images from ECR
- Writing logs to CloudWatch

**Policies**
- AmazonECSTaskExecutionRolePolicy

#### docdigest-task-role
**Allows Flask app to interact with AWS services**
- Get and Put objects in S3 bucket
- Get, Put and Update items in DynamoDB

**Policies**
- docdigest-task-policy (inline policy)

#### docdigest-processor-role
**Allows Lambda processor to access AWS services**
- Get and Delete objects from S3
- Get and Update items in DynamoDB
- Publish messages to SNS topic
- Receive and Delete messages from SQS queue

**Policies**
- AWSLambdaBasicExecutionRole (CloudWatch logs)
- docdigest-processor-policy (inline policy)

#### docdigest-notifier-role
**Allows Lambda notifier to send emails**
- Get items from DynamoDB
- Send emails via SES

**Policies**
- AWSLambdaBasicExecutionRole (CloudWatch logs)
- docdigest-notifier-policy (inline policy)

---

### Elastic Container Registry (ECR)
**Private Docker image repository**

#### docdigest-flask
- Stores Flask webapp Docker images
- Tagged with git commit SHA and 'latest'
- Lifecycle policy: Keep last 10 images

#### docdigest-processor
- Stores Lambda processor Docker images
- Tagged with git commit SHA and 'latest'
- Lifecycle policy: Keep last 10 images

#### docdigest-notifier
- Stores Lambda notifier Docker images
- Tagged with git commit SHA and 'latest'
- Lifecycle policy: Keep last 10 images

---

### Elastic Container Service (ECS) Cluster
**Grouping of containers used in DocDigest**

#### docdigest-cluster
- Infrastructure: AWS Fargate (serverless)
- No server provisioning needed
- Containers run in this cluster

#### Security Groups

**docdigest-fargate-sg**
- Protects Fargate tasks
- Inbound: Port 8000 from ALB only
- Outbound: All traffic (to reach ECR, S3, DynamoDB)

**docdigest-alb-sg**
- Protects Application Load Balancer
- Inbound: Port 80 from anywhere (0.0.0.0/0)
- Outbound: All traffic

---

### Application Load Balancer (ALB)
**Distributes incoming web traffic to ECS containers**

#### docdigest-alb
- Type: Application Load Balancer
- Scheme: Internet-facing
- Provides public URL for Flask app
- Listener: HTTP on port 80
- Routes traffic to healthy Fargate tasks
- Health checks: GET / every 30 seconds
- Security group: docdigest-alb-sg

#### docdigest-flask-tg (Target Group)
- Target type: IP addresses (required for Fargate)
- Protocol: HTTP
- Port: 8000
- Health check path: /
- Health thresholds: 2 healthy, 3 unhealthy
- ECS automatically registers/deregisters tasks

---

### ECS Task Definition
**Blueprint for running Flask container**

#### docdigest-flask-task
- Family: docdigest-flask-task
- Launch type: Fargate
- CPU: 0.25 vCPU (256 units)
- Memory: 0.5 GB (512 MB)
- Network mode: awsvpc
- Execution role: ecsTaskExecutionRole
- Task role: docdigest-task-role

**Container: flask-app**
- Image: `<account>.dkr.ecr.us-west-2.amazonaws.com/docdigest-flask:latest`
- Port: 8000
- Essential: Yes
- Environment variables:
  - S3_BUCKET_NAME
  - AWS_DEFAULT_REGION
  - DYNAMODB_TABLE_NAME
  - FLASK_ENV
  - FLASK_DEBUG
- Logging: CloudWatch Logs (/ecs/docdigest-flask)

---

### ECS Service
**Runs and maintains Flask containers**

#### docdigest-flask-service
- Cluster: docdigest-cluster
- Task definition: docdigest-flask-task
- Desired count: 1
- Launch type: Fargate
- Deployment type: Rolling update
  - Minimum healthy: 50%
  - Maximum: 200%
- Load balancer: docdigest-alb
- Target group: docdigest-flask-tg
- Health check grace period: 60 seconds

**Auto Scaling**
- Minimum tasks: 1
- Maximum tasks: 3
- Target metric: CPU utilization 70%
- Scale-out cooldown: 60 seconds
- Scale-in cooldown: 60 seconds

**Network Configuration**
- VPC: Default VPC
- Subnets: 2+ across availability zones
- Security group: docdigest-fargate-sg
- Public IP: Enabled (required to pull from ECR)

---

### Lambda Functions
**Serverless compute for background processing**

#### docdigest-processor
- Runtime: Container image (Python 3.11)
- Image: `<account>.dkr.ecr.us-west-2.amazonaws.com/docdigest-processor:latest`
- Memory: 1024 MB
- Timeout: 2 minutes
- Role: docdigest-processor-role
- Architecture: x86_64

**Trigger**
- Source: SQS queue (docdigest-processing-queue)
- Batch size: 1
- Enabled: Yes

**Environment Variables**
- S3_BUCKET_NAME
- DYNAMODB_TABLE_NAME
- SNS_TOPIC_ARN
- ANTHROPIC_API_KEY
- AWS_DEFAULT_REGION

**Purpose**
- Downloads file from S3
- Calls Claude API for extraction
- Updates DynamoDB with results
- Publishes to SNS when complete
- Deletes file from S3

#### docdigest-notifier
- Runtime: Container image (Python 3.11)
- Image: `<account>.dkr.ecr.us-west-2.amazonaws.com/docdigest-notifier:latest`
- Memory: 512 MB
- Timeout: 30 seconds
- Role: docdigest-notifier-role
- Architecture: x86_64

**Trigger**
- Source: SNS topic (docdigest-processing-complete)
- Enabled: Yes

**Environment Variables**
- DYNAMODB_TABLE_NAME
- AWS_DEFAULT_REGION
- SES_SENDER_EMAIL

**Purpose**
- Fetches session from DynamoDB
- Formats email with results
- Sends email via SES

---

### Storage & Database

#### S3 Bucket
**Temporary file storage**
- Bucket name: docdigest-files-*
- Region: us-west-2
- Purpose: Store uploaded PDFs temporarily
- Lifecycle policy: Delete files after 7 days
- Encryption: AES-256 at rest
- Public access: Blocked
- Event notifications: Triggers SQS on object creation

#### DynamoDB
**Session tracking and results storage**
- Table name: docdigest-sessions
- Partition key: session_id (String)
- Billing mode: On-demand
- Encryption: AWS owned key

**Schema**
```
session_id        - UUID (primary key)
email             - User email address
total_files       - Number of files in session
completed_count   - Files processed so far
processed_files   - Set of processed filenames
status            - PROCESSING | COMPLETED
uploaded_at       - ISO timestamp
completed_at      - ISO timestamp (nullable)
results           - Map of filename → extracted data
```

**Purpose**
- Track upload sessions
- Store processing results
- Atomic updates for concurrent processing

---

### Messaging

#### SQS Queue
**Asynchronous processing queue**
- Queue name: docdigest-processing-queue
- Type: Standard
- Visibility timeout: 120 seconds (matches Lambda timeout)
- Message retention: 4 days
- Dead-letter queue: docdigest-dlq

**Purpose**
- Receives S3 upload events
- Buffers messages for Lambda processor
- Automatic retries on failure

#### SNS Topic
**Pub/sub notification system**
- Topic name: docdigest-processing-complete
- Type: Standard
- Subscribers: Lambda notifier

**Purpose**
- Broadcasts processing completion events
- Decouples processor from notifier
- Allows multiple subscribers (future webhooks, etc.)

#### SES
**Email delivery service**
- Verified identity: sender email address
- Region: us-west-2
- Configuration: Sandbox mode (during development)

**Purpose**
- Sends processing results to users
- Cost-effective ($0.10 per 1,000 emails)

---

### Monitoring

#### CloudWatch Logs
**Centralized logging**

Log Groups:
- `/ecs/docdigest-flask` - Flask application logs
- `/aws/lambda/docdigest-processor` - Processor Lambda logs
- `/aws/lambda/docdigest-notifier` - Notifier Lambda logs

Retention: 7 days

#### CloudWatch Metrics
**Performance monitoring**

Tracked Metrics:
- ECS: CPU utilization, memory, network
- Lambda: Invocations, duration, errors, throttles
- SQS: Messages sent, received, queue depth
- DynamoDB: Read/write capacity consumed
- ALB: Request count, response time, target health

---

## Data Flow

1. User uploads PDF via Flask webapp (ALB → Fargate)
2. Flask stores file in S3, creates DynamoDB session
3. S3 event notification → SQS queue
4. SQS triggers Lambda processor
5. Processor downloads file, calls Claude API, updates DynamoDB
6. When all files complete, processor publishes to SNS
7. SNS triggers Lambda notifier
8. Notifier sends email via SES with results
9. S3 lifecycle policy deletes file after 7 days

## Cost Estimate

| Service | Monthly Cost |
|---------|--------------|
| ECS Fargate (0.25 vCPU, 0.5 GB) | $8-15 |
| Application Load Balancer | $16 |
| Lambda (1000 invocations) | $2-5 |
| DynamoDB (on-demand) | $1-2 |
| S3 (few GB storage) | $0.50 |
| SQS/SNS | Free tier |
| SES (100 emails) | $0.01 |
| CloudWatch Logs | $1 |
| **Total** | **~$30/month** |

Cost optimization:
- Use Fargate Spot (70% cheaper)
- Scale to 0 tasks when not in use
- S3 lifecycle policies

## Why These Services?

**Fargate over EC2**
- No server management
- Auto-scaling included
- Cost-effective for variable traffic
- Zero-downtime deployments

**Lambda over EC2**
- Pay per execution (not 24/7)
- Auto-scales to zero
- Event-driven processing
- No cold start concerns (async processing)

**DynamoDB over RDS**
- Serverless (no provisioning)
- Atomic updates (concurrent processing)
- Fast reads for session lookup
- On-demand billing (no wasted capacity)

**SQS + SNS Pattern**
- Decouples upload from processing
- Automatic retries on failure
- Enables future extensibility (webhooks, etc.)
- Industry-standard event-driven architecture