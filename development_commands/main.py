import shutil

from pathlib import Path


class scaffoldMVC:
  TEMPLATE_DIR = Path(__file__).parent / "_templates"

  def copy_if_missing(self, src, dst):
    dst = Path(dst)
    if dst.exists():
      print(f"[-] Skipping existing file: {dst}")
    return shutil.copy2(src, dst)

  def scaffold(self, template_dir: str, dest: Path):
    template = self.TEMPLATE_DIR / template_dir
    dest = Path(dest)

    if not template.is_dir():
      raise FileNotFoundError(f"[X] Template dir not found: {template}")
    dest.mkdir(parents=True, exist_ok=True)
    
    for item in template.iterdir():
      target = dest / item.name

      if item.is_dir():
        if target.exists() and not target.is_dir():
          print(f"Will not, and cannot overwrite existing file: {target}")
          continue

        shutil.copytree(item, target, dirs_exist_ok=True, copy_function=self.copy_if_missing)
      else:
        self.copy_if_missing(item, target)
  
    print("[+] Finished. Run:\nnpm install\n")

class devTools:
  def __init__(self, args):
    self.command = args.dev_command
    self.args    = args

  def run(self):
    dest = Path(self.args.path).resolve()
    scaffold = scaffoldMVC()

    if self.command == "mvc":
      scaffold.scaffold("mvc", dest)
    elif self.command == "express":
      scaffold.scaffold("mvc", dest)
      scaffold.scaffold("express", dest)