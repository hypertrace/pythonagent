#!/bin/sh

cd prebuild && docker-compose up

echo "Upload the build/function.zip to Lambda"