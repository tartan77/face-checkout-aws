import boto3, json
from decimal import Decimal

db = boto3.resource('dynamodb')
carts, customers = db.Table('Carts'), db.Table('Customers')
HDR = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}

# Prices live on the server so the browser cannot change them.
CATALOG = {
    'Milk (500ml)': 30, 'Bread': 45, 'Eggs (6)': 60, 'Rice (1kg)': 70,
    'Tea (100g)': 55, 'Biscuits': 20, 'Apples (1kg)': 150, 'Sugar (1kg)': 48,
}

def enc(o):
    return float(o) if isinstance(o, Decimal) else str(o)

def resp(code, body):
    return {'statusCode': code, 'headers': HDR, 'body': json.dumps(body, default=enc)}

def lambda_handler(event, context):
    body = json.loads(event['body'])
    action = body.get('action')

    if action == 'catalog':
        return resp(200, {'catalog': CATALOG})

    cid = body.get('customer_id')
    if not cid or not customers.get_item(Key={'customer_id': cid}).get('Item'):
        return resp(404, {'error': 'Unknown customer'})

    if action == 'get':
        cart = carts.get_item(Key={'customer_id': cid}).get('Item') or {}
        return resp(200, {'items': cart.get('items', [])})

    if action == 'set':
        items = []
        for i in body.get('items', []):
            name, qty = i.get('name'), int(i.get('qty', 0))
            if name in CATALOG and 0 < qty <= 99:
                items.append({'name': name, 'price': Decimal(CATALOG[name]), 'qty': qty})
        if items:
            carts.put_item(Item={'customer_id': cid, 'items': items})
        else:
            carts.delete_item(Key={'customer_id': cid})
        return resp(200, {'items': items})

    return resp(400, {'error': 'Unknown action'})
