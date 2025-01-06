# CRON 
CRON server to run multiple cronjobs.

## Deploy
1. With an existing Kubernetes Cluster running, run `./deploy.sh`.
2. This will build the cron server as a docker image and deploy it to the namespace.

## Conventions
* All cronjobs are stored within the `crons` file.
* All scripts that are to be called via a cronjob are stored within the `scripts` folder.
* All error logs from all cronjobs are stored at `/var/log/errors`.