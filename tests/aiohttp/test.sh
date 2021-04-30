#!/bin/bash
curl -X 'POST' \
  'https://petstore.swagger.io/v2/pet' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": 0,
  "category": {
    "id": 0,
    "name": "doggie"
  },
  "name": "doggie",
  "photoUrls": [
    "http://example.co"
  ],
  "tags": [
    {
      "id": 0,
      "name": "doggie"
    }
  ],
  "status": "available"
}'
