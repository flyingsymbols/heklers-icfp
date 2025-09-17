FROM python:3.13

RUN mkdir /data /code

COPY ./docker/requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt

COPY ./server /code/app/
WORKDIR /code

ENTRYPOINT ["fastapi", "run", "app/main.py"]
