import json
# from openai import OpenAI
import time
import anthropic
import ast
import subprocess


def custom_decoder(string):
    return string.replace('\\n', '\n')

def parse_array(string):
    # Find the positions of the first, second, third, and last occurrence of "'"
    first_quote = string.find("'")
    second_quote = string.find("'", first_quote + 1)
    third_quote = string.find("'", second_quote + 1)
    last_quote = string.rfind("'")

    # Extract the substrings using string slicing
    first_part = string[first_quote + 1: second_quote]
    second_part = string[third_quote + 1: last_quote]
    print('STRING', string)
    print('FP', first_part)
    print('SP', second_part)
    # Create and return the parsed array
    return [first_part, second_part]

def query_ai(client, messages):
    print('messages', messages)
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system="you are code assistent, you should answer with JSON arrays which represents action, you have the following options\n['exec', 'command line to execute, for example -ls'] // execute some action on user's pc\n['say', 'to say something to user']\n\n    ",
        messages=messages
    )
    print(message)
    messages.append({
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": message.content[0].text
                }
            ]
    })
    parsed_message = parse_array(message.content[0].text)
    print('parsed message', parsed_message)
    return parsed_message
def main():

    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        # api_key="my_api_key",
    )
    messages = []
    while True:
        userInput = input('USER> ')
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"['user', '{userInput}']"
                }
            ]
        })
        ai_turn_ended = False
        ai_message = query_ai(client, messages)
        while not ai_turn_ended:
            if ai_message[0] == 'say':
                print(f'AI> {ai_message[1]}')
                break
            elif ai_message[0] == 'exec':
                terminal_command_execution_output = subprocess.run([ai_message[1]], capture_output=True, text=True, shell=True)
                output = terminal_command_execution_output.stdout if terminal_command_execution_output.returncode == 0 else terminal_command_execution_output.stderr
                print(f'TERMINAL> {output}')
                messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"['system', '{output}']"
                            }
                        ]
                })
                ai_message = query_ai(client, messages)
if __name__ == "__main__":
    main()