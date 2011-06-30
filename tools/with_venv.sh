#!/bin/bash
TOOLS=`dirname $0`
VENV=$TOOLS/../.benchmark-venv
source $VENV/bin/activate && $@
