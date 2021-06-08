#!/bin/bash

python bootstrap.sh
conda-build -c conda-forge carnapy $*

