# syntax=docker/dockerfile:1

FROM python:3.10-slim
MAINTAINER Leonid Kostrykin <leonid.kostrykin@bioquant.uni-heidelberg.de>

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir pybind11
RUN pip install --no-cache-dir jupyterlab

RUN python -m pip install --force-reinstall CarnaPy*.whl

EXPOSE 8890
CMD ['jupyter', 'lab', '--port', '8890']
