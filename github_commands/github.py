import os
import time
import argparse
import subprocess
from dotenv import load_dotenv


load_dotenv()


class githubCommands:
  def __init__(self, args):
    self.command    = args.git_command
    self.remote_url = args.remote_url
    self.username   = args.username
    self.gh_personal = {
      "username": os.getenv("GH_PERSONAL_USERNAME"),
      "email":    os.getenv("GH_PERSONAL_EMAIL")
    }
    self.gh_school = {
      "username": os.getenv("GH_SCHOOL_USERNAME"),
      "email":    os.getenv("GH_SCHOOL_EMAIL")
    }
    self.gh_ssh_host = os.getenv("GH_SSH_CONFIG_HOST")

  # Replaces standard ssh command with ssh config host profile:
  #
  # .ssh/config
  #   Host github-personal
  #       Hostname github.com
  #       User ...
  #       ...
  #
  # git@github.com:user/repo -> git@github-personal:user/repo
  #
  def resolve_url(self):
    if self.remote_url.startswith("git@"):
      self.remote_url = self.remote_url.replace("@github.com", f"@{self.gh_ssh_host}")

  def resolve_branch(self, stdout):
    for line in stdout.splitlines():
      if line.strip().startswith("origin/HEAD ->"):
        branch = line.split("origin/HEAD -> origin/", 1)[1]
        print(f"[+] Switching to branch: {branch}")

        self.execute([["git", "switch", "-c", branch, "--track", f"origin/{branch}"]])
        return

  def resolve_username(self) -> str:
    if self.remote_url.startswith("git@"):
      self.resolve_url()
      return self.gh_personal["username"]
    elif self.remote_url.startswith("https://github.com"):
      return self.gh_school["username"]

    raise argparse.ArgumentTypeError(f"Unsupported Git URL format: '{self.remote_url}'.")

  def config(self) -> list:
    if self.username == self.gh_personal["username"]:
      return [
        ["git", "init"],
        ["git", "config", "--local", "user.name",  self.gh_personal["username"]],
        ["git", "config", "--local", "user.email", self.gh_personal["email"]],
        ["git", "remote", "add",     "origin",     self.remote_url]
      ]
    elif self.username == self.gh_school["username"]:
      return [
        ["git", "init"],
        ["git", "config", "--local", "user.name",  self.gh_school["username"]],
        ["git", "config", "--local", "user.email", self.gh_school["email"]],
        ["git", "remote", "set-url", "origin",     self.remote_url]
      ]

    raise argparse.ArgumentTypeError(f"Unknown Github username: '{self.username}'.")

  def init(self):
    config = self.config()
    self.execute(config)
    time.sleep(2)

    print("[+] Executing remote git operations.")
    self.execute([["git", "fetch", "origin"]])

    result = subprocess.run(["git", "branch", "-r"], check=True, capture_output=True, text=True)

    if "origin/HEAD" in result.stdout:
      self.resolve_branch(result.stdout)
    else:
      prompt = input("[!] No remote branch. Create 'origin/main' [y/N]?")
      if prompt.lower() in ("y", "yes"):
        create_commands = [
          ["git", "branch", "-M", "main"],
          ["git", "commit", "--allow-empty", "-m", "\"Initialize main\""],
          ["git", "push",   "-u", "origin", "main"]
        ]

        self.execute(create_commands)

  def execute(self, commands):
    for command in commands:
      print(f"[-] {' '.join(command)}")
      subprocess.run(command, check=True)

  def run(self):
    self.resolve_url()
    self.username = self.resolve_username() if self.username is None else self.username

    if self.command == "init":
      self.init()
    elif self.command == "config":
      config = self.config()
      self.execute(config)