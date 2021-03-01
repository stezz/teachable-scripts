FROM python:3.9-slim-buster as build
WORKDIR /teachable
COPY . .
RUN python3 setup.py sdist

FROM python:3.9-slim-buster
COPY --from=build teachable/dist/teachable-school-manager-1.4.3.tar.gz .
RUN pip install teachable-school-manager-1.4.3.tar.gz
# Installing mime-support to have the Excel files recognized
RUN apt-get update && apt-get -y install mime-support procps
CMD ["teachable_scheduler"]
