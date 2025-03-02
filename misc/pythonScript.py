import subprocess

def run_command(command):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "Error running command"

def get_git_context():
    """Collects and returns Git context as a formatted string."""
    context = []
    
    # Header
    context.append("===== Local Git Context =====")
    
    # Branches and commits
    context.append("\nBranches and Latest Commits:")
    branches = run_command("git branch -a").split("\n")
    branch_info = []
    for branch in branches:
        branch_name = branch.strip().replace("* ", "")
        latest_commit = run_command(f"git log -1 --oneline {branch_name}")
        branch_info.append(f"- {branch_name}: {latest_commit}")
    context.append('\n'.join(branch_info))
    
    # Uncommitted changes status
    context.append("\n\nUncommitted Changes: " + 
                  ('Yes' if run_command("git status --porcelain") else 'No'))
    
    # Remote information
    context.append("\n\nRemote Repositories:")
    context.append(run_command("git remote -v"))
    
    # Working directory status
    context.append("\n\nWorking Directory Status:")
    context.append(run_command("git status --short"))
    
    # Recent commit history
    context.append("\n\nRecent Commits for Each Branch:")
    for branch in branches:
        branch_name = branch.strip().replace("* ", "")
        context.append(f"\nBranch: {branch_name}")
        context.append(run_command(f"git log --oneline -n 5 {branch_name}"))
    
    # Detailed changes
    context.append("\n\nStaged Changes:")
    context.append(run_command("git diff --staged"))
    
    context.append("\n\nUncommitted Changes (Detailed):")
    context.append(run_command("git diff"))
    
    return '\n'.join(context)
