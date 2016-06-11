from flask import Flask, request
import json
import requests
import os

app = Flask(__name__)

PAT = os.environ['PAT']

@app.route('/', methods=['GET'])
def handle_verification():
  if request.args.get('hub.verify_token', '') == 'inspired_by_zuck':
    return request.args.get('hub.challenge', '')
  else:
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  payload = request.get_data()
  for sender, message in messaging_events(payload):
    send_message(PAT, sender, message)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"

def send_message(token, recipient, inp):
  """Send the message text to recipient with id recipient.
  """
  out = generate_response(inp)
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": out.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})

def generate_response(inp):
    if inp == 'hi':
        out = 'hello!'
    elif inp == 'what\'s up':
        out = 'not much'
    else:
        out = inp

    return out

if __name__ == '__main__':
  app.run()
