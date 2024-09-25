### Set up

- Create a service account for the application in Google Cloud IAM
- Add the Log Writer role to the service account
- Add the Monitoring Metric Writer role to the service account
- Generate a new JSON key
- Confgiure the client library project with the GOOGLE_CLOUD_PROJECT environment variable
- Make the key available to the application with the GOOGLE_APPLICATION_CREDENTIALS environment variable

### Start-up Script

#### Environment Variables

`ADVOBS_DEBUG=True` enables more detailed logging to stdout
`ADVOBS_NO_GCE_METADATA=True` disables execution of GCE metadata endpoint when outside of a GCE VM instance
`ADVOBS_DRY_RUN=True` executes the whole script without sending requests to Google Cloud, but logging to stdout instead

