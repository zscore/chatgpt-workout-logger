# OPTIONAL: base64 the key (keeps newlines safe in env var)
export SA_KEY_JSON=$(base64 < log-workouts-465819-11b9eb2d72a0.json | tr -d '\n')
export SHEET_ID=1b-24Eiii4U55ex8F0xVsJX7obdKhWJ9-6PI4qT10aR0
export WORKOUT_KEY=add_your_key_here


gcloud functions deploy workoutlogger \
  --gen2 --runtime=python312 --region=europe-west3 \
  --source=. --entry-point=log_workout --trigger-http \
  --set-env-vars SA_KEY_JSON=$SA_KEY_JSON,SHEET_ID=$SHEET_ID,WORKOUT_KEY=$WORKOUT_KEY
