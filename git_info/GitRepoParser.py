#!/usr/bin/env python3
import os
import json
from typing import Optional, Dict

class GitRepoParser:
    def __init__(self, repo_path: str) -> None:
        """
        Initialize the GitRepoParser with the given repository path.

        Args:
            repo_path: The file system path to the repository.
        """
        self.repo_path: str = repo_path
        self.git_dir: str = os.path.join(repo_path, '.git')
        self.git_data: Dict[str, str] = {}

    def parse(self) -> Optional[Dict[str, str]]:
        """
        Parse the .git directory and store the contents of each file.

        Returns:
            A dictionary mapping relative file paths to their contents, or None
            if the repository path or .git directory is invalid.
        """
        if not os.path.isdir(self.repo_path):
            print("Provided path is not a valid directory.")
            return None

        if not os.path.exists(self.git_dir):
            print(f"No .git directory found in {self.repo_path}")
            return None

        for root, _, files in os.walk(self.git_dir):
            for file in files:
                file_path: str = os.path.join(root, file)
                rel_path: str = os.path.relpath(file_path, self.git_dir)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content: str = f.read()
                except Exception as e:
                    content = f"Error reading file: {e}"
                self.git_data[rel_path] = content

        return self.git_data

    def dump_to_json(self, output_file: str = "git_state.json") -> None:
        """
        Dump the parsed git data to a JSON file.

        Args:
            output_file: The file name or path where the JSON data will be saved.
        """
        if not self.git_data:
            print("No data to dump. Make sure the .git directory was parsed successfully.")
            return

        try:
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump(self.git_data, f, indent=4)
            print(f"Parsed Git data has been dumped to '{output_file}'")
        except Exception as e:
            print(f"Failed to write JSON file: {e}")

if __name__ == '__main__':
    repo_path: str = input("Enter the path to your repository: ").strip()
    parser: GitRepoParser = GitRepoParser(repo_path)
    data: Optional[Dict[str, str]] = parser.parse()
    if data is not None:
        parser.dump_to_json()

# TODO
# 1. Instead of dumping it in a json file; write it to a in-memory store like redis
