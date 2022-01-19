REGION=$1 # ex: us-east-1
BUCKET_NAME=$2 # ex: collector-layer

if [ -z ${REGION} ]; then
  echo "must pass 1st argument to indicate the region to deploy the layer into"
  echo "ex: us-east-2"
  echo "The region should be the same region as the lambda you want to instrument"
  exit 1
fi

if [ -z ${BUCKET_NAME} ]; then
  echo "2nd arg not provided, using default bucket name of 'collector-bucket'"
 BUCKET_NAME='collector-bucket-test-donnie'
fi


docker build -t collector-layer lambda_layer -f lambda_layer/collector.Dockerfile
docker run --rm -v "$(pwd)/lambda_layer/collector-build:/volume-copy" collector-layer

echo "Publishing collector extension layer..."
aws s3 mb s3://${BUCKET_NAME}
aws s3 cp ./lambda_layer/collector-build/collector-extension.zip s3://${BUCKET_NAME}
aws lambda publish-layer-version --layer-name collector-layer --content S3Bucket=${BUCKET_NAME},S3Key=collector-extension.zip --compatible-runtimes python3.6 python3.7 python3.8 python3.9 --query 'LayerVersionArn' --output text
echo Clearing cached files...
aws s3 rm s3://${BUCKET_NAME}/collector-extension.zip
aws s3 rb s3://${BUCKET_NAME}
echo OpenTelemetry Collector layer published.

# aws lambda add-layer-version-permission --layer-name node-sharp \
#  --principal '*' \
#  --action lambda:GetLayerVersion \
#  --version-number 3
#  --statement-id public
#  --region us-east-1