FROM python:3.9-slim-buster
# Fetching teachable-school-manager from PyPi
RUN pip install teachable-school-manager
# Installing mime-support to have the Excel files recognized
RUN apt-get update && apt-get -y install mime-support
