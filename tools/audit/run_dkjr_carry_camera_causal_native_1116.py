"""Stage exact6d7 privately and observe its known-incomplete ordinary crossing."""
from pathlib import Path
import json
import replay_dkjr_carry_camera_probe_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.C
OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/dkjr-carry-camera-private-causal-1116.json'

if __name__=='__main__':
    g=json.loads(GRANT.read_bytes());assert g['private_staging_and_causal_native_authorized'] and not g['Downloads_delivery_authorized']
    assert C.H(Path(C.__file__).read_bytes())==g['composer_SHA256']
    assert C.H(Path(F.__file__).read_bytes())==g['probe_factory_SHA256']
    official=C.Bowser.ROM;before=check(official);parent=official.read_bytes();assert C.H(parent)==g['parent_SHA256']==C.PIN
    target=OUT/'candidate.nes';assert target.read_bytes()==parent
    assert {p.name for p in OUT.iterdir() if p.is_file()}=={'candidate.nes','controller.lua'}
    raw,q=C.proposal(parent);assert C.H(raw)==g['candidate_SHA256']==C.CANDIDATE and C.inverse(raw)==parent
    assert q['owned_bytes']==230 and q['changed_bytes']==143 and q['all_unowned_bytes_exact']
    text,meta=F.controller(raw);assert C.H(text.encode())==g['Lua_SHA256']
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(C.R,target,allow_interactive=True)
    target.write_bytes(raw);assert check(target)['ROM_sha256']==C.CANDIDATE
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    result=run(script,target,OUT/'capture',C.CANDIDATE,240,extra_env={'SMB_DKJR_FAST_ROUTE':'1'})
    assert not result['images'] and result['outputs_written']==0 and result['script_SHA256']==g['Lua_SHA256']
    assert official.read_bytes()==parent and check(official)==before and target.read_bytes()==raw
    r=result['receipt'];out={k:v for k,v in result.items() if k not in ('receipt','images','capture_preflight')}
    keep=('passed','reason','terminal','flag','castle','entrance','script_RAM_writes','controller_only',
        'grounded_12_return_count','actual_12_returns','fourth_first_loss','fourth_first_loss_counts')
    out['receipt']={k:r[k] for k in keep if k in r}
    out['event_tail']=r.get('events',[])[-6:]
    out.update(private_diagnostic_only=True,actual_Downloads_unchanged=True,metadata=meta)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    p=r.get('fourth_first_loss',{})
    assert p.get('first_carry') and p.get('motor_entry') and p.get('support') and p.get('plane')
    assert len(p)<=8 and not r['script_RAM_writes'],'Passive bounded diagnostic only'
