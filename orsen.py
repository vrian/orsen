from flask import Flask
from flask import jsonify
from flask import request
from flask import json
import requests
#import logging
app = Flask(__name__)

#gunicorn_error_logger = logging.getLogger('gunicorn.error')
#app.logger.handlers.extend(gunicorn_error_logger.handlers)
#app.logger.setLevel(logging.DEBUG)
#app.logger.debug('this will show in the log')

storyId = 0

@app.route('/', methods=["GET","POST"])
def home():
	print("HOME")
	return jsonify({"Page":"Home"})
	
@app.route('/orsen', methods=["POST"])
def orsen():

	print(json.dumps(request.get_json()))
	requestJson = request.get_json()
	
	rawTextQuery = requestJson["inputs"][0]["rawInputs"][0]["query"]
	userId = requestJson["user"]["userId"]

	print(rawTextQuery + " ["+userId+"]")
	
	data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Hello! I am Orsen! What is your name?"+"POST"+""}],"noInputPrompts":[]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
	
	return jsonify(data)

if __name__ == '__main__':
    app.run(debug = True)