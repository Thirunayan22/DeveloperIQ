FROM ubuntu

RUN apt-get update
RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get -y install python3.7
RUN apt-get -y install python3-pip
RUN apt-get -y install build-essential libssl-dev libffi-dev python-dev


WORKDIR ./DeveloperIQ

COPY requirements.txt ./requirements.txt
RUN pip3 --no-cache-dir install -r requirements.txt

COPY . ./
