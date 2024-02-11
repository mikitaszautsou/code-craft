from openai import OpenAI
import time

def query_ai(client, thread_id, assistant_id, message_content):
    """
    Sends a message to the AI and waits for a completed response.
    """
    # Create a message in the thread as the user
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_content
    )
    # print('Message:', message)

    # Initiate a run with the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=""
    )
    
    # Poll for the run's status until it is completed
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        time.sleep(5)  # Wait before polling again
        if run_status.status == 'completed':
            break

    # Retrieve the list of messages in the thread
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    
    # Safely access the first message's content, if available
    if messages.data and messages.data[0].content:
        return messages.data[0].content[0].text.value
    else:
        return "No response found."

def main():
    client = OpenAI()

    # Create an assistant with initial instructions and configuration
    assistant = client.beta.assistants.create(
        instructions="Initial system instruction",  # Corrected spelling
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
    
    # Query the AI and print the response
    answer = query_ai(client, thread.id, assistant.id, "hello")
    print(answer)

if __name__ == "__main__":
    main()
