FROM python:3.6
MAINTAINER jadbin <jadbin.com@hotmail.com>

ADD ./ /opt/app

RUN chmod +x /opt/app/bin/manage \
  && pip install -r /opt/app/requirements/app.txt

CMD /opt/app/bin/manage start --daemon-off
