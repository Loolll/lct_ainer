FROM python:3.10

ENV	TZ=Europe/Moscow
RUN	ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN pip install --upgrade pip

COPY etc/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
