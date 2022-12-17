# aws-opensearch-s3-event

This repository consists of lambda function code in python 3.8 that enables you to listen to s3 new files, and upload it to opensearch.

## Things to do

1. Add two environment variables to the lambda function.
    1. ES_HOST - OpenSearch domain endpoint host
    2. ES_INDEX - OpenSearch index name
2. Add a new role with the policy (use the contents of the lambda_policy.json) and attach it as the execution role of the lambda. Replace the <accountId> with actual account id and <bucketName> with actual s3 bucket name within the file.
3. The zip file opensearch_s3_event_handler.zip contains the lambda function along with the dependant python 3.8 packages which can be uploaded to the lambda function code. If you are using a different python version, please use the corresponding packages.
