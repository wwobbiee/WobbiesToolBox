import shutil

from pathlib import Path
from .normalizeTools import normalizeTools
from .reencodeTools import reencodeTools


class editTools:
  def __init__(self, args):
    self.VOD        = Path(args.VOD)
    self.normalize  = normalizeTools(args)
    self.reenc      = reencodeTools(args)
    self.output_dir = (self.VOD.parent / "wtb_edit_processed" / self.VOD.stem)

  def move_to_dir(self, norm_files, vod_out):
    self.output_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(vod_out), str(self.output_dir / vod_out.name))
    for file in norm_files:
      shutil.move(str(file), str(self.output_dir / file.name))
    print(f"[+] Processed files saved to {self.output_dir}")

  def run(self):
    norm_out = self.normalize.run()
    vod_out = self.reenc.run()
    
    self.move_to_dir(norm_out, vod_out)
