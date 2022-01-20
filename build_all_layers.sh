#!/bin/sh
REGION=$1    # required # ex: us-east-2
HT_ARTIFACT_FROM_PYPI=$2 # true/false - default=true, if true pypi artifact is used instead of local source build, if false build agent from source locally

if [ -z ${REGION} ]; then
  echo "must pass argument to indicate the region to deploy the layer into"
  echo "ex: us-east-2"
  echo "The region should be the same region as the lambda you want to instrument"
  exit 1
fi

sh build_layer.sh $REGION python3.6 $HT_ARTIFACT_FROM_PYPI
sh build_layer.sh $REGION python3.7 $HT_ARTIFACT_FROM_PYPI
sh build_layer.sh $REGION python3.8 $HT_ARTIFACT_FROM_PYPI
sh build_layer.sh $REGION python3.9 $HT_ARTIFACT_FROM_PYPI

versions=(python36 python37 python38 python39)

echo '--done--'

for t in ${versions[@]}; do
  LAYER_NAME="hypertrace-layer-${t}"
  echo "$t Layer ARN:"

  arn=$(aws lambda list-layer-versions --layer-name $LAYER_NAME --region $REGION --query 'max_by(LayerVersions, &Version).LayerVersionArn')
  echo $arn
done
