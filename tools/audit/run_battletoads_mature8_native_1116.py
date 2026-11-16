"""Root private/installed exact91dc food, native stock and full-stage replays."""
from pathlib import Path
import argparse,json
import compose_battletoads_mature8_1116 as C
import replay_battletoads_mature8_food_credit_1116 as Food
import replay_battletoads_mature8_stock_1116 as Stock
import replay_battletoads_mature8_full11_1116 as Full
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=C.R/'build/smb2-flag-native-1113'
GRANT=C.R/'docs/qa/allocations/battletoads-mature8-private-native-1116.json'
PRIOR_PRIVATE={'ffbb98f80038a51747f36339c6420c5446a4b3da1a7b0d2b3114146a6674b53d',
    '6d7c3fa958efd42a1fcf5d256f0c5506228d55d344dce9bf7382e577d06272f5'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage',action='store_true');ap.add_argument('--downloads',action='store_true')
    ap.add_argument('--kinds',nargs='+',choices=('mushroom','oneup','star','full'),default=['mushroom','oneup','star','full'])
    ap.add_argument('--keys',nargs='+',choices=('rash','zitz'),default=['rash','zitz']);args=ap.parse_args()
    g=json.loads(GRANT.read_bytes());assert g['private_staging_and_native_authorized']
    assert C.digest(Path(C.__file__).read_bytes())==g['composer_SHA256']
    before=check(C.ROM);official=C.ROM.read_bytes();assert C.digest(official) in (C.PIN,C.CANDIDATE)
    assert {p.name for p in OUT.iterdir() if p.is_file()}=={'candidate.nes','controller.lua'}
    target=OUT/'candidate.nes';Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    if args.stage:
        assert not args.downloads and C.digest(official)==C.PIN
        assert C.digest(target.read_bytes()) in PRIOR_PRIVATE|{C.PIN,C.CANDIDATE}
        raw,comp=C.proposal(official);assert C.inverse(raw)==official and comp['owned_bytes']==27 and comp['changed_bytes']==22
        require_free_workspace(C.R,target,allow_interactive=True)
        target.write_bytes(raw);assert check(target)['ROM_sha256']==C.CANDIDATE
    raw=target.read_bytes();assert C.digest(raw)==C.CANDIDATE and C.digest(C.inverse(raw))==C.PIN
    delivery=None
    if args.downloads:
        assert official==raw
        delivery=json.loads((C.R/'docs/qa/allocations/battletoads-mature8-delivery-1116.json').read_bytes())
        assert delivery['direct_Downloads_replacement_authorized'] and delivery['candidate_SHA256']==C.CANDIDATE
    path=C.ROM if args.downloads else target
    for kind in args.kinds:
        module=Food if kind=='mushroom' else Full if kind=='full' else Stock
        assert C.digest(Path(module.__file__).read_bytes())==g['factory_SHA256'][kind]
        for key in args.keys:
            name=kind+'_'+key
            text=module.controller(raw,key) if kind in ('mushroom','full') else module.controller(raw,key,kind)
            assert C.digest(text.encode())==g['Lua_SHA256'][name]
            require_free_workspace(C.R,path,allow_interactive=True)
            script=OUT/'controller.lua';script.write_bytes(text.encode())
            q=run(script,path,OUT/'capture',C.CANDIDATE,240)
            assert q['script_SHA256']==g['Lua_SHA256'][name] and not q['images'] and q['outputs_written']==0
            assert C.ROM.read_bytes()==official and check(C.ROM)==before and target.read_bytes()==raw
            if delivery is not None:assert q['passed'] and q['receipt_SHA256']==delivery['private_native_receipts'][name]
            r=q['receipt'];out={k:v for k,v in q.items() if k not in ('receipt','images','capture_preflight')}
            omit={'food','events','recent','records','trace','samples'}
            out['receipt']={k:v for k,v in r.items() if k not in omit}
            if 'food' in r:
                out['food']={k:v for k,v in r['food'].items() if k not in ('heads','head_queries','actual_head','trace','samples')}
                if 'stock' in out['food']:
                    out['food']['stock']={k:v for k,v in out['food']['stock'].items() if k not in ('samples','trace')}
            out.update(kind=kind,key=key,actual_Downloads=args.downloads,private_receipt_match=delivery is not None)
            print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
            assert q['passed'],'Native candidate gate remains open; preserve negative'
            assert not r.get('game_state_writes',r.get('script_RAM_writes',False))
            if kind=='full':
                assert r['Bt_original_entries']==r['Bt_original_returns']
                assert r['full_nonshortcut1_1'] and r['next_area_updates']>=25
                s=r['terminal'];assert s['y']==176 and s['x']==40 and s['level']==1 and s['lives']==2
            else:assert r['Bt_entries']==r['Bt_returns'] and r['Main_entries']==r['Main_returns']
