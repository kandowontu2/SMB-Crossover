"""Root single-queue genuine Mushroom replay on unchanged actual Downloads."""
import json
from pathlib import Path

import replay_excitebike_mushroom_91dc_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
GRANT=F.R/'docs/qa/allocations/excitebike-mushroom-downloads-root-1116.json'


def run_case(factory,grant_path,key):
    F=factory
    grant=json.loads(grant_path.read_bytes())
    assert grant['native_Mesen_actual_Downloads_authorized'] and not grant['ROM_replacement_authorized']
    assert F.digest(Path(F.__file__).read_bytes())==grant['factory_SHA256']
    before=check(F.ROM);raw=F.ROM.read_bytes();assert F.digest(raw)==grant['ROM_SHA256']==F.PIN
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    candidate=OUT/'candidate.nes';assert candidate.read_bytes()==raw
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    text=F.controller(raw,key);assert F.digest(text.encode())==grant['Lua_SHA256']
    require_free_workspace(F.R,F.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,240)
    assert F.ROM.read_bytes()==raw and candidate.read_bytes()==raw and check(F.ROM)==before
    assert q['script_SHA256']==grant['Lua_SHA256'] and not q['images'] and q['outputs_written']==0
    receipt=q['receipt'];out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    out['receipt']={k:v for k,v in receipt.items()if k not in('food','events','samples','trace')}
    out['food']=receipt.get('food');out['actual_Downloads']=True;out['key']=key
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert q['passed'],'Retain native negative; no qualification claim'
    assert not receipt.get('game_state_writes',receipt.get('script_RAM_writes',False))


if __name__=='__main__':run_case(F,GRANT,'excitebike')
