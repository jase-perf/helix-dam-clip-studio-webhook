#!/bin/bash

# Stop and remove the existing container if it exists
docker stop clip-studio-webhook || true

# Start the new container
docker run -d \
  --name clip-studio-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  -e DAM_URL=http://localhost \
  -e ACCOUNT_KEY=your_account_key_here \
  clip-studio-webhook