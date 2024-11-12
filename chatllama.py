import asyncio
import websockets
from langchain_community.llms import Ollama
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.callbacks.base import BaseCallbackHandler


class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, websocket):
        self.partial_output = ""
        self.websocket = websocket  # Store the websocket connection

    async def on_llm_new_token(self, token: str, **kwargs):
        self.partial_output += token
        # Send each token to the WebSocket client as it is received
        await self.websocket.send(token)


folder_path = "db"

embedding = FastEmbedEmbeddings()

cached_llm = Ollama(model="llama3.2")


async def getresponse(websocket, path):
    streaming_handler = StreamingCallbackHandler(websocket)

    while True:
        try:
            prompt = await websocket.recv()
            print(f"Received prompt: {prompt}")

            response = await cached_llm.agenerate([prompt], callbacks=[streaming_handler])

        except Exception as e:
            print(f"Error: {e}")
            break


start_server = websockets.serve(getresponse, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
