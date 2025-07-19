# OPTIONAL: base64 the key (keeps newlines safe in env var)
export SA_KEY_JSON=$(base64 -w0 log-workouts-465819-11b9eb2d72a0.json)
export SHEET_ID=1b-24Eiii4U55ex8F0xVsJX7obdKhWJ9-6PI4qT10aR0

gcloud functions deploy workoutLogger \
  --gen2 --runtime=python312 --region=us-central1 \
  --source=. \
  --entry-point=app \
  --trigger-http --allow-unauthenticated \
  --set-env-vars SA_KEY_JSON=$SA_KEY_JSON,SHEET_ID=$SHEET_ID

