'use strict'

const handler = (interaction) => {
  return new Promise((resolve, reject) => {
    interaction.response = {
      "fulfillmentText": "This is a text response",
      "fulfillmentMessages": [
        {
          "card": {
            "title": "card title",
            "subtitle": "card text",
            "imageUri": "https://assistant.google.com/static/images/molecule/Molecule-Formation-stop.png",
            "buttons": [
              {
                "text": "button text",
                "postback": "https://assistant.google.com/"
              }
            ]
          }
        }
      ],
      "source": "example.com",
      "payload": {
        "google": {
          "expectUserResponse": true,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "Your last trip was Trip number “100” on “26th September 2018” from “Bosch RMZ Ecospace campus, Bangalore” to “Bosch Koramangala”. \
                  Total kilometers travelled is “10” and duration “1 Hour”. \
                  Your average Speed was “20/Hour” and mileage during trip was “10 kilometers/Liters”. \
                  Your Top speed was “35/Hr”. \
                  You have “5 Instances” of rash driving, “2 Instances “ of Sudden braking and “3 instances” of high speed cornering. \
                  You can improve your driving score & Mileage by driving better on your next trip. \
                  Happy Motoring!"
                }
              }
            ]
          }
        },
        "facebook": {
          "text": "Hello, Facebook!"
        },
        "slack": {
          "text": "This is a text response for Slack."
        }
      },
      "outputContexts": [
        {
          "name": "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/context name",
          "lifespanCount": 5,
          "parameters": {
            "param": "param value"
          }
        }
      ],
      "followupEventInput": {
        "name": "event name",
        "languageCode": "en-US",
        "parameters": {
          "param": "param value"
        }
      }
    }
    // Resolve the Promise to say that the handler performed the action without any error
    resolve()
  })
}

module.exports = handler
