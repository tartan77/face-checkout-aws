#!/usr/bin/env bash
# FaceCart: create the data layer from AWS CloudShell (region ap-south-1).
# The Lambda functions, API Gateway, S3 and CloudFront were created in the AWS console.

REGION=ap-south-1

# 1. Rekognition Face Collection (stores face vectors, not photos)
aws rekognition create-collection \
  --collection-id customers-faces \
  --region $REGION

# 2. DynamoDB tables (on-demand billing)
aws dynamodb create-table \
  --table-name Customers \
  --attribute-definitions AttributeName=customer_id,AttributeType=S \
  --key-schema AttributeName=customer_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION

aws dynamodb create-table \
  --table-name Carts \
  --attribute-definitions AttributeName=customer_id,AttributeType=S \
  --key-schema AttributeName=customer_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION

aws dynamodb create-table \
  --table-name Bills \
  --attribute-definitions AttributeName=bill_id,AttributeType=S \
  --key-schema AttributeName=bill_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION

# 3. Check that the enrolled faces are in the collection
# aws rekognition list-faces --collection-id customers-faces --region $REGION
