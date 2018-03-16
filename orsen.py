from flask import Flask
from flask import jsonify
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
	
    try:
	
        if request.method == "POST":
		
            rawInput = request.form['inputs']['rawInputs']['query']
            #attempted_password = request.form['password']

            #flash(attempted_username)
            #flash(attempted_password)

            #if attempted_username == "admin" and attempted_password == "password":
            #    return redirect(url_for('dashboard'))
				
            #else:
            #    error = "Invalid credentials. Try Again."

        #return render_template("login.html", error = error)
			data = {
				"conversationToken": "{'state':null,'data':{}}",
				"expectUserResponse": True,
				"expectedInputs": [{
					"inputPrompt": {
						"initialPrompts": {	
							"textToSpeech": "Hello! I am Orsen! What is your name?",
							"displayText": "Hello! I am Orsen! What is your name?" + rawInput + ""
						}
					},
					"possibleIntents": [{
						"intent": "actions.intent.TEXT"
					}]
				}]
			}

    except Exception as e:
        #flash(e)
        #return render_template("login.html", error = error)

	return jsonify(data)
		

if __name__ == '__main__':
    app.run()