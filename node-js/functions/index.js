// Copyright 2016, Google, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

'use strict';

process.env.DEBUG = 'actions-on-google:*';

const ActionsSdkApp = require('actions-on-google').ActionsSdkApp;
// const Eliza = require('elizabot');
const functions = require('firebase-functions');

// Intent constants
// const NO_INPUT_EVENT = 'no.input';
// const RAW_INTENT = 'raw.input';
// const INVOCATION_ARGUMENT = 'feelings';

let previousOrsenSpeech = '<NONE>';
const DEBUG_ID = 'Initial test#0 | ';

let items = ['Okay', 'Uh huh', 'I see', 'Ah', 'All right',
  "What's next?", 'Then what?', 'And then?', 'What else happens?',
  'Tell me more', 'What happens next?', 'And then what?',
  'What else?', 'Then what happens?'];

let end = ['Okay. Thanks for the story', 'Okay. Talk to you later', 'Thank you. Goodbye'];

/**
 * Handles the MAIN intent coming from Assistant, when the user first engages
 * with the app, expecting for an initial greeting from Eliza.
 */
const mainIntentHandler = (app) => {
  console.log('MAIN intent triggered.');
  console.log(DEBUG_ID + '-----------START------------');
  let inputPrompt = app.buildInputPrompt(false, 'Hello! I am Alice! Let us make a story, you start!');
  app.ask(inputPrompt);
  previousOrsenSpeech = 'Hello! I am Alice! Let us make a story, you start!';
  // const eliza = new Eliza();
  // app.ask(eliza.getInitial(), {elizaInstance: eliza});
};

/**
 * Handles the intent where the user invokes with a query to be handled by Eliza.
 *
 * This intent is triggered when the user invokes the Raw Input action by calling
 * Eliza and already sending an initial prompt.
 */
const noInputIntentHandler = (app) => {
  console.log('raw.input intent triggered.');

  let reprompt = ['Im sorry. What is it again?', 'Sorry, what was that?', 'bye'];

  app.ask(reprompt[Math.floor(Math.random() * reprompt.length)]);
};

/**
 * Handles the intent where the user returns a query to be handled by Eliza.
 *
 * This intent is triggered inside the dialogs when the user already has a
 * conversation going on with Eliza
 */
const textIntentHandler = (app) => {
  console.log('TEXT intent triggered.');
  let userReply = app.getRawInput();
  console.log('Initial test#0 | ' + previousOrsenSpeech + ' : ' + userReply);

  if (app.getDialogState().questionEndConvo === true) {
    if (userReply === 'yes' || userReply === 'sure' || userReply === 'Why not') {
      let ip = app.buildInputPrompt(false, 'Okay then, Let us make another story, you start! ');
      previousOrsenSpeech = 'Okay then, Let us make another story, you start!';
      app.ask(ip);
    } else {
      let finalResponse = end[Math.floor(Math.random() * end.length)];
      console.log(DEBUG_ID + '' + finalResponse);
      console.log(DEBUG_ID + '------------END------------');
      app.tell(finalResponse);
    }
  } else if (userReply === 'the end' || userReply === "that's all") {
    previousOrsenSpeech = 'Wow thanks for the story! Do you want to tell another one?';
    app.ask(previousOrsenSpeech, {questionEndConvo: true});
  } else {
    let reply = items[Math.floor(Math.random() * items.length)];
    let inputPrompt = app.buildInputPrompt(false, reply + '');
    previousOrsenSpeech = reply;
    app.ask(inputPrompt);
  }
};

/**
 * Handles the post request incoming from Assistant.
 */
exports.eliza = functions.https.onRequest((request, response) => {
  console.log('Incoming post request...');
  const app = new ActionsSdkApp({request, response});

  // Map that contains the intents and respective handlers to be used by the
  // actions client library
  const actionMap = new Map();

  /**
   * Configures the post request handler by setting the intent map to the
   * right functions.
   */
  actionMap.set(app.StandardIntents.MAIN, mainIntentHandler);
  actionMap.set(app.StandardIntents.NO_INPUT, noInputIntentHandler);
  actionMap.set(app.StandardIntents.TEXT, textIntentHandler);

  app.handleRequest(actionMap);
});
