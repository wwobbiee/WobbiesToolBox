import re
import os
import shutil
import tempfile
import subprocess

from pathlib import Path


class cutTools:
  # Cuts a section from a video
  def __init__(self, args):
    self.time_from   = args.vod_from
    self.time_to     = args.vod_to
    self.vod         = Path(args.VOD)
    self.no_reenc    = args.no_reenc
    self.tempdir     = None
    self.output_file = None
    self.from_sec    = None
    self.to_sec      = None

  def parse_time(self, value) -> float:
    """_summary_
    Accepts:
        5         -> 5 seconds
        30s       -> 30 seconds
        2m3s      -> 123 seconds
        1h        -> 3600 seconds
        1h2m3s    -> 3723 seconds

        00:30     -> 30 seconds
        05:30     -> 330 seconds
        00:05:30  -> 330 seconds
    """
    value = str(value).strip().lower()
    if not value:
      raise ValueError("Time cannot be empty.")

    if ":" in value:
      parts = value.split(":")

      if len(parts) == 2:
        # MM:SS
        m, s = parts
        try:
          m = int(m)
          s = int(s)
        except ValueError:
          raise ValueError(f"Invalid time format: {value}")

        if m < 0 or not 0 <= s < 60:
          raise ValueError(f"Invalid time format: {value}")

        return m * 60 + s
      elif len(parts) == 3:
        # HH:MM:SS
        h, m, s = parts
        try:
          h = int(h)
          m = int(m)
          s = int(s)
        except ValueError:
          raise ValueError(f"Invalid time format: {value}")

        if h < 0 or not 0 <= m or not 0 <= s < 60:
          raise ValueError(f"Invalid time format: {value}")

        return h * 3600 + m * 60 + s

      raise ValueError(f"Invalid time format: {value}")

    unit_pattern = re.compile(r"^(?:(\d+(?:\.\d+)?)h)?(?:(\d+(?:\.\d+)?)m)?(?:(\d+(?:\.\d+)?)s)?$")
    match = unit_pattern.fullmatch(value)
    if match and any(match.groups()):
      h = float(match.group(1) or 0) 
      m = float(match.group(2) or 0)
      s = float(match.group(3) or 0)

      return h * 3600 + m * 60 + s
  
    try:
      s = float(value)
      if s < 0:
        raise ValueError

      return s
    except ValueError:
      raise ValueError(f"Invalid time format: {value}")
  
  def format_time(self, sec) -> str:
    s = float(sec)
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    s = s % 60
    if s.is_integer():
      s = int(s)

    return f"{h:02d}:{m:02d}:{s:02}"

  def check_params(self) -> None:
    if not self.vod.exists():
      raise ValueError(f"Input file not found.")

    self.from_sec = self.parse_time(self.time_from)
    self.to_sec   = self.parse_time(self.time_to)

    if self.from_sec >= self.to_sec:
      raise ValueError("-- from must be earlier than --to")

    self.time_from = self.format_time(self.from_sec)
    self.time_to   = self.format_time(self.to_sec)

  def create_output(self):
    base = self.vod.stem
    ext = self.vod.suffix

    safe_from = self.time_from.replace(":", "-")
    safe_to   = self.time_to.replace(":", "-")

    self.output_file = self.vod.with_name(f"{base}_cut_{safe_from}_to_{safe_to}{ext}")

    if self.output_file.exists():
      prompt = input(f"[!] Output exists ({self.output_file}). Overwrite [y/N]? ").lower()
      if prompt not in ("y", "yes"):
        raise RuntimeError("Cancelled operation.")
      self.output_file.unlink()

    self.tempdir = tempfile.mkdtemp(prefix="ffmpeg_cut_")

    part1 = os.path.join(self.tempdir, f"part1{ext}")
    part2 = os.path.join(self.tempdir, f"part2{ext}")
    list_file = os.path.join(self.tempdir, "files.txt")

    return part1, part2, list_file

  def cut(self):
    part1, part2, list_file = self.create_output()

    if self.no_reenc:
      reenc_command = ["-c", "copy"]
    else:
      reenc_command = ["-c:v", "libx264", "-c:a", "aac"]

    try:
      print("[-] Creating first segment...")
      self.execute([
        "ffmpeg", "-y",
        "-i", str(self.vod),
        "-to", self.time_from,
        *reenc_command,
        part1
      ])

      print("[-] Creating second segment...")
      self.execute([
        "ffmpeg", "-y",
        "-i", str(self.vod),
        "-ss", self.time_to,
        *reenc_command,
        part2
      ])

      with open(list_file, "w", encoding="utf-8") as f:
        f.write(f"file '{part1.replace(os.sep, "/")}'\n")
        f.write(f"file '{part2.replace(os.sep, "/")}'\n")

      print("[-] Joining segments...")
      self.execute([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        str(self.output_file)
      ])

      print(f"[+] Done: {self.output_file}")
    finally:
      shutil.rmtree(self.tempdir, ignore_errors=True)

  def execute(self, commands):
    result = subprocess.run(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
      print(result.stderr.decode(errors="ignore"))
      raise RuntimeError("FFmpeg command failed.")

  def run(self):
    self.check_params()
    self.cut()
