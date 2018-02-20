from flask import Flask
from flask import jsonify
app = Flask(__name__)

@app.route('/')
def hello_world(req, res):
	print("request: "+req)
	print("response: "+res)
	data = {
		"conversationToken": "",
		"expectUserResponse": true,
		"expectedInputs": [{
			"inputPrompt": {
				"richInitialPrompt": {
					"items": [{
						"simpleResponse": {
							"textToSpeech": "Howdy! I can tell you fun facts about almost any number, like 42. What do you have in mind?",
							"displayText": "Howdy! I can tell you fun facts about almost any number. What do you have in mind?"
						}
					}],
					"suggestions": []
				}
			},
			"possibleIntents": [{
				"intent": "actions.intent.TEXT"
			}]
		}]
	}
	return jsonify(data)

if __name__ == '__main__':
    app.run()