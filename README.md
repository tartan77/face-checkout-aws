# FaceCart: face-based checkout on AWS

Customers check out with their face instead of typing a phone number. A webcam photo is matched against an Amazon Rekognition Face Collection, the customer confirms who they are, builds a cart, and gets a bill.

Built as a Cloud Computing project (5th semester) using only free-tier AWS services.

## How it works

```
Browser (webcam) -> CloudFront + S3 (static site, HTTPS)
        |
        v
   API Gateway (HTTP API)
        |
        v
     Lambda  --->  Rekognition (Face Collection)
        |
        v
    DynamoDB (Customers, Carts, Bills)
```

1. **Enroll (once):** the customer's photo is indexed into a Rekognition Face Collection. The customer ID is stored as the `ExternalImageId`, and the profile is saved in DynamoDB. Consent is required.
2. **Scan:** the browser sends a photo to `/identify`. Lambda calls `SearchFacesByImage` (95% threshold) and looks up the profile.
3. **Confirm:** the UI asks "Is this you, [name]?". Nobody is billed on a match alone.
4. **Cart:** products and prices live in the `cart` Lambda (not the browser). The cart is saved in DynamoDB per customer.
5. **Bill:** `/bill` totals the cart, saves the bill, and clears the cart.

## AWS services

| Service | Purpose |
|---|---|
| Amazon Rekognition | Face Collection, `IndexFaces`, `SearchFacesByImage` |
| AWS Lambda (Python) | `enrollCustomer`, `identifyCustomer`, `cart`, `generateBill` |
| Amazon API Gateway (HTTP API) | `POST /enroll`, `/identify`, `/cart`, `/bill` |
| Amazon DynamoDB | `Customers`, `Carts`, `Bills` tables |
| Amazon S3 + CloudFront | HTTPS hosting for the frontend (camera access needs HTTPS) |
| IAM | Least-privilege role for the Lambda functions |

## Repository layout

```
index.html        Frontend (single file, no build step)
lambda/           Source of the four Lambda functions
README.md
```

## Setup summary

1. Region: `ap-south-1` (Mumbai) for everything.
2. Create the collection: `aws rekognition create-collection --collection-id customers-faces --region ap-south-1`
3. Create DynamoDB tables: `Customers` (pk `customer_id`), `Carts` (pk `customer_id`), `Bills` (pk `bill_id`).
4. Create an IAM role for Lambda with `AWSLambdaBasicExecutionRole` plus access to the collection and the three tables.
5. Create the four Lambda functions from `lambda/` (Python, 15 s timeout, the role above).
6. Create an HTTP API with the four POST routes, and enable CORS (`content-type` header, POST and OPTIONS).
7. Put the API's invoke URL in the `API` constant in `index.html`.
8. Upload `index.html` to a private S3 bucket and serve it through CloudFront (Origin Access Control, default root object `index.html`).

## Security and privacy notes

- Face templates (vectors) are stored, not photos. Photos are not saved anywhere.
- Enrollment requires explicit consent, in line with the DPDP Act 2023. Deleting a user means `delete_faces` plus removing the `Customers` row.
- Product prices are set server-side, so the browser cannot change them.
- The S3 bucket is private. Only CloudFront can read it.

## Known limitations and future work

- A printed photo could fool basic matching. Rekognition Face Liveness would address this.
- `/bill` and `/cart` trust the `customer_id` sent by the browser. A short-lived signed token from `/identify` (or Cognito) would fix this.
- The API is open (CORS `*` during development). For production, restrict the origin and add throttling.

## Cleanup

Delete the Face Collection, Lambda functions, API, DynamoDB tables, CloudFront distribution and S3 bucket when finished, to avoid charges.
