import boto3, json, uuid, time
from decimal import Decimal

db = boto3.resource('dynamodb')
carts, bills = db.Table('Carts'), db.Table('Bills')
HDR = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}

def resp(code, body):
    return {'statusCode': code, 'headers': HDR, 'body': json.dumps(body, default=str)}

def lambda_handler(event, context):
    cid = json.loads(event['body'])['customer_id']
    cart = carts.get_item(Key={'customer_id': cid}).get('Item')
    if not cart or not cart.get('items'):
        return resp(404, {'error': 'Cart is empty'})
    total = sum(Decimal(str(i['price'])) * int(i['qty']) for i in cart['items'])
    bill = {'bill_id': 'B' + uuid.uuid4().hex[:8], 'customer_id': cid,
            'items': cart['items'], 'total': total, 'created_at': int(time.time())}
    bills.put_item(Item=bill)
    carts.delete_item(Key={'customer_id': cid})
    return resp(200, bill)
