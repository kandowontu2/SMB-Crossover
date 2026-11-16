"""Repeat exact private cadence and full-stage receipts from the installed nightly."""
from pathlib import Path
import json
import replay_hot_draw_bt_67e_1115 as F
import run_hot_draw_stair_native_1115 as Stage
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.C
OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/hot-draw-bt118-delivery-1115.json'

if __name__=='__main__':
    g=json.loads(GRANT.read_bytes());assert g['direct_Downloads_replacement_authorized']
    raw=F.ROM.read_bytes();assert C.H(raw)==C.CANDIDATE and raw==(OUT/'candidate.nes').read_bytes()
    before=check(F.ROM);assert C.H(Path(F.__file__).read_bytes())==g['cadence_factory_SHA256']
    text=F.cadence_reads(raw);assert C.H(text.encode())==g['cadence_Lua_SHA256']
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(C.R,C.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',C.CANDIDATE,240)
    assert q['script_SHA256']==g['cadence_Lua_SHA256']and not q['images']and q['outputs_written']==0
    assert q['passed']and q['receipt_SHA256']==g['private_native_receipts']['cadence']
    out={k:v for k,v in q.items()if k not in('images','capture_preflight')}
    out.update(identity='fixed-cadence',actual_Downloads_repeat=True,private_receipt_match=True)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    for identity in('zitz','rash'):
        q=Stage.Root.execute(identity,True);r=q['receipt']
        assert q['passed']and q['receipt_SHA256']==g['private_native_receipts'][identity]
        assert q['script_SHA256']==g['stage_Lua_SHA256'][identity]
        assert r['Main_entries']==r['Main_returned']and not r['game_state_writes']
        assert r['full_nonshortcut1_1']and r['next_area_updates']>=25
        s=r['terminal'];assert s['world']==0 and s['level']==1 and s['engine']==8 and s['state']==0
        assert s['y']==176 and s['source_HP']>0 and s['lives']==2
        out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
        keep=('passed','reason','Main_entries','Main_returned','physical_frames','full_nonshortcut1_1',
              'next_area_updates','Bt_1_2_steps','Bt_source_steps','minimum_source_HP','terminal','game_state_writes')
        out['receipt']={k:r[k]for k in keep if k in r}
        out.update(identity=identity,actual_Downloads_repeat=True,private_receipt_match=True)
        print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before and raw==(OUT/'candidate.nes').read_bytes()
