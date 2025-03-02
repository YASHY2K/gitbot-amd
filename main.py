import re
import sys
from pathlib import Path
from threading import Thread, Event
from typing import Any, Generator, List, Tuple
from subprocess import run as subprocess_run

from transformers import StoppingCriteriaList, PreTrainedTokenizer, PreTrainedModel
from lemonade.tools.serve import StopOnEvent
from lemonade.api import from_pretrained
from lemonade.tools.ort_genai.oga import OrtGenaiStreamer
from git_info.GitRepoParser import GitRepoParser
from misc.pythonScript import get_git_context

# Constants
path: str = str(input("Enter Repo path: "))
# REPO_PATH = Path(r"C:\Users\aup\Desktop\temp\Hack_cu")
REPO_PATH = Path(path)
COMMAND_PATTERN = re.compile(r'```(?:\w+)?\n?(.*?)\n?```', re.DOTALL)
DEFAULT_GENERATION_CONFIG = {
    "max_new_tokens": 512,
    "temperature": 0.3,
    "top_p": 0.9,
}

def build_prompt(user_query: str, git_data: str) -> str:
    """Constructs the formatted prompt for the LLM."""
    return f"""<|start_header_id|>system<|end_header_id|>
    You are a Git repository assistant. I have access to the following repository information:
    {git_data}

    I will help analyze the repository, suggest Git commands, and explain concepts.
    Always respond with short, clear explanations and format commands in backticks.<|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    {user_query}<|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>"""

def load_model() -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Loads and returns the pretrained model and tokenizer."""
    return from_pretrained(
        "amd/Qwen1.5-7B-Chat-awq-g128-int4-asym-fp16-onnx-hybrid",
        recipe="oga-hybrid",
    )

def process_commands(commands: List[str], repo_path: Path) -> None:
    """Handles interactive command execution with user confirmation."""
    for cmd in commands:
        while True:
            user_input = input(f"Do you want to run: `{cmd}`? [Y/N] ").strip().lower()
            if user_input == 'y':
                print(f"Running: {cmd}")
                subprocess_run(cmd, shell=True, cwd=repo_path)
                break
            elif user_input == 'n':
                print(f"Skipping: {cmd}")
                break
            print("Invalid input. Please enter Y or N.")

def extract_commands(text: str) -> List[str]:
    """Extracts and cleans Git commands from LLM response text."""
    matches = COMMAND_PATTERN.findall(text)
    commands: List[str] = []
    
    for match in matches:
        for line in match.split("\n"):
            cleaned_line = re.sub(r'\s*#.*$', '', line.strip())
            if cleaned_line:
                commands.append(cleaned_line)
    
    return commands

def generate_response(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    prompt: str,
    stop_event: Event,
    streamer: OrtGenaiStreamer
) -> str:
    """Generates LLM response with streaming output."""
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    stopping_criteria = StoppingCriteriaList([StopOnEvent(stop_event)])

    generation_args = {
        "input_ids": input_ids,
        "streamer": streamer,
        "stopping_criteria": stopping_criteria,
        **DEFAULT_GENERATION_CONFIG
    }

    thread = Thread(target=model.generate, kwargs=generation_args)
    thread.start()

    accumulated_text = ""
    try:
        print("LLM: ", end="")
        for new_text in streamer:
            print(new_text, end="")
            accumulated_text += new_text
            sys.stdout.flush()
    except KeyboardInterrupt:
        stop_event.set()
        print("\nGeneration interrupted by user.")
    
    thread.join(timeout=10)
    return accumulated_text

def main() -> None:
    """Main execution loop for the Git assistant."""
    model, tokenizer = load_model()
    git_parser = GitRepoParser(REPO_PATH)
    
    while True:
        git_context = git_parser.get_attr()
        user_message = input("\nUser: ").strip()
        print()

        if user_message.lower() == "quit":
            print("System: Ok, bye!\n")
            return

        if user_message.lower() == "exec":
            print("System: No commands to execute. Please ask a question first.\n")
            continue

        prompt = build_prompt(user_message, git_context)
        streamer = OrtGenaiStreamer(tokenizer)
        stop_event = Event()

        response_text = generate_response(model, tokenizer, prompt, stop_event, streamer)
        commands = extract_commands(response_text)
        
        if commands:
            print("\nDetected commands:", commands)
            process_commands(commands, REPO_PATH)

if __name__ == "__main__":
    main()