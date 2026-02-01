echo "Starting to clean up the data"

# Load .env file if it exists
if [ -f ../app/.env ]; then
  export $(grep -v '^#' ../app/.env | xargs)
fi

echo "Removing files in s3 bucket: ${S3_BUCKET}"
aws s3 rm s3://${S3_BUCKET}/ --recursive
echo "Successfully removed files"

echo "Refreshing DynamoDB table: ${DYNAMO_DB_TABLE}"
aws dynamodb delete-table --table-name ${DYNAMO_DB_TABLE}
aws dynamodb create-table \
  --table-name ${DYNAMO_DB_TABLE} \
  --attribute-definitions AttributeName=session_id,AttributeType=S \
  --key-schema AttributeName=session_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
echo "Successfully refreshed table"

echo "Purging SQS queue"
aws sqs purge-queue --queue-url ${SQS_URL}
echo "Successfully purged SQS queue"