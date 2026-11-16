"""Root passive physical/shadow comparison; does not qualify or deliver the fix."""
from hashlib import sha256
from pathlib import Path
import json
import replay_bub_star_oam_diagnostic_67_1115 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.SLOT
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
FACTORY='265fe5aff817da9406ccc45d103adfdbf55dd19bef14918d28ce12f81be9e07e'
LUA='b8570250d94f0cf0817021be37ded2e0d12435e0194afcef7f2f1ad5fcc2cb11'
OFFICIAL='7fb328a6dcf6b50fd000e81eced4fd4b7390bedec56085d33130434003cc76d0'

if __name__=='__main__':
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    before=check(ROM);official=ROM.read_bytes();assert sha256(official).hexdigest()==OFFICIAL
    target=OUT/'candidate.nes';raw=target.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw);assert sha256(text.encode()).hexdigest()==LUA
    assert {p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    require_free_workspace(F.R,target,allow_interactive=True)
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,target,OUT/'capture',F.PIN,240)
    assert q['script_SHA256']==LUA and len(q['images'])<=3 and q['outputs_written']==0
    assert ROM.read_bytes()==official and check(ROM)==before and target.read_bytes()==raw
    r=q['receipt'];d=r.get('star_oam_diagnostic')
    summary={k:v for k,v in q.items()if k not in('receipt','images','capture_preflight')}
    summary['receipt']={k:r[k]for k in('passed','reason','Main_updates','source_updates','physical_frames','terminal')if k in r}
    summary['receipt']['star_oam_diagnostic']=d
    summary['images']=[{k:v for k,v in im.items()if k!='base64'}for im in q['images']]
    summary['diagnostic_only']=True
    print('RESULT '+json.dumps(summary,separators=(',',':')),flush=True)
    assert d and d['frames']and d['dma'],'Passive diagnostic did not observe real active-Star output'
    assert not r['runtime_state_writes']
