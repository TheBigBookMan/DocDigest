# ADR: Asynchronous File Processing

## Context
File processing involves storing the file into an S3 bucket and using an LLM to query on the uploaded file. This process can take 10-20 seconds as LLMs are not particularly fast, so if a user uploads multiple files, using the Flask API to query the LLM could lead to browser timeout and server crashing under higher load.

## Decision
Using an asynchronous event-driven architecture we are eliminating the reliance on one server processing everything.
We will use:
- S3 for storage of files
- SQS will queue tasks to ensure that the system can scale and files are not lost
- DynamoDB will store session information to keep track of file grouping
- SNS are acts as a trigger to bridge processor and notifier

## Consequences
### Positives
- Decoupling the querying of LLM on files by using a lambda serverless function
- Message queue used to ensure that data is not lost and that tasks get actioned if any issues occur server side
- S3 storage for files is simple to use
- Serverless functionality for lambda reduces server overhead

### Negatives
- Using multiple services which can create extra complexity
- Relying on S3 events to push to SQS rather than creating own SQS makes debugging harder
- Lambda invocations can start to get more expensive as we are doing 1 invocation per file uploaded