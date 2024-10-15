FROM python:3.11.0
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple --trusted-host pypi.douban.com

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY src /usr/src/app/

ENTRYPOINT ["uvicorn", "--reload" ,"--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile", "/app/ssl/tls.key", "--ssl-certfile", "/app/ssl/tls.crt", "main:app" ]