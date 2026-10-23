import subprocess

from pathlib import Path

class reencodeTools:
  def __init__(self, args):
    self.input_file = Path(args.VOD)

  def validate_input(self):
    if not self.input_file.exists():
      raise ValueError("Input file not found.")
    if not self.input_file.is_file():
      raise ValueError("Input is not file.")

  def reencode(self):
    output_file = self.input_file.with_suffix(".mp4")
    if output_file.exists():
      prompt = input(f"Output exists ({output_file}). Overwrite [y/N]?").lower()
      if prompt not in ("y", "yes"):
        raise RuntimeError("[-] Cancelled operation.")
      output_file.unlink()

    print("[+] Reencoding to mp4...")
    command1 = [
      "ffmpeg",
      "-i", str(self.input_file),
      
      "-map", "0:v",
      "-map", "0:a",

      "-c:v", "libx264",
      "-crf", "18",
      "-preset", "medium",
      "-pix_fmt", "yuv420p",
      "-fps_mode", "cfr",

      "-c:a", "aac",
      "-b:a", "192k",
      "-map_metadata", "0",

      str(output_file)
    ]

    self.execute(command1)

    print(f"[+] Done: {output_file}")
    return output_file

  def execute(self, command):
    try:
      subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
      print(f"[X] FFmpeg failed with exit code: {e.returncode}")
      raise

  def run(self):
    self.validate_input()
    return self.reencode()

