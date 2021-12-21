#!/bin/sh

mkdir -p build/python
echo "mkdir done"
python3 -m pip install -r function/requirements.txt --upgrade --force-reinstall -t build/python
echo "install deps done "
# python3 -m pip install ./hypertrace-agent-0.9.2.dev0.tar.gz  --upgrade --force-reinstall -t build/python
echo "install hy done"
cp function/main.py -t build/python
echo "copy main done"

# rm build/python/googleapis_common_protos-1.54.0-py3.10-nspkg.pth

cd build/python || exit
echo "cd done"
zip -r ../function.zip *
echo "zip done"