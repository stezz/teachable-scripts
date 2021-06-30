ARG PACKAGE=teachable-school-manager-1.5.6.tar.gz
FROM python:3.9-slim-buster as build
WORKDIR /teachable
COPY . .
RUN python3 setup.py sdist

ARG PACKAGE
FROM python:3.9-slim-buster
COPY --from=build teachable/dist/${PACKAGE} .
ARG PACKAGE
RUN pip install ${PACKAGE}
# Installing mime-support to have the Excel files recognized
RUN apt-get update && apt-get -y install mime-support procps
CMD ["teachable_scheduler"]
