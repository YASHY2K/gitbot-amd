import subprocess

def run_command(command):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "Error running command"

print("===== Local Git Context =====")

# Get current branch
print(f"Current Branch: {run_command('git rev-parse --abbrev-ref HEAD')}")

# Get latest commit
print(f"Latest Commit: {run_command('git log -1 --oneline')}")

# Check for uncommitted changes
uncommitted_changes = run_command("git status --porcelain")
print(f"Uncommitted Changes: {'Yes' if uncommitted_changes else 'No'}")

# Get remote repository information
print("\nRemote Repositories:")
print(run_command("git remote -v"))

# Get working directory status
print("\nWorking Directory Status:")
print(run_command("git status --short"))

# Get recent commit history
print("\nRecent Commit History:")
print(run_command("git log --oneline -n 5"))

# Get staged changes
print("\nStaged Changes:")
print(run_command("git diff --staged"))

# Get uncommitted changes
print("\nUncommitted Changes (Detailed):")
print(run_command("git diff"))
