#!/bin/bash

docker build -t dictation .
docker tag dictation YOUR_REGION-docker.pkg.dev/YOUR_REPO/rebble-asr/dictation
docker push YOUR_REGION-docker.pkg.dev/YOUR_REPO/rebble-asr/dictation
gcloud config set run/region SOME_REGION #ex. 'us-west1'
gcloud run deploy dictation --image YOUR_REGION-docker.pkg.dev/YOUR_REPO/rebble-asr/dictation:latest
