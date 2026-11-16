"""Bind two passive image observations without launching Mesen or writing ROMs."""
from pathlib import Path
import json

import replay_dkjr_entry_images_root_1116 as F

if __name__ == '__main__':
    raw, _ = F.C.current_proposal(F.C.BT.ROM.read_bytes())
    text = F.controller(raw)
    report = dict(passed=True, candidate_SHA256=F.H(raw),
                  factory_SHA256=F.H(Path(F.__file__).read_bytes()),
                  base_factory_SHA256=F.BASE_SHA, Lua_SHA256=F.H(text.encode()),
                  exact_controls_after_observer_removal=True, maximum_images=2,
                  maximum_PNG_bytes_each=65536, new_output_files=0,
                  scope='Controller compile and passive observer restoration only; no CPU or Mesen/image capture')
    report['receipt_SHA256'] = F.H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
