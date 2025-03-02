import sys
from threading import Thread, Event
from transformers import StoppingCriteriaList
from lemonade.tools.serve import StopOnEvent
from lemonade.api import from_pretrained
from lemonade.tools.ort_genai.oga import OrtGenaiStreamer
from git_info.GitRepoParser import GitRepoParser
import subprocess
from pythonScript import get_git_context


# Add this function to format your git data and create a system message
def build_prompt(user_query: str, git_data: dict) -> str:
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
    git_context = get_git_context()
    while True:
        # Enable sending a signal into the generator thread to stop
        # the generation early
        stop_event = Event()

        stopping_criteria = StoppingCriteriaList([StopOnEvent(stop_event)])

        myObjectParser=GitRepoParser(r"C:\Users\aup\Desktop\temp\Hack_cu")
        GIT_CONTEXT_JSON=myObjectParser.get_attr()
        #print(myDict)
        # Prompt the user for an input message
        print()
        user_message = input("User: ")
        print()

        # Print a friendly message when we quit
        if user_message == "quit":
            print("System: Ok, bye!\n")
            break
        
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

        # Print each word to the screen as it arrives from the streamer
        # Allow the user to terminate the response with
        # a keyboard interrupt (ctrl+c)
        try:
            print("LLM: ", end="")
            for new_text in streamer:
                print(new_text, end="")
                sys.stdout.flush()
        except KeyboardInterrupt:
            stop_event.set()

        print()

        thread.join()
        # subprocess.run([ ], cwd=f"{repo_path}")


if __name__ == "__main__":
    main()