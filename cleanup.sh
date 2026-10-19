#!/usr/bin/env bash
# FaceCart: delete everything to avoid AWS charges. Run from CloudShell.
# Replace YOUR_API_ID with the ID in your API's invoke URL (the part before ".execute-api").

REGION=ap-south-1

# Rekognition: removes ALL stored face templates (biometric data)
aws rekognition delete-collection --collection-id customers-faces --region $REGION

# DynamoDB tables
for t in Customers Carts Bills; do
  aws dynamodb delete-table --table-name $t --region $REGION
done

# Lambda functions
for f in enrollCustomer identifyCustomer cart generateBill; do
  aws lambda delete-function --function-name $f --region $REGION
done

# API Gateway (HTTP API)
aws apigatewayv2 delete-api --api-id YOUR_API_ID --region $REGION

# IAM role: remove the inline policy and the managed policy first, then the role
aws iam delete-role-policy --role-name face-checkout-role --policy-name face-checkout-policy
aws iam detach-role-policy --role-name face-checkout-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name face-checkout-role

# CloudWatch log groups created by the Lambda functions
for f in enrollCustomer identifyCustomer cart generateBill; do
  aws logs delete-log-group --log-group-name /aws/lambda/$f --region $REGION
done

# Do these two in the console:
#  - CloudFront: disable the distribution, wait until it finishes deploying, then delete it
#  - S3: empty the bucket, then delete it
