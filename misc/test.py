import sys
from threading import Thread, Event
from transformers import StoppingCriteriaList
from lemonade.tools.serve import StopOnEvent
from lemonade.api import from_pretrained
from lemonade.tools.ort_genai.oga import OrtGenaiStreamer
from git_info.GitRepoParser import GitRepoParser
import subprocess
from pythonScript import get_git_context


def create_git_examples():
    """Create useful Git examples with explanations."""
    examples = [
        {
            "title": "Stashing Changes",
            "content": """# Stashing Changes in Git

## Basic Stashing

Stashing is useful when you need to switch branches but aren't ready to commit your changes.

```
git stash
```

This command saves your changes and reverts to the last commit. Your changes are stored in a "stash".

## Stashing with a Message

```
git stash save "work in progress for feature X"
```

Adding a descriptive message helps you identify the stash later.

## Including Untracked Files

By default, `git stash` only stores tracked files. To include untracked files:

```
git stash -u
```

or

```
git stash --include-untracked
```

## Listing Stashes

```
git stash list
```

This shows all your stashes.

## Applying a Stash

To apply the most recent stash and keep it in the stash list:

```
git stash apply
```

To apply a specific stash:

```
git stash apply stash@{2}
```

## Applying and Removing a Stash

To apply the most recent stash and remove it from the stash list:

```
git stash pop
```

## Dropping a Stash

To delete a stash:

```
git stash drop stash@{1}
```

## Clearing All Stashes

```
git stash clear
```

This removes all stashes.

## Creating a Branch from a Stash

```
git stash branch new-branch-name stash@{1}
```

This creates a new branch, applies the stash, and drops it if successful.
"""
        },
        {
            "title": "Undoing Changes",
            "content": """# Undoing Changes in Git

## Discarding Unstaged Changes

To discard changes in your working directory (dangerous - changes will be lost):

```
git restore <file>
```

Or with the older syntax:

```
git checkout -- <file>
```

## Unstaging Files

To remove a file from the staging area but keep your changes:

```
git restore --staged <file>
```

Or with the older syntax:

```
git reset HEAD <file>
```

## Amending the Last Commit

To add changes to the last commit or change the commit message:

```
git commit --amend
```

If you just want to change the commit message:

```
git commit --amend -m "New commit message"
```

## Reverting a Commit

To create a new commit that undoes changes from a previous commit:

```
git revert <commit-hash>
```

This is safe for public branches as it doesn't rewrite history.

## Resetting to a Previous Commit

To move the current branch to a previous commit (dangerous for shared branches):

Soft reset (keeps changes staged):
```
git reset --soft <commit-hash>
```

Mixed reset (default - keeps changes unstaged):
```
git reset <commit-hash>
```

Hard reset (discards all changes - dangerous):
```
git reset --hard <commit-hash>
```

## Recovering Lost Commits

If you've lost commits due to a reset, you can find them using:

```
git reflog
```

Then restore using:

```
git checkout <commit-hash>
```

or

```
git cherry-pick <commit-hash>
```
"""
        },
        {
            "title": "Branching and Merging",
            "content": """# Git Branching and Merging

## Creating a Branch

```
git branch <branch-name>
```

This creates a new branch but doesn't switch to it.

## Creating and Switching to a Branch

```
git checkout -b <branch-name>
```

Or with newer Git versions:

```
git switch -c <branch-name>
```

## Listing Branches

List local branches:
```
git branch
```

List all branches (including remote):
```
git branch -a
```

## Switching Branches

```
git checkout <branch-name>
```

Or with newer Git versions:

```
git switch <branch-name>
```

## Merging a Branch

First, switch to the target branch:
```
git checkout main
```

Then merge:
```
git merge <branch-name>
```

## Handling Merge Conflicts

When conflicts occur:
1. Files with conflicts will be marked in `git status`
2. Edit the files to resolve conflicts (look for `<<<<<<<`, `=======`, and `>>>>>>>` markers)
3. Add the resolved files:
   ```
   git add <resolved-file>
   ```
4. Complete the merge:
   ```
   git merge --continue
   ```
   or
   ```
   git commit
   ```

## Aborting a Merge

If you want to cancel a merge with conflicts:

```
git merge --abort
```

## Deleting a Branch

Delete a merged branch:
```
git branch -d <branch-name>
```

Force delete an unmerged branch:
```
git branch -D <branch-name>
```

## Viewing Branch History

```
git log --graph --oneline --all
```

This shows a graphical representation of your branch history.

## Rebasing a Branch

To reapply your branch commits on top of another branch:

```
git checkout <feature-branch>
git rebase main
```

This creates a cleaner history but should not be used on public branches.
"""
        },
        # Add more examples as needed
    ]
    
    return examples




def main():

    output_commands=create_git_examples()
    #print(output_commands)
    model, tokenizer = from_pretrained(
        "amd/Qwen1.5-7B-Chat-awq-g128-int4-asym-fp16-onnx-hybrid",
        recipe="oga-hybrid",
    )
    # repo_path: str = input("Enter the path to your repository: ").strip()
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
                # CURRENT REPOSITORY CONTEXT
        # {git_context}
        
        # THESE ARE ALL THE GIT COMMANDS you should refer to when answering. Answer only using the git commmands provided
        # {output_commands}

                # CURRENT REPOSITORY CONTEXT
        # {git_context}

        #         1: pull origin main
        # 2: branch
        # 3: status
        # 4: add .
        # 5: commit -m "Your commit message"
        # 6: push origin main
        # 7: clone <repository_url>
        # 8: log
        # 9: checkout -b <new_branch_name>
        # 10: fetch

        # OUTPUT THE NUMBER THAT CORRESPONDS TO THE QUESTION:
        # {user_message}
        
        total_message = f'''

        use the following context to cater to the user message correctly
        # CURRENT REPOSITORY CONTEXT
        {git_context}
        
        following user message:
        {user_message} 

        Strictly output only the git command in quotes and no other text!

       '''
        #        USER REQUEST
        #        first used the given git commands to find the appropriate command and then used the repository context to adjust the commands according to the user.
        # Strictly output only the git command in quotes and no other text!
        # Strictly output only the git command and no other text!
        # Generate the response in a thread and stream the result back
        # to the main thread
        # print(total_message)
        input_ids = tokenizer(total_message, return_tensors="pt").input_ids


        streamer = OrtGenaiStreamer(tokenizer)
        generation_kwargs = {
            "input_ids": input_ids,
            "streamer": streamer,
            "max_new_tokens": 400,
            "stopping_criteria": stopping_criteria,
        }

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