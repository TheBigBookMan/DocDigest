echo "Starting build and deployment of DocDigest webapp"

# Load .env file if it exists
if [ -f ../app/.env ]; then
  export $(grep -v '^#' ../app/.env | xargs)
fi

echo "Starting retrieval of ECR authentication"
aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
echo "Successfully retrieved ECR authentication"

echo "Starting docker image build for webapp"
docker build -t ${ECR_REPO_NAME} ..
echo "Finished building webapp image"

echo "Tagging image"
docker tag ${ECR_REPO_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest

echo "Pushing docker image to ECR"
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest
echo "Successfully pushed docker image to ECR"