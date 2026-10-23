# WobbiesToolBox
A collection of Python utilities for automating my workflows, managing media, and reducing repetitive tasks.

`WobbiesToolBox` is a personal project built to consolidate scripts and tools into a single cli. Rather than maintaining isolated scripts for individual tasks, this project organizes functionality into modular command groups that can be extended as new needs arise in my day-to-day development.

The project also serves as an ongoing exploration of Python application structure, CLI design, process automation, and reusable tooling. It is apart of my portfolio to demonstrate my approach to scripting, automation, software organization, and development through a tool that I use and expand on, myself.

```cmd
C:\>wtb --help
usage: wobbiesToolbox [-h] [--dry-run] {dev,git,vod} ...

Personal development toolbox that make my life easier.

options:
  -h, --help     show this help message and exit
  --dry-run      See the command chain without executing it.

subcommands:
  {dev,git,vod}  Supported subcommands
    dev          Development commands
    git          Git commands
    vod          Vod tools
```

## Features

### Media & VOD Tools
Utilities for processing video recordings and automating media workflows using Python and FFmpeg.

- Video cutting and processing
- Automated media re-encoding
- Organized output for processed recordings
- Audio stream mixing for recordings with multiple tracks

### Github Utilities
A dedicated command group for Github related development tasks and workflow automation.
- Initialize an existing remote repository to a local folder and set `git config --local`
- Set's a local git config file

### Development Tools
Project scaffolding utilities for quickly creating consistent development environments.

- MVC directory structure generation
- Express.js project scaffolding
- Reusable project templates
- Dependency and configuration setup

## Design
This project is organized around independant command grouping, with each group responsible for its own functionality. This makes it easier to introduce new tools without turning the main CLI into a single script.

The current structure emphasizes:
- **Modularity**: Keeps related tools and command handlers seperated by responsibility.
- **Automation**: Reduces repetitive setup and media processing tasks.
- **Reusability**: Uses template and shared utilities instead of recreating common structures.
- **Maintainability**: Keeps the project extensible as the number of commands grows.

## Stack
- **Python**: CLI implementation, automation, and filesystem operations
- **FFmpeg**: Video and audio processing
- **Node.js / npm**: Tooling for JavaScript project scaffolding
- **Express.js**: WebApp scaffolding
- **Tailwind CSS**: Front-end styling for supported project templates

## Status
This project is under active development. Features, commands, and internal structure may change as the toolbox grows.

The focus is on building useful tools, improving the underlying architecture, and making recurring development tasks easier to reproduce.

## Disclaimer
This project is primarily developed for personal use and is published as a demonstration of my work and ongoing development. It is not intended to be a polished, production-ready product or a general purpose tool for public use.

Features, documentation, and error handling may be incomplete, and functionality may change without notice. Use at your own discretion; compatibility and reliability are not guaranteed.