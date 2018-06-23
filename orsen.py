from src.run import extract_info, new_world
from src.dialoguemanager.DialoguePlanner import *
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

storyId = -1
output = "Hello, I am ORSEN. Let's start."
retrieved = None
nIR = {"I can't hear you", "Sorry. What did you say again?", "Okay"}
tts = "Sorry. What did you say again?"
dt = "Sorry. What did you say again?"

focus = None

manwal_kawnt = 0
MAKSIMUM_KAWNT = 5
endstory = False

def main_intent():
	return None


@app.route('/', methods=["GET","POST"])
def home():
	print("HOME")
	return jsonify({"Page":"Home"})
	
@app.route('/orsen', methods=["POST"])
def orsen():
	global manwal_kawnt, storyId, endstory
	
	#print(json.dumps(request.get_json()))
	requestJson = request.get_json()
	
	focus = requestJson["inputs"][0]#["rawInputs"][0]["query"]
	#print(focus["intent"])
	
	#When the app invocation starts, create storyid and greet the user and reset reprompt count
	if focus["intent"] == "actions.intent.MAIN":
		storyId = storyId + 1
		print("STORY ID ",storyId)
		new_world(storyId)
		#reset reprompt count
		manwal_kawnt = 0
		#greet user (app.ask)
		data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Hi! Let's create a story. You start"}],"noInputPrompts":[{"textToSpeech":tts,"displayText":dt}]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
	elif focus["intent"] == "actions.intent.GIVE_IDEA_ORSEN":
		data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Okay, I will give you a hint"}],"noInputPrompts":[{"textToSpeech":tts,"displayText":dt}]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
	
	#When there is no input: ask the user (prompt from model) until maximum count is reached 
	elif focus["intent"] == "actions.intent.NO_INPUT":
		#increment reprompt count
		manwal_kawnt = manwal_kawnt + 1
		#app termination when maximum reprompt count is reached
		if manwal_kawnt == MAKSIMUM_KAWNT:
			data = {"expectUserResponse": False, "finalResponse": {"speechResponse": {"textToSpeech": "Okay. Goodbye"}}}
		#reprompt user
		else:
			#get the reprompt
			retrieved = retrieve_output("", storyId)
			
			if retrieved.type_num == MOVE_HINT:
				extract_info(retrieved.get_string_response())
	
			output_reply = retrieved.get_string_response()
			#reprompt user
			data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":""+output_reply+""}],"noInputPrompts":[{"textToSpeech":tts,"displayText":dt}]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	#When there is input, simply pass to model and get reply
	else:
		rawTextQuery = requestJson["inputs"][0]["rawInputs"][0]["query"]
	
		manwal_kawnt =0
		userId = requestJson["user"]["userId"]
		data = {}
	
		#print(rawTextQuery + " ["+userId+"]")

		if endstory:
			rawTextQuery = requestJson["inputs"][0]["rawInputs"][0]["query"]
			#If user wants to create another story, create new story and reset reprompt counts
			if rawTextQuery == "yes" or rawTextQuery == "yes." or rawTextQuery == "sure" or rawTextQuery == "sure." or rawTextQuery == "yeah" or rawTextQuery == "yeah.":
				data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Okay then, Let's create a story. You start"}],"noInputPrompts":[{"textToSpeech":tts,"displayText":dt}]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
				manwal_kawnt = 0
				storyId = storyId + 1
				print("STORY ID ",storyId)
				new_world(storyId)
				
			#If the user wants to end anyway, 
			else:
				data = {"expectUserResponse": False, "finalResponse": {"speechResponse": {"textToSpeech": "Thank you. Goodbye"}}}
			endstory = False
				
		#the user may end the conversation
		elif rawTextQuery == "bye" or rawTextQuery == "the end" or rawTextQuery == "the end.":
			data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":"Wow. Thanks for the story. Do you want to create another one?"}],"noInputPrompts":[{"textToSpeech":tts,"displayText":dt}]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
			endstory = True
		else:
	
			extract_info(rawTextQuery)

			#dialogue
			retrieved = retrieve_output(rawTextQuery, storyId)

			if retrieved.type_num == MOVE_HINT:
				extract_info(retrieved.get_string_response())
	
			output_reply = retrieved.get_string_response()
			data = {"conversationToken":"{\"state\":null,\"data\":{}}","expectUserResponse":True,"expectedInputs":[{"inputPrompt":{"initialPrompts":[{"textToSpeech":""+output_reply+""}],"noInputPrompts":[{"textToSpeech":tts,"displayText":dt}]},"possibleIntents":[{"intent":"actions.intent.TEXT"}]}]}
	
			print("I: ", rawTextQuery)
			print("O: ", output_reply)
	
	
	#if expectedUserResponse is false, change storyId
	
	return jsonify(data)

if __name__ == '__main__':
    app.run(debug = True)