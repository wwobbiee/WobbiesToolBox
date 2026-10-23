import subprocess

from pathlib import Path


class fixTools:
  def __init__(self, args):
    self.input_dir = Path(args.VOD)
    self.output_dir = Path(args.output_dir)

  def is_valid(self, file) -> bool:
    return file.exists() and file.stat().st_size > 0

  def fix(self, vod):
    print(f"Processing: {vod.name}")

    out_file = self.output_dir / vod.name

    # Normal remux (fast, lossles)
    command1 = [
      "ffmpeg", "-y",
      "-i", str(vod),
      "-c", "copy",
      str(out_file)
    ]

    code, err = self.execute(command1)
    if self.is_valid(out_file):
      print("[+] Remux successful.")
      return

    print("[X] Remux failed, trying recovery mode...")

    # Recovery mode (fix timestampes, ignore errors)
    command2 = [
      "ffmpeg", "-y",
      "-fflags", "+genpts",
      "-err_detect", "ignore_err",
      "-i", str(vod),
      "-c", "copy",
      str(out_file)
    ]

    code, err = self.execute(command2)
    if self.is_valid(out_file):
      print("[+] Recovery successful.")
    else:
      print(f"[X] Failed to repair: {vod.name}")

      log_file = self.output_dir / f"{vod.name}.log"
      with open(log_file, "w") as f:
        f.write(err)

  def execute(self, command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
      print(result.stderr.decode(errors="ignore"))

    return result.returncode, result.stderr

  def run(self):
    if self.input_dir.is_dir():
      for vod in self.input_dir.glob("*.mkv"):
        self.fix(vod)
    elif self.input_dir.is_file():
      self.fix(self.input_dir)
