"""Private and installed signed-life Bowser item replays, exact scoped pins."""
from pathlib import Path
import argparse,json
import compose_bowser_life_gain_signed_1116 as C
import replay_bowser_life_gain_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/bowser-life-gain-private-native-1116.json'

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage',action='store_true')
    ap.add_argument('--downloads',action='store_true')
    ap.add_argument('--kind',nargs='+',choices=('oneup','star'),default=['oneup','star'])
    ap.add_argument('--identity',nargs='+',type=int,choices=(0,1),default=[0,1]);args=ap.parse_args()
    g=json.loads(GRANT.read_bytes());assert g['all_scoped_source_gates_complete']and g['private_candidate_staging_and_native_items_authorized']
    assert C.digest(Path(C.__file__).read_bytes())==g['composer_SHA256']and C.digest(Path(F.__file__).read_bytes())==g['factory_SHA256']
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    before=check(C.ROM);official=C.ROM.read_bytes();assert C.digest(official)in(C.PIN,C.CANDIDATE)
    target=OUT/'candidate.nes';Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    if args.stage:
        assert not args.downloads and C.digest(official)==C.PIN and C.digest(target.read_bytes())in(C.PIN,C.CANDIDATE)
        candidate,info=C.proposal(official);assert info['owned_bytes']==72 and info['changed_bytes']==56
        assert C.inverse(candidate)==official
        require_free_workspace(C.R,target,allow_interactive=True)
        target.write_bytes(candidate);assert check(target)['ROM_sha256']==C.CANDIDATE
    candidate=target.read_bytes();assert C.digest(candidate)==g['candidate_SHA256']==C.CANDIDATE
    parent=C.inverse(candidate);assert C.digest(parent)==C.PIN and official in(parent,candidate)
    delivery=None
    if args.downloads:
        assert official==candidate
        delivery=json.loads((C.R/'docs/qa/allocations/bowser-life-gain-delivery-1116.json').read_bytes())
        assert delivery['direct_Downloads_replacement_authorized']
        assert delivery['candidate_SHA256']==C.CANDIDATE and delivery['parent_SHA256']==C.PIN
        assert delivery['composer_SHA256']==g['composer_SHA256'] and delivery['factory_SHA256']==g['factory_SHA256']
    path=C.ROM if args.downloads else target
    for kind in args.kind:
        for identity in args.identity:
            expected=g['Lua_SHA256'][kind+str(identity)];text=F.controller(candidate,identity,kind)
            assert C.digest(text.encode())==expected
            require_free_workspace(C.R,path,allow_interactive=True)
            script=OUT/'controller.lua';script.write_bytes(text.encode())
            q=run(script,path,OUT/'capture',C.CANDIDATE,240,variant=0)
            assert q['script_SHA256']==expected and not q['images']and q['outputs_written']==0
            if delivery is not None:
                assert q['passed'] and q['receipt_SHA256']==delivery['private_native_receipts'][kind+str(identity)]
            assert C.ROM.read_bytes()==official and check(C.ROM)==before and target.read_bytes()==candidate
            r=q['receipt'];out={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
            out['receipt']={k:v for k,v in r.items()if k not in('stock','natural','pipes','recent','records','events')}
            out['receipt']['stock']={k:v for k,v in r.get('stock',{}).items()if k not in('trace','samples')}
            out['receipt']['natural_keys']=list(r.get('natural',{}))
            out.update(identity=identity,kind=kind,actual_Downloads=args.downloads)
            if delivery is not None:out['private_receipt_match']=True
            print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
            assert q['passed'],'Candidate Bowser native item gate remains open'
            s=r['stock'];assert s['resumed']==s['tail_resumed']==25
            c=s['counts'];assert all(c[n+'_entries']==c[n+'_returns']for n in('movement','core','tail'))
            if kind=='oneup':assert s['saved_life']==3 and s['preserved_HP']==s['credit']['s']['health']
            else:assert s['credit']['after']-s['credit']['before']==1000
