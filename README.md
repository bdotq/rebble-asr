# rebble-asr
asr.rebble.io: speech recognition for rebble

## setup Google Speech-to-text credentials

 In the Cloud Console, go to the Create service account page.
 
 Create or select a project. (I'll use `rebble-asr`)
 
 Enable the Cloud Speech-to-Text API for that project.
 
 Create a service account.
 
 Download a private key as JSON. Save it as `key.json`
 

## setup Google Cloud Platform: Artifact Registry, Cloud Run

 Enable Artifact Registry and Cloud Run
 
 In Artifact Registry create a new repository
 
 Set as Docker, choose a region, create repository

## build & deploy

In Google Cloud Shell terminal

  `git clone https://github.com/bdotq/rebble-asr`

  `cd rebble-asr`

  in `Dockerfile` change `$PORT` to `443`

  upload `key.json` to the `asr` folder

  in `asr/__init__.py` API_KEY no longer used, but `GOOGLE_APPLICATION_CREDENTIALS` will refer to key.json

  `auth_req` around line 58 has been commented out, needed to authenticate the user for the rebble.io service, but no needed for this

  `cd ..`
  
  `docker build -t dictation .`
  
 With the repository you creted with the region in Artifact Registry, modify the following command (where `rebble-asr` is your project name)
  
  `docker tag dictation YOURREGIION-docker.pkg.dev/YOUR_REPO/rebble-asr/dictation`
 
 Then push to Artifact Registry:
 
  `docker push YOURREGIION-docker.pkg.dev/YOUR_REPO/rebble-asr/dictation`
  
  Open up Artifact Registry
 
  Navigate to the image digests that you just pushed [ YOURREGIION-docker.pkg.dev > YOUR_REPO > rebble-asr > dictation ]
  
  Click on the most recent,  Then click Deploy > Deploy on Cloud Run. 
  
  Set port to be 443 and the rest of defaults will be fine
  
  After server is up running, you can use that is URL created (eg. https://dictation-########.a.run.app)
  
  
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
  
 
  
