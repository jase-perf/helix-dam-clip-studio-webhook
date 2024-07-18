#!/bin/bash

# Stop and remove the existing container if it exists
echo "Stopping existing container if any"
docker stop clip-studio-webhook || true
docker rm clip-studio-webhook || true

echo "Starting new container"
# Start the new container
docker run -d \
  --name clip-studio-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  -e DAM_URL="http://10.0.0.1" \ # Change this to the private IP address of DAM
  -e ACCOUNT_KEY=your_account_key_here \
  clip-studio-webhook

echo "Container started"
echo "You can tail logs with this command: docker logs -f clip-studio-webhook"