from fastapi import FastAPI
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import helpers
import db_connector
import json

app = FastAPI()
inprogress_order = {}


@app.post("/")
async def handle_request(request: Request):
    try:
        payload = await request.json()
        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult']['outputContexts']
        session_id = helpers.extract_session_id(output_contexts[0]['name'])
        intent_handle = {
            'track.order - context: ongoing-tracking': track_order,
            'order.add - context: ongoing-order': add_to_order
        }
        return intent_handle[intent](parameters, session_id)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data")


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters['food-item']
    quantities = parameters['number']

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I can't understand. Please specify the food items and their quantities."
    else:
        food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_order.keys():
            current_dict = inprogress_order[session_id]
            for j in food_dict:
                if food_dict[j] not in current_dict:
                    current_dict.update(dict((j, food_dict[j])))
                else:
                    current_dict[j] += food_dict[j]
        else:
            inprogress_order[session_id] = food_dict
        order_str=helpers.get_str_from_food_dict(inprogress_order[session_id])

        fulfillment_text = f"Received {food_items} and {quantities} in the backend."
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict, session_id: str):
    order_id = int(parameters['number'])
    status = db_connector.get_order_status(order_id)
    if status:
        fulfillment_text = f"The order status for order id {order_id} is {status}."
    else:
        fulfillment_text = f"No order found for order id {order_id}."
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
