# CSV Transformer Application Documentation

This document provides instructions on how to set up and run the CSV Transformer application on macOS and Windows PC.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Docker Desktop
  - For macOS: [Docker Desktop for Mac](https://docs.docker.com/docker-for-mac/install/)
  - For Windows: [Docker Desktop for Windows](https://docs.docker.com/docker-for-windows/install/)
- Git (optional, for cloning the repository)

## Setup and Running the Application

Follow these steps to set up and run the application on your local machine:

### 1. Get the Application Code

Either clone the repository or download the source code to your local machine.

Using Git:
```
git clone https://github.com/michalito/sortly-csv-formatter.git
cd sortly-csv-formatter
```

### 2. Build the Docker Image

Open a terminal (macOS) or Command Prompt/PowerShell (Windows) and navigate to the project directory.

Build the Docker image:
```
docker build -t sortly-csv-formatter .
```

### 3. Run the Docker Container

After successfully building the image, run the Docker container:

```
docker run -p 5000:5000 sortly-csv-formatter
```

### 4. Access the Application

Open a web browser and go to:
```
http://localhost:5000
```

You should now see the CSV Formatter application interface.

## Usage

1. Click the "Choose File" button to select your CSV file.
2. Click the "Transform CSV" button to process the file.
3. The transformed CSV will be automatically downloaded.

## Troubleshooting

If you encounter any issues:

1. Ensure Docker Desktop is running.
2. Check if port 5000 is available on your machine.
3. Review the Docker logs for any error messages:
   ```
   docker logs <container-id>
   ```

## Stopping the Application

To stop the running container:

1. Find the container ID:
   ```
   docker ps
   ```
2. Stop the container:
   ```
   docker stop <container-id>
   ```

## Development

For development purposes, you can mount your local directory to the container for live code changes:

```
docker run -p 5000:5000 -v $(pwd):/app sortly-csv-transformer
```

Note: On Windows, replace `$(pwd)` with `%cd%` in Command Prompt or `${PWD}` in PowerShell.