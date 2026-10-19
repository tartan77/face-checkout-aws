import boto3, json, base64

rek = boto3.client('rekognition')
customers = boto3.resource('dynamodb').Table('Customers')
COLL = 'customers-faces'
HDR = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}

def resp(code, body):
    return {'statusCode': code, 'headers': HDR, 'body': json.dumps(body, default=str)}

def lambda_handler(event, context):
    img = base64.b64decode(json.loads(event['body'])['image'].split(',')[-1])
    try:
        r = rek.search_faces_by_image(CollectionId=COLL, Image={'Bytes': img},
                FaceMatchThreshold=95, MaxFaces=1, QualityFilter='AUTO')
    except rek.exceptions.InvalidParameterException:
        return resp(400, {'error': 'No clear face detected'})

    if not r['FaceMatches']:
        return resp(404, {'error': 'No match found'})

    m = r['FaceMatches'][0]
    cid = m['Face']['ExternalImageId']
    item = customers.get_item(Key={'customer_id': cid}).get('Item')
    if not item:
        return resp(404, {'error': 'Profile missing'})
    return resp(200, {'customer_id': cid, 'name': item['name'],
                      'confidence': round(m['Similarity'], 2)})
