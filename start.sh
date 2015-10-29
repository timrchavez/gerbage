#!/bin/bash

export PYTHONPATH=`pwd`:$PYTHONPATH
zoidbergd -c `pwd`/gerbage/zoidberg/conf.yaml -v
