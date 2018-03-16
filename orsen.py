from flask import Flask
from flask import jsonify
from flask import request
from flask import json
app = Flask(__name__)


@app.route('/', methods=["GET","POST"])
def home():
	return jsonify({"Page":"Home"})
	
@app.route('/orsen/', methods=["GET","POST"])
def orsen():

	#jsonData = request.data
	requestData = request.get_json()#json.loads(jsonData)
	
	#rawTextQuery = requestData["inputs"]["rawInputs"]["query"]

	if request.method == 'GET':
		data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Hello! I am Orsen! What is your name?"+"GET"+""}],"noInputPrompts":[]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
	elif request.method == 'POST':
		data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Hello! I am Orsen! What is your name?"+"POST"+""}],"noInputPrompts":[]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
	
	return jsonify(data)

if __name__ == '__main__':
    app.run()