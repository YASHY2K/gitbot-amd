import sys
from threading import Thread, Event
from transformers import StoppingCriteriaList
from lemonade.tools.serve import StopOnEvent
from lemonade.api import from_pretrained
from lemonade.tools.ort_genai.oga import OrtGenaiStreamer
from git_info.GitRepoParser import GitRepoParser
import subprocess
from misc.pythonScript import get_git_context
import re


def build_prompt(user_query, git_data):
    return f"""<|start_header_id|>system<|end_header_id|>
    You are a Git repository assistant. I have access to the following repository information:
    {git_data}

    I will help analyze the repository, suggest Git commands, and explain concepts.
    Always respond with short, clear explanations and format commands in backticks.<|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    {user_query}<|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>"""


def main():
    model, tokenizer = from_pretrained(
        "amd/Qwen1.5-7B-Chat-awq-g128-int4-asym-fp16-onnx-hybrid",
        recipe="oga-hybrid",
    )
    # git_context = get_git_context()
    while True:
        stop_event = Event()
        stopping_criteria = StoppingCriteriaList([StopOnEvent(stop_event)])

        myObjectParser = GitRepoParser(r"C:\Users\aup\Desktop\temp\Hack_cu")
        GIT_CONTEXT_JSON = myObjectParser.get_attr()

        print()
        user_message = input("User: ")
        print()

        if user_message == "quit":
            print("System: Ok, bye!\n")
            break

        if user_message == "exec":
            for cmd in individual_commands:
                while True:
                    user_input = input(f"Do you want to run: `{cmd}`? [Y/N] ").strip().lower()
                    if user_input == 'y':
                        print(f"Running: {cmd}")
                        # Execute the command in the terminal
                        subprocess.run(cmd, shell=True, cwd=r"C:\Users\aup\Desktop\temp\Hack_cu")
                        break
                    elif user_input == 'n':
                        print(f"Skipping: {cmd}")
                        break
                    else:
                        print("Invalid input. Please enter Y or N.")
                    

        full_prompt = build_prompt(user_message, GIT_CONTEXT_JSON)
        input_ids = tokenizer(full_prompt, return_tensors="pt").input_ids

        streamer = OrtGenaiStreamer(tokenizer)
        generation_kwargs = {
            "input_ids": input_ids,
            "streamer": streamer,
            "max_new_tokens": 512,
            "temperature": 0.3,
            "top_p": 0.9,
            "stopping_criteria": stopping_criteria,
        }
        accumulated_text = ""
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        try:
            print("LLM: ", end="")
            for new_text in streamer:
                print(new_text, end="")
                accumulated_text += new_text
                sys.stdout.flush()
                #print(f"\nDebug: New text received: {new_text}")  # Debug statement
        except KeyboardInterrupt:
            stop_event.set()
            print("\nDebug: Generation interrupted by user.")  # Debug statement
        print()

        thread.join(timeout=10)  # Wait for 10 seconds max

        # Regex pattern to match each line inside the code block
        #pattern = r'```(?:\w+)?\n(.*?)\n```'
        #pattern = r'```(?:\w+)?\n(.*?)```' 
        pattern = r'```(?:\w+)?\n?(.*?)\n?```'

        # Find all matches using re.DOTALL to match across multiple lines
        matches = re.findall(pattern, accumulated_text, re.DOTALL)
        

        # Clean and process commands
        individual_commands = []
        for match in matches:
            # Strip each match and split by newlines
            commands = [cmd.strip() for cmd in match.split("\n") if cmd.strip()]
            
            for cmd in commands:
                # Remove inline comments (everything after #)
                cmd = re.sub(r'\s*#.*$', '', cmd).strip()
                
                if cmd:  
                    individual_commands.append(cmd)

        # Print cleaned commands to verify
        print("Cleaned commands:", individual_commands)

        # Now `individual_commands` will contain separate commands
                
        

if __name__ == "__main__":
    main()