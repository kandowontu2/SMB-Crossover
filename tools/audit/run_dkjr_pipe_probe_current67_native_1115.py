"""Root first-failure diagnostic over unchanged current DK Jr controls."""
from hashlib import sha256
from pathlib import Path
import json
import replay_dkjr_public_first_pipe_probe_67_1115 as P
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

F=P.F
OUT=F.R/'build/smb2-flag-native-1113'
FACTORY='969bdb02aaabce94627ff0dcca0e156a9d38728d66dced403f2fbc96707b5ed1'
LUA='2ad66369a32a5d6313317151a9c4ba4b8bcc5d9bf7cccf4ff59d5149942aa689'

if __name__=='__main__':
    assert sha256(Path(P.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(F.NIGHTLY);raw=F.NIGHTLY.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=P.controller(raw);assert sha256(text.encode()).hexdigest()==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    prior=(OUT/'candidate.nes').read_bytes();require_free_workspace(F.R,F.NIGHTLY,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.NIGHTLY,OUT/'capture',F.PIN,240,extra_env={'SMB_DKJR_FAST_ROUTE':'1'})
    assert q['script_SHA256']==LUA and not q['images']and q['outputs_written']==0
    assert F.NIGHTLY.read_bytes()==raw and check(F.NIGHTLY)==before and (OUT/'candidate.nes').read_bytes()==prior
    r=q['receipt'];summary={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    summary['receipt']={k:v for k,v in r.items()if k.startswith('pipe1_')or k in('passed','reason','terminal','script_RAM_writes','controller_only')}
    summary['diagnostic_only']=True
    print('RESULT '+json.dumps(summary,separators=(',',':')),flush=True)
    assert r.get('pipe1_first_source5'),'First failing source transition was not observed'
    assert not r['script_RAM_writes']
