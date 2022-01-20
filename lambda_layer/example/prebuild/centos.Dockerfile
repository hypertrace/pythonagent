FROM centos/python-36-centos7

USER root
RUN pwd

RUN yum update -y
RUN yum install python-dev zip gcc -y
RUN pip install --upgrade pip
COPY . .


RUN ls
RUN chmod 777 build.sh

CMD ./build.sh

