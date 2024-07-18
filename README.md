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
   - Replace `http://10.0.0.1` with your actual DAM private IP or URL (If you are running this on the same instance then the private IP is preferred. If running on an external server, then using a public https endpoint will be more secure.)
   - Replace `your_account_key_here` with your Helix DAM account API key:
     - As an admin in DAM, click on in the upper right menu and choose `Go to Helix Teamhub`
     - Click on the small arrow in the upper right by your profile image and select `User Preferences`
     - Select API Keys
     - Click `+ Add new key` at the bottom, give it a title, and click save
     - Now copy the API key that was generated and paste it into the `start_container.sh` file.

5. Start the container:
   ```
   ./start_container.sh
   ```

6. Setup the webhook on DAM
   - As an admin in DAM, click on in the upper right menu and choose `Go to Helix Teamhub`
   - Select `Webhooks` from the left hand menu
   - Click the + button to add a new webhook
   - Give it a name and customize any settings you want (the defaults should work if you want this to apply to all projects in DAM)
   - Click Next and enter the URL or IP address of the docker container's instance followed by `/webhook`. If running on the same instance as DAM, then `http://localhost:8080/webhook` should work. Then click Save.

The webhook service is now running and will process Clip Studio files added to your DAM instance.

See instructions below on **Tailing Logs** to view the logs and confirm that webhook requests are being received successfully.

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


## Troubleshooting and Monitoring

### Viewing Logs
To view the logs of the container:

```bash
docker logs clip-studio-webhook
```

This will display all logs from the container start.

### Tailing Logs
To continuously watch the logs in real-time:

```bash
docker logs -f clip-studio-webhook
```

This command will follow the log output, displaying new log entries as they occur. Press Ctrl+C to stop watching the logs.

### Viewing Recent Logs
To view only the most recent logs:

```bash
docker logs --tail 100 clip-studio-webhook
```

This will show the last 100 log entries. Adjust the number as needed.

### Other Useful Commands
- To stop the service: `docker stop clip-studio-webhook`
- To start a stopped service: `docker start clip-studio-webhook`
- To restart the service: `docker restart clip-studio-webhook`

### Common Issues
If you encounter issues:
1. Ensure the DAM_URL and ACCOUNT_KEY are correctly set in the `start_container.sh` script.
2. Check if the required ports are open and not used by other services.
3. Verify that Docker is running on your system.

If problems persist, review the logs for specific error messages and consult the project documentation or seek support.

[Rest of the README remains the same...]
```

This expanded section provides users with:
1. Instructions for viewing logs in different ways (all logs, real-time tailing, recent logs).
2. Commands for basic container management.
3. A brief guide on what to check if they encounter issues.

These additions will help users better monitor and troubleshoot the webhook service, enhancing their ability to maintain and manage the deployment effectively.