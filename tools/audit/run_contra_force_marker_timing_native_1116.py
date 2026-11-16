"""Matched actual6a3/privateffbb idle and Right timing, frozen observer body."""
from pathlib import Path
import argparse,json
import replay_contra_force_marker_cadence_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.C
OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/contra-force-marker-private-timing-1116.json'
DK='6d7c3fa958efd42a1fcf5d256f0c5506228d55d344dce9bf7382e577d06272f5'

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=('both','parent','candidate'),default='both');args=ap.parse_args()
    g=json.loads(GRANT.read_bytes());assert g['private_staging_and_timing_native_authorized'] and not g['Downloads_delivery_authorized']
    assert C.H(Path(C.__file__).read_bytes())==g['composer_SHA256'] and C.H(Path(F.__file__).read_bytes())==g['cadence_factory_SHA256']
    assert C.H(F.Frozen.body().encode())==g['observer_body_SHA256']
    before=check(C.ROM);parent=C.ROM.read_bytes();assert C.H(parent)==C.PIN==g['parent_SHA256']
    target=OUT/'candidate.nes';assert C.H(target.read_bytes()) in (C.PIN,C.CANDIDATE,DK)
    assert {p.name for p in OUT.iterdir() if p.is_file()}=={'candidate.nes','controller.lua'}
    candidate,composition=C.proposal(parent);assert C.H(candidate)==g['candidate_SHA256'] and C.inverse(candidate)==parent
    assert composition['owned_bytes']==1042 and composition['changed_bytes']==714
    modes=('parent','candidate') if args.mode=='both' else (args.mode,)
    for mode in modes:
        raw=parent if mode=='parent' else candidate;path=C.ROM if mode=='parent' else target
        text=F.controller(raw,'burns');assert C.H(text.encode())==g['Lua_SHA256'][mode]
        Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
        require_free_workspace(C.R,path,allow_interactive=True)
        if mode=='candidate':
            target.write_bytes(raw);assert check(target)['ROM_sha256']==C.CANDIDATE
        prior=target.read_bytes();script=OUT/'controller.lua';script.write_bytes(text.encode())
        q=run(script,path,OUT/'capture',C.H(raw),240,variant=0)
        assert q['script_SHA256']==g['Lua_SHA256'][mode] and not q['images'] and q['outputs_written']==0
        assert C.ROM.read_bytes()==parent and check(C.ROM)==before and target.read_bytes()==prior
        out={k:v for k,v in q.items() if k not in ('images','capture_preflight')}
        out.update(mode=mode,actual_Downloads_baseline=mode=='parent',private_timing_only=mode=='candidate',Downloads_unchanged=True)
        print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
        assert q['passed'],'Timing observer needs valid scoped receipt before its metrics are used'
        r=q['receipt'];assert not r['game_state_writes'] and len(r['phases'])==2
        assert [p['Main_returns'] for p in r['phases']]==[48,16]
        assert all(p['Main_entries']==p['Main_returns'] for p in r['phases'])
