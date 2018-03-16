from flask import Flask
from flask import jsonify
from flask import request
from flask import json
#import logging
app = Flask(__name__)

#gunicorn_error_logger = logging.getLogger('gunicorn.error')
#app.logger.handlers.extend(gunicorn_error_logger.handlers)
#app.logger.setLevel(logging.DEBUG)
#app.logger.debug('this will show in the log')


@app.route('/', methods=["GET","POST"])
def home():
	return jsonify({"Page":"Home"})
	
@app.route('/orsen/', methods=["GET","POST"])
def orsen():

	#jsonData = request.data
	#if request.is_json:
	requestData = request.get_data()
	helllomehn = {}
	
	
	
	#if json.dumps(requestData) == "true":
	#	hellomehn = request.json
	
	#rawTextQuery = requestData["inputs"]["rawInputs"]["query"]

	if request.method == 'GET':
		data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Hello! I am Orsen! What is your name?"+requestData+""}],"noInputPrompts":[]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
	elif request.method == 'POST':
		data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Hello! I am Orsen! What is your name?"+"POST"+""}],"noInputPrompts":[]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
	
	return jsonify(data)

if __name__ == '__main__':
    app.run()