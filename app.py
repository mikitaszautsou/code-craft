import json
from openai import OpenAI
import time
import subprocess

def query_ai(client, thread_id, assistant_id, message_content):
    """
    Sends a message to the AI, initiates a run, and waits for a completed response or executes a required action.
    """
    # Create a message in the thread as the user
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=message_content)

    # Initiate a run with the assistant
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id, instructions="")

    poll_interval = 1  # Polling interval in seconds
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        time.sleep(poll_interval)  # Wait before polling again
        if run_status.status == 'completed':
            break
        elif run_status.status == 'requires_action':
            terminal_tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
            parsed_command = json.loads(terminal_tool_call.function.arguments)['command']
            print(f'AI trying to execute: {parsed_command}')
            try:
                terminal_command_execution_output = subprocess.run([parsed_command], capture_output=True, text=True, shell=True)
                output = terminal_command_execution_output.stdout if terminal_command_execution_output.returncode == 0 else terminal_command_execution_output.stderr
            except Exception as e:
                output = str(e)
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=[
                    {
                        "tool_call_id": terminal_tool_call.id,
                        "output": output,
                    }
                ]
            )
    # Retrieve and return the last AI message in the thread, if available
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value if messages.data else "No response found."

def main():
    client = OpenAI()

    # Create an assistant with initial instructions and configuration
    assistant = client.beta.assistants.create(
        instructions="Initial system instruction",
        model="gpt-4-turbo-preview",
        tools=[{
            "type": "function",
            "function": {
                "name": "executeTerminalCommand",
                "description": "Executes a terminal command.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to be executed in the terminal."
                        },
                    },
                    "required": ["command"]
                }
            }
        }]
    )

    # Create a thread for interaction
    thread = client.beta.threads.create()
    
    while True:
        userInput = input('USER> ')
        ai_response = query_ai(client, thread.id, assistant.id, userInput)
        print(f'AI> {ai_response}')

if __name__ == "__main__":
    main()