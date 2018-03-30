import src.run
from src.dialoguemanager.DialoguePlanner import retrieve_output
from flask import Flask
from flask import jsonify
from flask import request
from flask import json
import requests
import re
#import logging
app = Flask(__name__)

#gunicorn_error_logger = logging.getLogger('gunicorn.error')
#app.logger.handlers.extend(gunicorn_error_logger.handlers)
#app.logger.setLevel(logging.DEBUG)
#app.logger.debug('this will show in the log')

storyId = "0"

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
	data = {}
	
	print(rawTextQuery + " ["+userId+"]")
	
	if re.search('or sehn', rawTextQuery, re.IGNORECASE):
	
		data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Hi! Let's create a story. You start"}],"noInputPrompts":[]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
	else:
		output_reply = retrieve_output(rawTextQuery, storyId).get_string_response()
		data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":""+output_reply+""}],"noInputPrompts":[]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
		print("ORSEN CONTROLLER received output")
		print(output_reply)
	
	
	#if expectedUserResponse is false, change storyId
	
	return jsonify(data)

if __name__ == '__main__':
    app.run(debug = True)