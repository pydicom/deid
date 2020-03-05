FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y wget git pkg-config libfreetype6-dev g++
RUN conda install matplotlib
WORKDIR /code
ADD . /code
RUN python /code/setup.py install

RUN chmod 0755 /opt/conda/bin/deid
ENTRYPOINT ["/opt/conda/bin/deid"]
