# Agente Doc

## Repo Structure

```
|--server/
|  |--docAgentTool/
|     |--.env_example (example file for environment variables for the agent)
|     |--__init__.py (init file NEEDED)
|     |--agent.py (agent configuration file)
|--app/ (Simple AngularJS with a Chat)
```

## Setup

### Agente

``` bash
cd server

python -m venv .venv

source .venv/bin/activate

pip install google-adk

cd docAgentTool

cp .env_example .env
```
Fill the .env file as described inside

### AngularJS

``` bash
cd app
npm install
```

## Run locally

### Agente

``` bash
cd server
source .venv/bin/activate
adk api_server --allow_origins="*"
```

### AngularJS
```bash
cd app
ng serve
```
Open your browser and go to http://localhost:4200

## Deploy

### Agente

[Install google cloud cli](https://cloud.google.com/sdk/docs/install)
Follow the instructions to configure the gcloud cli

Ensure you have authenticated with Google Cloud (`gcloud auth login` and `gcloud config set project <your-gcloud-project-id>`).

``` bash
cd server
source .venv/bin/activate

adk deploy cloud-run \
--project=<your-glcloud-project-id> \
--region=<your-region-off-choice(eu-west1)> \
--allow_origins="<origins-to-allow-for-CORS("*" for all)>" \
./docAgentTool
```
The agent will be deployed to Cloud Run and will be available at the URL printed in the console.

