from flask import Flask
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient


p = Producer({'bootstrap.servers': 'kafka0:19092,kafka1:29095,kafka2:39095'})
kadmin = AdminClient({'bootstrap.servers': 'kafka0:19092,kafka1:29095,kafka2:39095'})
app = Flask(__name__)

def log_message(err, msg):
  if err is not None:
    print("An error happened while sending message", err)
  else:
    print("Message delivered", msg)

@app.route("/")
def index():
  return "To send a message use /send/:msg: path."

@app.route("/topics")
def topics():
  topics = kadmin.list_topics().topics
  return str(topics)

@app.route("/send/<msg>")
def send(msg):
  p.produce("messages", msg.encode("utf-8"), callback=log_message)
  print("Sending", msg)
  p.flush()
  return "ok"

app.run()