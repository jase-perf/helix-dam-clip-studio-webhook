# Helix DAM Clip Studio Webhook

This repository contains a webhook service for processing Clip Studio files in Helix DAM. It automatically generates previews and extracts metadata from .clip files and adds them to DAM so they are taggable and searchable with nice thumbnails and preview images.

## Prerequisites

- Docker installed on your server
- Git (for pulling updates)
- Access to your Helix DAM instance
- Account key for Helix DAM API access

## Installation
This is simplest to install directly on your DAM (Teamhub) instance so no traffic needs to go over the public internet.

1. Clone the repository:
   ```
   git clone https://github.com/jase-perf/helix-dam-clip-studio-webhook.git
   cd helix-dam-clip-studio-webhook
   ```
2. Make sure that `start_container.sh` and `update_and_build.sh` are executable:
   ```
   chmod +x start_container.sh update_and_build.sh
   ```
3. Build the Docker image:
   ```
   ./update_and_build.sh
   ```

4. Edit the `start_container.sh` script:
   - Replace `http://localhost` with your actual DAM URL (If you are running this on the same instance then localhost should work and you won't need to change it)
   - Replace `your_account_key_here` with your Helix DAM account key

5. Start the container:
   ```
   ./start_container.sh
   ```

6. Setup the webhook on DAM
   - As an admin in DAM, click on in the upper right menu and choose `Go to Helix Teamhub`
   - Select `Webhooks` from the left hand menu
   - Click the + button to add a new webhook
   - Give it a name and customize any settings you want (the defaults should work if you want this to apply to all projects in DAM)
   - Click Next and enter the URL of the docker container's webhook. If running on the same instance as DAM, then `http://localhost:8080/webhook` should work. Then click Save.

The webhook service is now running and will process Clip Studio files added to your DAM instance.

## Updating

To update the service with the latest changes:

1. Pull the latest changes and rebuild the Docker image:
   ```
   ./update_and_build.sh
   ```

2. Restart the container:
   ```
   ./start_container.sh
   ```

## Configuration

The service runs on port 8080 by default. If you need to change this, modify the `-p 8080:8080` line in `start_container.sh` to your desired port.

## Troubleshooting

- To view logs: `docker logs clip-studio-webhook`
- To stop the service: `docker stop clip-studio-webhook`
- To start a stopped service: `docker start clip-studio-webhook`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
