FROM python:3.10-alpine

COPY ./app /opt/app

WORKDIR /opt/app

# COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./app .
CMD [ "python", "./oncall-exp.py" ]