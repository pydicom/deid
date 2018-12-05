FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y wget git pkg-config libfreetype6-dev
RUN pip install pydicom
RUN /opt/conda/bin/conda install matplotlib==2.1.2
RUN mkdir /code
ADD . /code
WORKDIR /code
RUN python /code/setup.py install

RUN chmod 0755 /opt/conda/bin/deid
ENTRYPOINT ["/opt/conda/bin/deid"]
