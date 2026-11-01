"""Prepare a bounded, hash-bound controller observer with an isolated Mesen queue."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prepare(output, rom, controller, refs, *, expected, timeout, scope):
    output = output.resolve()
    rom = rom.resolve()
    assert output.is_relative_to(R / 'build')
    assert not output.exists() or set(p.name for p in output.iterdir()) <= {'controller.lua', 'run.py', 'ready.json'}
    assert sha(rom) == expected
    assert 1 <= timeout <= 240
    output.mkdir(exist_ok=True)
    (output / 'controller.lua').write_text(controller, encoding='utf-8', newline='\n')
    (output / 'run.py').write_text('''from pathlib import Path
import hashlib,json,os,sys
O=Path(__file__).resolve().parent
R=next(p for p in O.parents if(p/'AGENTS.md').is_file())
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from run_mesen import run
from mesen_session_guard_v1 import require_free_workspace
q=json.loads((O/'ready.json').read_text())
for p,h in q['bindings'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
other=require_free_workspace(R,Path(q['ROM']))
print('Other-project Mesen sessions left untouched: '+json.dumps([p['ProcessId'] for p in other]),flush=True)
os.environ['SMB_RUN_OUTPUT']=str(O/'capture')
O.joinpath('capture').mkdir()
(O/'capture/session-before.json').write_text(json.dumps(other,indent=2)+'\\n')
result=run(O/'controller.lua',Path(q['ROM']),timeout=q['timeout'],emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
for p,h in q['bindings'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
(O/'capture/binding.json').write_text(json.dumps(dict(ROM_sha256=q['ROM_sha256'],ready_sha256=hashlib.sha256((O/'ready.json').read_bytes()).hexdigest(),exit_code=result),indent=2)+'\\n')
raise SystemExit(result)
''', encoding='utf-8', newline='\n')
    paths = {Path(__file__), rom, rom.with_suffix('.lbl'), rom.with_suffix('.dbg'),
             output / 'controller.lua', output / 'run.py',
             R / 'tools/run_mesen.py', R / 'tools/audit/mesen_session_guard_v1.py',
             R / 'tools/audit/capture_budget.py', R / 'tools/audit/build_storage_guard_v1.py',
             R / 'tools/audit/run_bounded_build_v1.py', *refs}
    ready = dict(prepared=True, native=False, ROM=str(rom), ROM_sha256=expected,
                 timeout=timeout, scope=scope, emulated_writes=False,
                 run_byte_cap=128_000_000, max_files=64, max_PNGs=4,
                 bindings={str(p.resolve()): sha(p) for p in sorted(paths)})
    (output / 'ready.json').write_text(json.dumps(ready, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(prepared=True, ready=str(output / 'ready.json'), ROM_sha256=expected)))
