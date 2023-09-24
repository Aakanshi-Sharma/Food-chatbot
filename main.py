from fastapi import FastAPI
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import json

app = FastAPI()


@app.post("/")
async def handle_request(request: Request):
    try:
        payload = await request.json()
        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        outputs = payload['queryResult']['outputContexts']
        if intent == 'track.order - context: ongoing-tracking':
            track_order(parameters)
            return JSONResponse(content={
                "fulfillmentText": f"Received =={intent}== in the backend"
            })
        else:
            return JSONResponse(content={"fulfillmentText": "Intent not recognized"})
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data")

def track_order(parameters:dict):
    order_id=parameters['number']
    
