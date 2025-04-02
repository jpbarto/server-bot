FROM python:3.10-alpine

WORKDIR /server-bot/

COPY requirements.txt /server-bot
RUN pip3 install -r requirements.txt

COPY . /server-bot

ENTRYPOINT ["flask"]
CMD ["--app", "flaskr", "run", "--host", "0.0.0.0", "--port", "5000", "--debug"]
