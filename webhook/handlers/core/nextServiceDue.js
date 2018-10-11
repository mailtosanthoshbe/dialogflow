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
                  "textToSpeech": "Your last service was done on “26th October 2018” and “10000 Kilometers”.\
                  As per schedule, your next service is due at “15th January 2019” or on “15000 Kilometers”.\
                  Your car has covered “12000” Kilometers till date and Your next service is due in “90” days"
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
