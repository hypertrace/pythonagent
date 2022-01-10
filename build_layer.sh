#!/bin/sh
REGION=$1         # ex: us-east-2
PYTHON_VERSION=$2 # ex: python3.9
PYPI_ARTIFACT=$3  # true/false, if true downloads artifact from pypi

if [ -z ${PYPI_ARTIFACT} ]; then
  echo "Use pypi artifact not specified, defaulting to true"
  PYPI_ARTIFACT="true"
fi

if [ -z ${REGION} ]; then
  echo "must pass 1st argument to indicate the region to deploy the layer into"
  echo "ex: us-east-2"
  echo "The region should be the same region as the lambda you want to instrument"
  exit 1
fi

if [ -z ${PYTHON_VERSION} ]; then
  echo "must pass 2nd argument to indicate the python runtime version to build the layer for"
  echo "ex: python3.9"
  echo "The python version should be the same as the python runtime that the lambda runs on"
  exit 1
fi

LAYER_NAME="hypertrace-layer-${PYTHON_VERSION}"
LAYER_NAME=$(echo ${LAYER_NAME} | sed 's/\.//g') # layer name cant have a . in it
LAYER_DESCRIPTION="Hypertrace layer for ${PYTHON_VERSION}"
echo "Layer name: ${LAYER_NAME}"
echo $LAYER_DESCRIPTION

rm -rf lambda_layer/build

mkdir -p lambda_layer/build

if [ "false" = "$PYPI_ARTIFACT" ]; then
  echo "Using local source build"
  pip install build
  python3 -m build
  rm lambda_layer/hypertrace-agent-*.tar.gz
  mv dist/hypertrace-agent-*.tar.gz ./lambda_layer
  docker build -t aws-hypertrace-lambda-python-layer -f lambda_layer/source.Dockerfile lambda_layer --build-arg runtime=$PYTHON_VERSION
else
  docker build -t aws-hypertrace-lambda-python-layer -f lambda_layer/pypi.Dockerfile lambda_layer --build-arg runtime=$PYTHON_VERSION
fi
docker run --rm -v "$(pwd)/lambda_layer/build:/out" aws-hypertrace-lambda-python-layer
cd lambda_layer && unzip build/layer.zip -d ./build/layer
sam deploy build -t ./template.yaml --stack-name hypertrace-python --resolve-s3 --region $REGION \
    --parameter-overrides LayerName=$LAYER_NAME Runtime=$PYTHON_VERSION

arn=$(aws lambda list-layer-versions --layer-name $LAYER_NAME --region $REGION --query 'max_by(LayerVersions, &Version).LayerVersionArn')
		echo $arn | sed 's/\"//g'
echo "$PYTHON_VERSION Layer ARN:"
echo $arn