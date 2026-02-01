echo "Starting build and deployment of DocDigest lambda notifier"

# Load .env file if it exists
if [ -f ../lambda/notifier/.env ]; then
  export $(grep -v '^#' ../lambda/notifier/.env | xargs)
fi

GIT_SHA=$(git rev-parse --short HEAD)
ECR_URL=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com

echo "Starting retrieval of ECR authentication"
aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
echo "Successfully retrieved ECR authentication"

echo "Starting docker image build for lambda notifier"
docker build -t ${ECR_REPO_NAME}:${GIT_SHA} ../lambda/notifier
echo "Finished building lambda notifier image"

echo "Tagging image"
docker tag ${ECR_REPO_NAME}:${GIT_SHA} ${ECR_REPO_NAME}:latest
docker tag ${ECR_REPO_NAME}:${GIT_SHA} ${ECR_URL}/${ECR_REPO_NAME}:${GIT_SHA}
docker tag ${ECR_REPO_NAME}:${GIT_SHA} ${ECR_URL}/${ECR_REPO_NAME}:latest

echo "Pushing docker image to ECR"
docker push ${ECR_URL}/${ECR_REPO_NAME}:latest
docker push ${ECR_URL}/${ECR_REPO_NAME}:${GIT_SHA}
echo "Successfully pushed docker image to ECR"