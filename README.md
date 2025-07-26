This repo uses google cloud functions and the API interface to Google Sheets to log workouts via chat gpt.

# Instructions on the setup

1. Create a google sheet with the columns Exercise,	Weight (kg),	Reps,	Sets,	Comment,	Date,
Example: https://docs.google.com/spreadsheets/d/1jqzNKE12vsp8WN8dwLg6uhk1t3_nRiMpeiWGK8CptwM/edit?usp=sharing
2. Then, we need to enable the google sheets API in google cloud.
3. Create a service account and download its json credentials.
4. In the sheets Share dialog, you should add the service account as an editor.


If you want to test the function locally, you can do it like this
```
python -m venv venv
source venv/bin/activate               # Windows: venv\Scripts\activate

# install deps (make sure functions-framework is in requirements.txt)
pip install -r requirements.txt


python -m functions_framework --target=log_workout --port=8080

curl -X POST http://127.0.0.1:8080/workout-entry \
     -H "x-api-key: $WORKOUT_KEY" \
     -H "Content-Type: application/json" \
     -d '{"exercise":"Test Curl","weight":42,"reps":10,"sets":3,"comment":"local run"}'

```
5. You need to locally generate an API key with a command like this `openssl rand -base64 32 | tr -d '=+/[:space:]'` and add this to the environemnt variable WORKOUT_KEY
6. You should find the sheets id and export the json key as base 64 into the environment variables SA_KEY_JSON and SHEET_ID, which you can find by looking at the URl of your google sheet. In the above case, it should be 1jqzNKE12vsp8WN8dwLg6uhk1t3_nRiMpeiWGK8CptwM. You can then run the command in the deploy script to deploy the cloud function which will deploy the main.py flask app. 

7. Then, once you get the URL from the cloud run function, you can test it with the following command and check to see if a row is appended to the google sheet.

```curl -X POST "$FUNC_URL/workout-entry" \
     -H "Content-Type: application/json" \
     -H "x-api-key: $WORKOUT_KEY" \
     -d '{"exercise":"Bench Press","weight":90,"reps":5,"sets":3,"comment":"test call"}'
```
8. Now we can configure the GPT. 
You can fill out these fields:
Name: Google Sheets Workout Logger
Description: Logs workout data into Google Sheets, including reps, sets, weight, exercise, and comments.
Conversation Starters: Add bench press: 3 sets of 10 reps at 60 kg, felt a bit tiring

and it will generate isntructions for it.

For the custom action, you should past the `gpt-openapi-schema.json` into it and give the function URL. Then, for authentication you should pick API Key, Auth Type custom with customer header name `x-api-key`, and you should paste in the previous key you generated.

Now, you can test it out to see if it works!

possible improvements: 
1. We could lock down the google cloud function URL better? I'm not sure if there's more authentication that should be used there.
2. We might also be able to reuse the service account credentials somehow so we don't have to maintain two different authentication strings?
3. It would actually be better if we could call the google sheet through an Apps script, but unfortunately I was running into some issues getting the API to be called properly by the customer GPT action because it was adding some extra authentication string, although possibly this could be fixed with a better OpenAPI spec? It's hard to debug this because you can't really see the API calls that GPT is making.
4. Also, there is no support in the android app yet for the custom gpt, so it has to be used in the web interface or from desktop.