import re
import json
import shutil
import subprocess

from pathlib import Path

class normalizeTools:
  ATTACK = 5
  RELEASE = 150
  DYNAUDNORM = "dynaudnorm=f=250:g=15:p=0.95"
  LIMITER = "alimiter=limit=0.9"
  PREVIEW_SECONDS = 120
  WAV_LIMIT = 3.8 * 1024 ** 3

  def __init__(self, args):
    self.input_file = Path(args.VOD)
    self.FFMPEG     = self.ff_exists("ffmpeg")
    self.FFPROBE    = self.ff_exists("ffprobe")
    self.NO_AUDIO   = -89
    self.processed  = []

  def ff_exists(self, name):
    path = shutil.which(name)
    if not path:
      raise RuntimeError(f"[X] '{name}' not found on PATH. Install FFmpeg and try again.")
    return path

  def probe(self, path):
    command = [
      self.FFPROBE,
      "-v", "error",
      "-select_streams", "a",
      "-show_entries",
      "stream=index,codec_name,sample_rate,channels,channel_layout:stream_tags=title",
      "-show_entries",
      "format=duration",
      "-of", "json",
      str(path)
    ]
    result = self.execute(command, {
      "capture_output": True,
      "text": True
    })

    if result.returncode != 0:
      raise RuntimeError("[X] FFprobe failed.")

    data = json.loads(result.stdout)
    streams = data.get("streams", [])

    if not streams:
      raise RuntimeError("[X] No audio streams found.")

    duration = float(data["format"]["duration"])
    audio_streams = []

    for stream in streams:
      audio_streams.append({
        "index":          stream["index"],
        "codec":          stream.get("codec_name"),
        "sample_rate":    int(stream.get("sample_rate", 0)),
        "channels":       int(stream.get("channels", 0)),
        "channel_layout": stream.get("channel_layout"),
        "title":          stream.get("tags", {}).get("title"),
      })

    return duration, audio_streams

  def analyze(self, path, duration, stream_index):
    print("[-] Analyzing audio...")

    command = [
      self.FFMPEG,
      "-hide_banner",
      "-i",   str(path),
      "-map", f"0:{stream_index}",
      "-t",   str(min(duration, self.PREVIEW_SECONDS)),
      "-af",  "volumedetect",
      "-f",   "null",
      "NUL"
    ]

    result = self.execute(command, {
      "stdout": subprocess.PIPE,
      "stderr": subprocess.PIPE,
      "text": True
    })

    log = result.stderr
    mean_match = re.search(r"mean_volume:\s*(-?[\d.]+)\s*dB", log)
    max_match  = re.search(r"max_volume:\s*(-?[\d.]+)\s*dB", log)

    if not mean_match or not max_match:
      return None
      # raise RuntimeError("[X] Could not analyze audio.")

    mean_volume         = float(mean_match.group(1))
    max_volume          = float(max_match.group(1))

    if max_volume < self.NO_AUDIO:
      return None

    dynamic_range       = max_volume - mean_volume
    suggested_threshold = mean_volume + 2
    suggested_ratio     = max(2, min(8, round(dynamic_range / 6, 1)))

    return {
      "mean": mean_volume,
      "max": max_volume,
      "dynamic_range": dynamic_range,
      "threshold": suggested_threshold,
      "ratio": suggested_ratio
    }

  def ask(self, analysis):
    print()
    print(f"Mean volume:     {analysis["mean"]:.1f} dB")
    print(f"Peak volume:     {analysis["max"]:.1f} dB")
    print(f"Dynamic range:   {analysis["dynamic_range"]:.1f} dB")
    print()

    default_threshold = analysis["threshold"]
    default_ratio     = analysis["ratio"]

    threshold_input   = input(f"Compressor threshold [{default_threshold:.1f}]: ").strip()
    ratio_input       = input(f"Compressor ratio [{default_ratio:.1f}]: ").strip()

    threshold         = float(threshold_input) if threshold_input else default_threshold
    ratio             = float(ratio_input) if ratio_input else default_ratio

    return threshold, ratio

  def normalize(self, stream_index, track_number, threshold, ratio):
    output_file = self.input_file.with_name(f"{self.input_file.stem}_track{track_number}_normalized.wav")

    if output_file.exists():
      prompt = input(f"[!] Output exists ({output_file}). Overwrite [y/N]? ").lower()

      if prompt not in ("y", "yes"):
        raise RuntimeError("[-] Cancelled operation.")
      output_file.unlink()

    compressor   = f"acompressor=threshold={threshold}dB:ratio={ratio}:attack={self.ATTACK}:release={self.RELEASE}"
    filter_chain = f"{compressor},{self.DYNAUDNORM},{self.LIMITER}"

    print("[-] Normalizing audio...")

    command = [
      self.FFMPEG,
      "-y",
      "-i", str(self.input_file),
      "-map", f"0:{stream_index}",
      "-af", filter_chain,
      "-c:a", "pcm_s16le",
      str(output_file)
    ]

    self.execute(command)
    self.processed.append(output_file)
    print(f"[+] Done: {output_file}")

  def execute(self, command, options=None):
    if options is None:
      options = {}

    try:
      result = subprocess.run(command, **options, check=True)
      return result
    except subprocess.CalledProcessError as e:
      print(f"[X] FFmpeg failed with exit code: {e.returncode}")
      raise

  def run(self):
    duration, audio_streams = self.probe(self.input_file)
    print(f"[+] Found {len(audio_streams)} audio track(s).\n")

    for track_number, stream in enumerate(audio_streams, start=1):
      print(f"--- Audio Track {track_number} ---")
      print(f"Stream:          {stream["index"]}")
      print(f"Codec:           {stream["codec"]}")
      print(f"Sample rate:     {stream["sample_rate"]} Hz")
      print(f"Channels:        {stream["channels"]}")
      print(f"Layout:          {stream["channel_layout"] or "unknown"}")

      if stream["title"]:
        print(f"Title:           {stream["title"]}")
      print()

      analysis = self.analyze(self.input_file, duration, stream["index"])

      if analysis is None:
        print("[-] Track is empty, skipping.\n")
        continue
      threshold, ratio = self.ask(analysis)

      self.normalize(stream["index"], track_number, threshold, ratio)

      print()

    return self.processed
