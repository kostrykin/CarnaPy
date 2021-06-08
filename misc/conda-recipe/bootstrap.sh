#!/usr/bin/env python

import yaml
with open('../VERSIONS.yaml', 'r') as io:
    versions = yaml.safe_load(io)

import os
from pathlib import Path
root_dir   = Path(os.path.abspath(os.path.dirname(__file__)))
input_dir  = root_dir / 'carnapy.in'
output_dir = root_dir / 'carnapy'
output_dir.mkdir(parents=True, exist_ok=True)

from string import Template
values = dict(
    VERSION_CARNA_PY = versions['build'  ]['carnapy'],
    VERSION_CARNA    = versions['package']['carna'  ],
)
print(f'Configured to build conda package version: {values["VERSION_CARNA_PY"]}')
for filename in ('build.sh', 'meta.yaml'):
    with open(str(input_dir / filename), 'r') as io:
        source = Template(io.read())
    result = source.substitute(values)
    with open(str(output_dir / filename), 'w') as io:
        io.write(result)

