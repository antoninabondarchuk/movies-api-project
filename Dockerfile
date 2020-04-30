FROM python:3.6-alpine

WORKDIR /code/

COPY . /code/

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev linux-headers zlib-dev jpeg-dev libffi-dev
RUN pip install psycopg2-binary
RUN pip install -r requirements.txt

VOLUME /code/static_root/

EXPOSE 8000

RUN ["chmod", "+x", "/code/entrypoint.sh"]
