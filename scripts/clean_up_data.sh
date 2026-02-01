aws s3 rm s3://docdigest/ --recursive

aws dynamodb delete-table --table-name docdigest-sessions
aws dynamodb create-table \
  --table-name docdigest-sessions \
  --attribute-definitions AttributeName=session_id,AttributeType=S \
  --key-schema AttributeName=session_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST