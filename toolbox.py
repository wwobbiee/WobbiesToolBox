# Wobbie's Toolbox
# A wrapper for a bunch of programs to help me with some redunant things.
import sys
import argparse

from vod_commands import vodTools
from github_commands import githubCommands
from development_commands import devTools


def main(argv=None):
  parser = argparse.ArgumentParser(
    prog="wobbiesToolbox",
    description="Personal development toolbox that make my life easier."
  )
  parser.add_argument("--dry-run", action="store_true", help="See the command chain without executing it.")
  subparsers = parser.add_subparsers(title="subcommands", dest="command", help="Supported subcommands")

  # Development tools
  dev_parser = subparsers.add_parser("dev", help="Development commands", description="Setup environments with MVC structures, creates files and 'workspaces' to start developing applications.")
  dev_subparser = dev_parser.add_subparsers(dest="dev_command")
  dev_mvc       = dev_subparser.add_parser("mvc",
                                           help="Scaffold MVC structure",
                                           description="Scaffold proper MVC folder structure with empty files."
                                          )
  dev_express   = dev_subparser.add_parser("express",
                                           help="Scaffold express server",
                                           description="Scaffolds express server with proper MVC, template files, tailwind, & npm packages."
                                          )

  for d_parser in (dev_mvc, dev_express):
    d_parser.add_argument("path", nargs="?", default=".", help="Specify a target directory (default: current working directory).")

  # Github
  git_parser        = subparsers.add_parser("git", help="Git commands", description="Git command helpers to configure a local directory to an existing repository.")
  git_subparser     = git_parser.add_subparsers(dest="git_command")
  git_init_parser   = git_subparser.add_parser("init",
                                                help="Initialize and configure a repository",
                                                description="Configure a repository with 'git config --local' and fetch HEAD. If there is no HEAD at origin, an empty branch named 'main' will be created."
                                              )
  git_config_parser = git_subparser.add_parser("config",
                                               help="Configure a repository",
                                               description="Configure a repository with 'git config --local'."
                                              )
  for gh_parser in (git_init_parser, git_config_parser):
    gh_parser.add_argument("remote_url", help="The remote github repository URL.")
    gh_parser.add_argument("-u", "--username", help="Github account to configure.")

  # VOD tools
  vod_parser        = subparsers.add_parser("vod", help="Vod tools", description="Tools to re-encode, cut and merge VOD's at timestamp, extract & normalize audio for export/import for video editing. You must have 'ffmpeg' and 'ffprobe' installed.")
  vod_subparser     = vod_parser.add_subparsers(dest="vod_command")
  vod_encode_parser = vod_subparser.add_parser("encode",
                                               help="Reencode a video to mp4 format",
                                               description="Reencode's an input video to output mp4 format"
                                              )
  vod_cut_parser    = vod_subparser.add_parser("cut",
                                               help="Cut and delete a section within a video and merge into one",
                                               description="Cut at start timestamp and remerges VOD at end timestamp"
                                              )
  vod_fix_parser    = vod_subparser.add_parser("fix",
                                               help="Fix a broken mkv corrupted video",
                                               description="Fixes an .mkv VOD that had been interrupted while recording. Outputs to directory ./fixed_vods_"
                                              )
  vod_edit_parser   = vod_subparser.add_parser("edit",
                                               help="Prepare a VOD for editing",
                                               description="Reencodes the VOD to mp4 format and normalizes the audio files."
                                              )
  vod_normalize_parser = vod_subparser.add_parser("normalize",
                                                  help="Normalize the audio of a video",
                                                  description="Normalizes the audio of a video, creates an audio file for import"
                                                 )
  for vod_tools in (vod_encode_parser, vod_cut_parser, vod_fix_parser, vod_normalize_parser, vod_edit_parser):
    vod_tools.add_argument("VOD", help="The input video")

  vod_cut_parser.add_argument("--from",    dest="vod_from",   help="The timestamp to cut from HH:MM:SS", required=True)
  vod_cut_parser.add_argument("--to",      dest="vod_to",     help="The timestamp to cut to HH:MM:SS",   required=True)
  vod_cut_parser.add_argument("--no-reenc",dest="no_reenc",   help="No reencoding the video (omits frame level precision.)", action="store_true")
  vod_fix_parser.add_argument("--out-dir", dest="output_dir", help="The output directory to save the remuxed videos to",     default="./fixed_vods_")

  args = parser.parse_args(argv)

  if (args.dry_run):
    print("===DRY RUN===")
    print(args)
    sys.exit(0)

  if args.command == "git":
    gh = githubCommands(args)
    gh.run()
  elif args.command == "vod":
    vod = vodTools(args)
    vod.run()
  elif args.command == "dev":
    dev = devTools(args)
    dev.run()



if __name__ == "__main__":
  main()