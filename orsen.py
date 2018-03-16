from flask import Flask
from flask import jsonify
from flask import request
app = Flask(__name__)

@app.route('/')
def hello_world():
	
	data = {
		"conversationToken": "{'state':null,'data':{}}",
		"expectUserResponse": True,
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
	
	
@app.route('/orsen/', methods=["GET","POST"])
def orsen():

	error = ''
	#data = {"result":"Method is get"}
	data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Hello! I am Orsen! What is your name?"}],"noInputPrompts":[]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	'''
			"conversationToken": "{'state':null,'data':{}}",
			"expectUserResponse": True,
			"expectedInputs": [{
				"inputPrompt": {
					"initialPrompts": {	
						#"richInitialPrompt":{
							"items": [{
								"simpleResponse": {
									"textToSpeech": "Howdy! I can tell you fun facts about almost any number, like 42. What do you have in mind?",
									"displayText": "Howdy! I can tell you fun facts about almost any number. What do you have in mind?"
								}
							}],
							"suggestions": []
						},
						#"noInputPrompts":[{
						
						#}]
						#"textToSpeech": "Hello! I am Orsen! What is your name?",
						#"displayText": "Hello! I am Orsen! What is your name?" + "rawInput" + ""
					}
				},
				"possibleIntents": [{
					"intent": "actions.intent.TEXT"
				}]
			}]
		}
	
	#try:
	if request.method == "POST":		
		rawInput = request.form['inputs']['rawInputs']['query']
		
		data = {
			"conversationToken": "{'state':null,'data':{}}",
			"expectUserResponse": True,
			"expectedInputs": [{
				#"inputPrompt": {
				#	"initialPrompts": {	
				#		"textToSpeech": "Hello! I am Orsen! What is your name?",
				#		"displayText": "Hello! I am Orsen! What is your name?" + rawInput + ""
				#	}
				#},
				#"possibleIntents": [{
				#	"intent": "actions.intent.TEXT"
				#}]
			}]
		}

	#except Exception as e:
		#flash(e)
		#return render_template("login.html", error = error)
	'''
	return jsonify(data)

if __name__ == '__main__':
    app.run()