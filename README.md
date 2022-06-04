# rebble-asr
asr.rebble.io: speech recognition for rebble

## setup Google Speech-to-text credentials

 In the Cloud Console, go to the Create service account page.
 
 Create or select a project. (I'll use `rebble-asr`)
 
 Enable the Cloud Speech-to-Text API for that project.
 
 Create a service account. Set its permissions role only for Speech-to-Text
 
 Download a private key as JSON. Save it as `key.json`
 

## Setup Google Cloud Platform: Artifact Registry, Cloud Run

 Enable Artifact Registry and Cloud Run
 
 In Artifact Registry create a new repository. Set up the region and note it.
 
 Set as Docker, choose a region, create repository

## Build & Deploy

In Google Cloud Shell Terminal and Editor

  `git clone https://github.com/bdotq/rebble-asr`

  `cd rebble-asr`

  in `Dockerfile` change `$PORT` to `443` if not already set

  upload `key.json` to the `asr` folder

  in `asr/__init__.py` change `lang="en-US"` to whatever language locale you wish to use. `API_KEY` is no longer used, SpeechClient will now refer to key.json.  `auth_req` around line 58 has been commented out, its used to authenticate the user for the rebble.io service, but not needed for this

  `cd ..`
  
  `docker build -t dictation .`
  
 With the REPOSITORY NAME you created in the REGION on Artifact Registry, modify the following command (where `rebble-asr` is your Google cloud project name):
  
  `docker tag dictation YOURREGIION-docker.pkg.dev/YOUR_REPO/rebble-asr/dictation`
 
 Then push to Artifact Registry, similarily modifying this command:
 
  `docker push YOURREGIION-docker.pkg.dev/YOUR_REPO/rebble-asr/dictation`
  
  Open up Artifact Registry
 
  Navigate to the image digests that you just pushed [ YOURREGIION-docker.pkg.dev > YOUR_REPO > rebble-asr > dictation ]
  
  Click on the most recent,  Then click Deploy > Deploy on Cloud Run. 
  
  Set port to be 443 and the rest of defaults will be fine
  
  After server is up running, you can use that is URL created (eg. https://dictation-########.a.run.app)
  
  (Can also deploy with command `gcloud run deploy dictation --image YOURREGIION-docker.pkg.dev/YOUR_REPO/rebble-asr/dictation:latest`)
  
## Use with Pebble

  Log into [auth.rebble.io/account](https://auth.rebble.io/account/)
  
  Under "Experimental Features for Developers", click 'I know what I'm doing'
  
  In the text area paste the following with the URL modified with the server URL you got above
  ```
  {
    "config": {
        "voice": {
            "languages": [
                {
                    "endpoint": "dictation-########.a.run.app",
                    "six_char_locale": "eng-USA",
                    "four_char_locale": "en_US"
                }
            ],
            "first_party_uuids": [
                ""
            ]
            }
        }
  }
  ```
  
 
  
