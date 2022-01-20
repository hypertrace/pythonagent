#!/bin/sh

mkdir -p build/python
python3 -m pip install -r function/requirements.txt --upgrade --force-reinstall -t build/python
cp function/main.py -t build/python
cp function/collector.yaml -t build/python
cd build/python || exit

zip -r ../function.zip *