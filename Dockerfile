FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y wget git
RUN pip install git+git://github.com/pydicom/pydicom.git@affb1cf10c6be2aca311c29ddddc622f8bd1f810
RUN mkdir /code
ADD . /code
WORKDIR /code
RUN python /code/setup.py install

RUN chmod 0755 /opt/conda/bin/deid
ENTRYPOINT '/opt/conda/bin/deid'
