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
            'order.add - context: ongoing-order': add_to_order,
            'order.complete - context: ongoing-order': complete_order
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
                if j not in current_dict:
                    current_dict[j] = food_dict[j]
                else:
                    current_dict[j] += food_dict[j]
        else:
            inprogress_order[session_id] = food_dict
        order_str = helpers.get_str_from_food_dict(inprogress_order[session_id])

        fulfillment_text = f"So far you have {order_str}. Do you want anything else?"
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def save_to_db(orders: dict):
    next_order_id = db_connector.get_next_order_id()
    for food_item, quantity in orders.items():
        rcode = db_connector.insert_into_db(food_item, quantity, next_order_id)
        if rcode == -1:
            return -1
    return next_order_id


def complete_order(parameters: dict, session_id):
    if session_id not in inprogress_order:
        fulfillment_text = "There is a trouble in tracking your order. Please order again."
    else:
        orders = inprogress_order[session_id]
        order_id = save_to_db(orders)
        if order_id == -1:
            fulfillment_text = "Sorry, error in saving in our database."
        else:
            total_price=db_connector.get_total_price(order_id)
            fulfillment_text=f"""Successfully placed the order.
                                Here is the order id {order_id}.
                                Total amount of the order is {total_price} which you can pay after the delivery."""
    return JSONResponse(content={
        "fulfillmentText":fulfillment_text
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
