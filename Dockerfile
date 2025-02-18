FROM python:3.7.12-slim-buster

EXPOSE 5000

WORKDIR /usr/app

COPY . .

RUN apt-get update
RUN xargs -a packages.txt apt-get install --yes

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install fbprophet

WORKDIR /usr/app/project
CMD streamlit-launchpad . --port 5000
