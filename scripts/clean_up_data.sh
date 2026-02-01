
# Load .env file if it exists
if [ -f app/.env ]; then
  export $(grep -v '^#' app/.env | xargs)
fi

aws s3 rm s3://${S3_BUCKET}/ --recursive

aws dynamodb delete-table --table-name ${DYNAMO_DB_TABLE}
aws dynamodb create-table \
  --table-name ${DYNAMO_DB_TABLE} \
  --attribute-definitions AttributeName=session_id,AttributeType=S \
  --key-schema AttributeName=session_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws sqs purge-queue --queue-url ${SQS_URL}