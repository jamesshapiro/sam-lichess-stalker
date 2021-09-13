#!/bin/bash -e

if [ -d src/python ]; then
	rm -rf src/python
fi

pip3 install --target src/python -r src/requirements.txt

cp -R src/lichessdependencies src/python

sam build
