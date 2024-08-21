import json
from datetime import datetime
import re

#returns a dict with the interesting value from the prompt
@staticmethod
def get_elts_from_prompt_get_response(bedrock_prompt_get_response):
    response = dict()
    response["temperature"] = bedrock_prompt_get_response["variants"][0]["inferenceConfiguration"]["text"]["temperature"]
    response["topP"] = bedrock_prompt_get_response["variants"][0]["inferenceConfiguration"]["text"]["topP"]
    response["maxTokens"] = bedrock_prompt_get_response["variants"][0]["inferenceConfiguration"]["text"]["maxTokens"]
    response["modelId"] = bedrock_prompt_get_response["variants"][0]["modelId"]
    response["prompt_text"] = bedrock_prompt_get_response["variants"][0]["templateConfiguration"]["text"]["text"]
    response["input_variable_dict"] = bedrock_prompt_get_response["variants"][0]["templateConfiguration"]["text"]["inputVariables"]
    return response

#load jsonlines transcripts file from ../generated/transcripts/transcripts.jsonl
@staticmethod
def load_jsonlines_file(file_path):
    transcripts = []
    with open(file_path, 'r') as f:
        for line in f:
            transcripts.append(json.loads(line))
    return transcripts

#extract answer from tags
@staticmethod
def extract_answer(text, tag="answer"):
    pattern = f'<{tag}>(.*?)</{tag}>'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None

#call Bedrock converse apis
@staticmethod
def converse_api_call_no_tool(user_input, 
                              system_prompt, 
                              bedrock_client, 
                              conversation_history= [], 
                              prefill="", 
                              model_id="anthropic.claude-3-haiku-20240307-v1:0", 
                              temperature=0, 
                              top_p=1, 
                              max_tokens=4096,
                              json_check=False,
                              debug=False):

    message = []

    #check if conversation history is provided. if so, add it to the message, else start a new conversation
    if conversation_history:
        message = conversation_history

    user_message = {
            "role": "user",
            "content": [
                { "text": json.dumps(user_input) } 
            ],
        }

    message.append(user_message)

    #add prefill if provided
    if prefill != "": 
        assistant_prefill_message = {
            "role": "assistant",
            "content": [
                { "text": prefill }
            ],
        }
        message.append(assistant_prefill_message)

    #converse api call
    response = bedrock_client.converse(
        modelId=model_id,
        messages=message,
        inferenceConfig={
            "maxTokens": max_tokens,
            "temperature": temperature,
            "topP": top_p
        },
        system=[{"text": json.dumps(system_prompt)}]
    )

    #extract message
    response_message = response['output']['message']

    #extract the model response and add prefill
    response_text = prefill + response_message["content"][0]["text"]

    #print output if debug is True.
    if debug:
        print(f"Raw response:{response}")
        print(f"Prefill combined response:{response_text}")

    #if response is in answer tag, just retrieve that info
    if "<answer>" in response_text:
        response_text = extract_answer(response_text)
        if debug:
            print(f"Extracted answer:{response_text}")

    #if json_check is True, we check that the json output is correctly formatted
    if json_check:
        
        try:
            response_text = json.loads(response_text.replace("\n", ""))
        except:
            #boolean used to stop the loop
            fixed = False
            #max 3 retries
            counter = 3
            
            while ((not fixed) and (counter > 0)):
                print(f"converse_api_call_no_tool - Attempting to fix malformed JSON, retries left:{counter}")
                #we try to fix the json if it is not valid
                json_fix_system_prompt = """You are an expert at formatting JSON strings."""
                json_fix_prompt_template = """ 
                Your task is to fix the following JSON string in <erroneous_json> tag and format it into a valid JSON object. 
                <erroneous_json>{json}</erroneous_json>
                Skip the preamble, return only the JSON object and nothing else.
                """
                json_fix_prompt = json_fix_prompt_template.format(json=response_text)

                #formatting the message
                fix_message = []
                fix_prompt_user = {
                        "role": "user",
                        "content": [
                            { "text": json.dumps(json_fix_prompt) } 
                        ],
                    }
                fix_message.append(fix_prompt_user)

                fix_response = bedrock_client.converse(
                    modelId=model_id,
                    messages=fix_message,
                    inferenceConfig={
                        "maxTokens": 4096,
                        "temperature": 0,
                        "topP": 0.8
                    },
                    system=[{"text": json.dumps(json_fix_system_prompt)}]
                )

                #extract message
                fix_response_text = fix_response['output']['message']["content"][0]["text"]

                try:
                    response_text = json.loads(fix_response_text.replace("\n", ""))
                    fixed = True
                except:
                    print(f"converse_api_call_no_tool - Failed to fix JSON string: {fix_response}")
                    counter = counter - 1
                    response_text = None

    return response_text
        

#retrieve prompt details and call the converse_api_call_no_tool method
@staticmethod
def retrieve_prompt_and_inference(prompt_id, bedrock_agent_client, transcript):
    #retrieve prompt details from Bedrock
    bedrock_prompt = bedrock_agent_client.get_prompt(
            promptIdentifier=prompt_id
        )

    #parse the response and retrieve the elements we need for later.
    prompt_dict = llm_utils.get_elts_from_prompt_get_response(bedrock_prompt)

    #format prompt with transcript
    prompt_text = prompt_dict["prompt_text"].format(transcript=transcript)

    #generate response from LLM
    bedrock_runtime = boto3.client(service_name='bedrock-runtime')

    response= converse_api_call_no_tool(prompt_text, 
                            "", 
                            bedrock_runtime, 
                            conversation_history= [], 
                            prefill="",
                            model_id=prompt_dict["modelId"], 
                            temperature=prompt_dict["temperature"], 
                            top_p=prompt_dict["topP"], 
                            max_tokens=prompt_dict["maxTokens"],
                            debug=False)
    return response

# Persist the dictionary to a JSON file
@staticmethod
def save_dict_to_json(dictionary, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(dictionary, json_file)

# Load the dictionary from a JSON file
@staticmethod
def load_dict_from_json(file_path):
    with open(file_path, 'r') as json_file:
        dictionary = json.load(json_file)
    return dictionary