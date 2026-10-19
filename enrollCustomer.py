import boto3, json, base64, uuid, time

rek = boto3.client('rekognition')
customers = boto3.resource('dynamodb').Table('Customers')
COLL = 'customers-faces'
HDR = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}

def resp(code, body):
    return {'statusCode': code, 'headers': HDR, 'body': json.dumps(body)}

def lambda_handler(event, context):
    body = json.loads(event['body'])
    if not body.get('consent'):
        return resp(400, {'error': 'Consent is required'})
    img = base64.b64decode(body['image'].split(',')[-1])

    # Prevent duplicate enrollment
    try:
        dup = rek.search_faces_by_image(CollectionId=COLL, Image={'Bytes': img},
                FaceMatchThreshold=95, MaxFaces=1, QualityFilter='AUTO')
        if dup['FaceMatches']:
            return resp(409, {'error': 'Face already enrolled'})
    except rek.exceptions.InvalidParameterException:
        return resp(400, {'error': 'No clear face detected'})

    cid = 'C' + uuid.uuid4().hex[:8]
    r = rek.index_faces(CollectionId=COLL, Image={'Bytes': img},
            ExternalImageId=cid, MaxFaces=1, QualityFilter='AUTO')
    if not r['FaceRecords']:
        return resp(400, {'error': 'Photo quality too low, retake'})

    customers.put_item(Item={
        'customer_id': cid, 'name': body['name'],
        'face_id': r['FaceRecords'][0]['Face']['FaceId'],
        'consent': True, 'created_at': int(time.time())})
    return resp(200, {'customer_id': cid, 'name': body['name']})
