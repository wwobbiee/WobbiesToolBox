from .cutTools import cutTools
from .fixTools import fixTools
from .reencodeTools import reencodeTools
from .normalizeTools import normalizeTools
from .editTools import editTools

class vodTools:
  def __init__(self, args):
    self.command = args.vod_command
    self.args    = args

  def run(self):
    if self.command == "cut":
      cut_vod = cutTools(self.args)
      cut_vod.run()
    elif self.command == "fix":
      fix_vod = fixTools(self.args)
      fix_vod.run()
    elif self.command == "encode":
      reenc_vod = reencodeTools(self.args)
      reenc_vod.run()
    elif self.command == "normalize":
      normalize_vod = normalizeTools(self.args)
      normalize_vod.run()
    elif self.command == "edit":
      edit_vod = editTools(self.args)
      edit_vod.run()
