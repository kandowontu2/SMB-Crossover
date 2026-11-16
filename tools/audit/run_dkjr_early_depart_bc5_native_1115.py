"""Root native ordinary-controls DK Jr route with a returned-motor endpoint."""
from hashlib import sha256
from pathlib import Path
import argparse,json,time
import replay_dkjr_public_early_depart_bc5_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C=F.Hot
OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/dkjr-early-depart-bc5-native-1115.json'

def compact(row):
    if not isinstance(row,dict):return row
    return {k:v for k,v in row.items()if k in('Main','frame','x','y','top','left','center','phase','pipe','state','source','lives')}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group()
    group.add_argument('--fourth-carried',action='store_true')
    group.add_argument('--first-loss-probe',action='store_true')
    group.add_argument('--first-loss-probe-v2',action='store_true')
    group.add_argument('--private-x-probe',action='store_true');args=ap.parse_args()
    if args.first_loss_probe:
        raise RuntimeError('Known-invalid v1 callback registration; use --first-loss-probe-v2')
    selected=F
    if args.fourth_carried:
        import replay_dkjr_public_fourth_carried_bc5_1115 as selected
        GRANT=C.R/'docs/qa/allocations/dkjr-fourth-carried-bc5-native-1115.json'
    elif args.first_loss_probe_v2:
        import replay_dkjr_fourth_first_loss_bc5_v2_1115 as selected
        GRANT=C.R/'docs/qa/allocations/dkjr-first-loss-calibration-v2-bc5-native-1115.json'
    elif args.private_x_probe:
        import replay_dkjr_fourth_private_x_bc5_1115 as selected
        GRANT=C.R/'docs/qa/allocations/dkjr-private-x-calibration-bc5-native-1116.json'
    is_probe=args.first_loss_probe_v2 or args.private_x_probe
    g=json.loads(GRANT.read_bytes());assert g['native_ordinary_controls_authorized']and not g['ROM_game_state_or_helper_changes_authorized']
    assert sha256(Path(selected.__file__).read_bytes()).hexdigest()==g['factory_SHA256']
    before=check(C.ROM);raw=C.ROM.read_bytes();assert C.H(raw)==F.PIN==g['ROM_SHA256']
    if args.private_x_probe:
        C.lease();assert len(C.NEW)==len(C.OLD)==C.SIZE==118 and raw[C.FILE:C.FILE+C.SIZE]==C.NEW
        reference=raw[:C.FILE]+C.OLD+raw[C.FILE+C.SIZE:];assert C.H(reference)==C.PIN
        owner,_=F.Early.Old.identity(reference)
        spans=[(F.Early.Old.CHR+p*1024,1024)for p in F.Early.Old.PAGES]
        spans+=[(F.Early.Old.COOKIE_AT,16)]+[(at,len(data))for at,data in F.Early.Old.PUBLIC_NATIVE]
        assert sum(n for _,n in spans)==11433
        assert all(raw[at:at+n]==reference[at:at+n]and(at+n<=C.FILE or at>=C.FILE+C.SIZE)for at,n in spans)
        identity=dict(actual_input_SHA256=F.PIN,complete11433B_DK_owner_exact=True,
            complete_DK_owner_SHA256=owner['complete_DK_owner_SHA256'],reference67_SHA256=C.PIN,
            inverse='Exact leased118 OLD restoration; reference only',execution_ROM_is_not_normalized_reference=True)
        base=(OUT/'controller.lua').read_bytes().decode();assert C.H(base.encode())==g['base_probe_Lua_SHA256']
        text,descriptor=selected.from_probe_text(base,raw)
    else:reference,identity=F.normalize(raw,kind=F.KIND)
    if args.first_loss_probe_v2:text,descriptor=selected.controller(raw)
    elif args.private_x_probe:pass
    else:text=selected.controller(raw)if args.fourth_carried else F.controller(raw,grounded12=True)
    assert C.H(text.encode())==g['Lua_SHA256']
    assert identity['complete11433B_DK_owner_exact']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes();assert prior==raw
    require_free_workspace(C.R,C.ROM,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    started=time.monotonic()
    try:
        q=run(script,C.ROM,OUT/'capture',F.PIN,240,variant=0,extra_env={'SMB_DKJR_FAST_ROUTE':'1'})
    except Exception as error:
        print('NATIVE_OBSERVATION_FAILED '+json.dumps(dict(ROM_SHA256=F.PIN,
            Lua_SHA256=g['Lua_SHA256'],elapsed_seconds=round(time.monotonic()-started,3),
            error_type=type(error).__name__,error=str(error)[:1800],
            game_failure_not_inferred=True),separators=(',',':')),flush=True)
        raise
    assert q['script_SHA256']==g['Lua_SHA256']and not q['images']and q['outputs_written']==0
    assert C.ROM.read_bytes()==raw and check(C.ROM)==before and (OUT/'candidate.nes').read_bytes()==prior
    r=q['receipt'];out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    keys=('passed','reason','terminal','flag','castle','entrance','script_RAM_writes','controller_only',
          'injury','input_polls','grounded_12_return_count','actual_12_returns','first_grounded_12_return','last_grounded_12_return')
    out['receipt']={k:r[k]for k in keys if k in r}
    out['event_tail']=r.get('events',[])[-8:]
    out['earlier_hop_events']=[e for e in r.get('events',[])if e.get('event')in('third-depart-enemy-hop','third-static-ground-depart','fourth-actual-ride-adopted')]
    out['helper_births']={k:compact(v)for k,v in r.get('births',{}).items()}
    out['helper_carries']={k:dict(count=v.get('count'),first=compact(v.get('first')),last=compact(v.get('last')))for k,v in r.get('carries',{}).items()}
    out['owner_binding']=identity;out['host_Main_completion_claim']=False
    out['control']='fourth-carried'if args.fourth_carried else'earlier-third-depart'
    if is_probe:
        out['control']='passive-first-loss-calibration';out['diagnostic_only']=True
        out['receipt']['fourth_first_loss']=r.get('fourth_first_loss',{})
        out['receipt']['fourth_first_loss_counts']=r.get('fourth_first_loss_counts',{})
        out['hook_bindings']=descriptor
        del out['helper_births'],out['helper_carries'],out['event_tail'],out['earlier_hop_events']
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
    if is_probe:
        p=r.get('fourth_first_loss',{})
        assert p.get('first_carry')and p.get('motor_entry')and p.get('source4_writer')
        assert len(p)<=8 and not r['script_RAM_writes']
        raise SystemExit(0)
    assert q['passed'],'Current DK Jr full route remains unverified; retain negative and diagnose'
    assert r['flag']and r['castle']and r['entrance']and not r['script_RAM_writes']
    assert r['grounded_12_return_count']>=25 and r['actual_12_returns']>=25
    s=r['terminal'];assert s['world']==0 and s['level']==1 and s['engine']==8 and s['state']==0
    assert s['x']==40 and s['y']==176 and s['source']==1 and s['lives']==2
