"""Root's single bounded native queue; one reusable ROM/Lua slot, no captures."""
from hashlib import sha256
import argparse,json
from pathlib import Path

import compose_battletoads_native_service_1114 as C
import replay_battletoads_native_service_1114 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
DESTINATION=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def execute(mode):
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    guard=check(DESTINATION);raw=DESTINATION.read_bytes();assert sha256(raw).hexdigest()==C.PIN
    image,composition=C.proposal(raw);assert C.inverse(image)==raw
    # Compile every controller before replacing either disposable slot file.
    texts={'baseline':F.cadence(raw,baseline=True),'cadence':F.cadence(image),
           'rash':F.controller(image,'rash'),'zitz':F.controller(image,'zitz')}
    assert mode in texts
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    target=DESTINATION if mode=='baseline'else OUT/'candidate.nes'
    if mode!='baseline':target.write_bytes(image);assert target.read_bytes()==image
    text=texts[mode];script=OUT/'controller.lua';script.write_bytes(text.encode())
    expected=C.PIN if mode=='baseline'else C.CANDIDATE
    q=run(script,target,OUT/'capture',expected,240)
    assert q['script_SHA256']==sha256(text.encode()).hexdigest()
    assert not q['images']and q['outputs_written']==0
    assert DESTINATION.read_bytes()==raw and check(DESTINATION)==guard
    return dict(mode=mode,composition=composition,**q)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('baseline','cadence','rash','zitz'));a=p.parse_args()
    q=execute(a.mode);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Native candidate gate remains unqualified'
