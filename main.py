from fastapi import FastAPI
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import db_connector
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
            return track_order(parameters)
        else:
            return JSONResponse(content={"fulfillmentText": "Intent not recognized"})
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data")


def track_order(parameters: dict):
    order_id = int(parameters['number'])
    status = db_connector.get_order_status(order_id)
    if status:
        fulfillment_text = f"The order status for order id {order_id} is {status}."
    else:
        fulfillment_text = f"No order found for order id {order_id}."
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
