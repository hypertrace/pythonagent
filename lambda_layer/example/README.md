# Example lambda function

Prerequisites: 
- Make sure you have docker & docker-compose

1.) Run `./build_example_lambda.sh`

2.) `sam deploy build -t ./template.yaml --stack-name hypertrace-python-example --resolve-s3 --capabilities CAPABILITY_IAM`