FROM ubuntu

RUN apt-get update
RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get -y install python3.7
RUN apt-get -y install python3-pip
RUN apt-get -y install build-essential libssl-dev libffi-dev python-dev

ARG AWS_DEFAULT_REGION
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

WORKDIR /DeveloperIQ

COPY requirements.txt ./requirements.txt
RUN pip3 --no-cache-dir install -r requirements.txt

ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

COPY . ./
EXPOSE 8002

CMD ["python3","ProductivityCalculationService/productivity_calculation_service.py"]