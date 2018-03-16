from flask import Flask
from flask import jsonify
from flask import request
from flask import json
app = Flask(__name__)

	
@app.route('/orsen/', methods=["GET","POST"])
def orsen():

	jsonData = request.data
	requestData = json.loads(jsonData)
	
	rawTextQuery = requestData["inputs"]["rawInputs"]["query"]

	data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Hello! I am Orsen! What is your name?"+rawTextQuery+""}],"noInputPrompts":[]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
		

	#except Exception as e:
		#flash(e)
		#return render_template("login.html", error = error)
	
	return jsonify(data)

if __name__ == '__main__':
    app.run()