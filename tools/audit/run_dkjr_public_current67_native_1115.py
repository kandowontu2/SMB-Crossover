"""Root replays the delivered public DK Jr route on actual current67."""
from hashlib import sha256
from pathlib import Path
import argparse,json
import recover_dkjr_current_identity_67_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='bd66417d48d7e068226402cb8853f7a1ef94b95117c06580faa064522d608b08'
LUA='43b51e99c2e05c101a697f35bbf4a154deb6a3a3b4edf455f58bf586badb500d'

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cap-depart',action='store_true');args=ap.parse_args()
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.NIGHTLY);raw=F.NIGHTLY.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    ownership,_=F.identity(raw);expected=LUA
    if args.cap_depart:
        import replay_dkjr_public_cap_depart_67_1115 as Cap
        assert sha256(Path(Cap.__file__).read_bytes()).hexdigest()=='d4a14cf6d92f5c561ac3025369d67d7e1d5c056e07315044818d2e054b6f534c'
        text=Cap.controller(raw);expected='5c65a62251a0613e0c072087cc81f94716426e037c3ae9618d59e3415ddd9ffa'
    else:text=F.controller(raw,kind='delivered-public-67')
    assert sha256(text.encode()).hexdigest()==expected
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes();require_free_workspace(F.R,F.NIGHTLY,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.NIGHTLY,OUT/'capture',F.PIN,240,variant=0,extra_env={'SMB_DKJR_FAST_ROUTE':'1'})
    assert q['script_SHA256']==expected and not q['images']and q['outputs_written']==0
    assert F.NIGHTLY.read_bytes()==raw and check(F.NIGHTLY)==before and (OUT/'candidate.nes').read_bytes()==prior
    r=q['receipt'];summary={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    keys=('passed','reason','terminal','flag','castle','entrance','script_RAM_writes',
          'controller_only','injury','input_polls','first_gap','second_gap','third_gap')
    summary['receipt']={k:r[k]for k in keys if k in r}
    summary['receipt'].update({k:v for k,v in r.items()if k.startswith('pipe1_')})
    summary['control']='cap-depart'if args.cap_depart else'delivered-public'
    summary['helper_births']=r.get('births',{})
    summary['helper_carries']={k:{a:b for a,b in v.items()if a in('count','first','last')}if isinstance(v,dict)else v for k,v in r.get('carries',{}).items()}
    summary['current_public_owner_SHA256']=ownership['complete_DK_owner_SHA256']
    print('RESULT '+json.dumps(summary,separators=(',',':')),flush=True)
    assert q['passed'],'Delivered public DK Jr current route remains unverified'
    assert r['flag']and r['castle']and r['entrance']and r['terminal']['level']==1
    assert r['terminal']['engine']==8 and r['terminal']['lives']==2 and not r['script_RAM_writes']
