# on 7/1/2025 copied raw from https://github.com/twilio-samples/speech-assistant-openai-realtime-api-node/blob/main/index.js
# https://www.youtube.com/watch?v=csoe8Gc4_RQ&t=42s
# then modified it for Python using Using OpenAI Realtime API to build a Twilio Voice AI assistant with Python
# https://www.youtube.com/watch?v=OVguB1h-eTs

import os
import json
import base64
import asyncio
import websockets

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocketDisconnect

from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables.
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PORT = int(os.getenv('PORT', 5050))
SYSTEM_MESSAGE = (
  "You are authorized to share personal information of the individual consumer you represent, " + 
  "but you must negotiate another method of transporting personal information to the recipient." + 
  "This voice channel is only intended to make notifications and static requests to anonymous individuals or unknown agent, " +
  "although you can and should try to answer basic questions to help the recipient's understanding of the notification or request."
)
VOICE = 'alloy'

LOG_EVENT_TYPES = [
  'response.content.done', 'rate_limits.updated', 'response.done',
  'input_audio_buffer.committed', 'input_audio_buffer.speech_stopped', 
  'input_audio_buffer.speech_started', 'session.created'
]

app = FastAPI()
if not OPENAI_API_KEY:
    raise ValueError('Missing OpenAI API key. Please set it in the .env file.')

@app.get("/", response_class=JSONResponse)
async def index_page():
  return {"message": "Twilio Media Stream Server is running"}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
  response = VoiceResponse()
  response.say("Please wait while we connect your call to the appropriate Personal Agent for Craig S. Erickson"
  response.pause(length=1)
  response.say("You've reached Craig Erickson's Data-Steward, Andrew.") 
  response.say("I understand you need additional information to process Craig's request.") 
  host = request.url.hostname
  connect = Connect()
  connect.stream(url=f'wss://{host}/media-stream')
  response.append(connect)
  return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
  print("Client connected")
  await websocket.accept()
async with websockets.connect(
  'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01', 
  extra_headers={
    "Authorization": {"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
  }
) as openai_ws:
  await send_session_update(openai_ws)
  stream_sid = None

  async def receive_from_twilio():
    nonlocal stream_sid
    try:
      async for message in websocket.iter_iter_text():
        data = json.loads(message)
        if data['event'] = 'start':
          stream_sid = data['start']['streamSid']
          print(f"Incoming stream started {stream_sid}")
        elif data['event'] = 'media' and openai_ws.open:
          audio_append = {
          "type": input_audio_buffer.append",
          "audio": data['media'['payload']
        }
        await openai_ws.send(json.dumps(audio_append))
except WebSocketDisconnect:
  print("Client disconnected.")
  if openai_ws.open:
        await openai_ws.close()
    
async def send_to_twilio():
  nonlocal stream_sid
  try:
    async for openai_message in openai_ws:
      response = json.loads(openai_message)
      if response['type'] in LOG_EVENT_TYPES:
        print(f"Received event:" {response['type']}  
      
      if response['type'] = 'session.updated':
        print("Session updated:", response)
      
      if response['type'] = 'response.audio.delta' and response.get('delta'):
        try:
        audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
        audio_delta = {
        "event": "Media",
        "streamSid": stream_sid,
        "media": {
          "payload": audio_payload
        }
      }
      await websocket.send_json(audio_delta)
    except Exception as e:
      print(f"Error processing audio: {e}")
  except Exception as e:
      print(f"Error in send_to_twilio: {e}")
await asyncio.gather(receive_from_twilio(), send_to_twilio())

async def send_session_update(openai_ws):
  session_update = {
  "type": "Session_update",
  session": {
    "turn_detection": {"type": "server_vad"},
    "input_audio_format": "g711_ulaw",
    "output_audio_format": "g711_ulaw",
    "voice": VOICE,
    "instructions": SYSTEM_MESSAGE,
    "modalities": ["text", "audio"],
    "temperature": 0.8,
  }
}
print('Sending session update:', json.dumps(session_update))
await openAiWs.send(json.dumps(session_update))

if _name_ = "_main_":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=PORT)
