"""Bounded KB controller discovery/replay using one frozen ROM/symbol set.

No emulated writes or save-state edits. Reuses the standard roster harness and
audit; avoids copying the same 15 MB debug symbols into every negative attempt.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, sys, zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen
from workspace_storage import CAP_BYTES
from playthroughs.roster_run import workspace_bytes

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    a = argparse.ArgumentParser()
    a.add_argument('--character', type=int, required=True)
    a.add_argument('--variant', type=int, default=0)
    a.add_argument('--tag', required=True)
    a.add_argument('--policy', type=Path, required=True)
    a.add_argument('--prefix', type=Path)
    a.add_argument('--replay', type=Path)
    a.add_argument('--frames', type=int, default=6000)
    a.add_argument('--audit', action='store_true')
    a.add_argument('--timeout', type=int, default=150)
    v = a.parse_args()
    assert v.character in (1, 2, 3, 4)
    assert v.variant == 0 or (v.character == 3 and v.variant == 1)
    assert not (v.prefix and v.replay)
    assert not v.replay or v.audit
    used = workspace_bytes(ROOT)
    assert used + 64 * 1024 * 1024 < CAP_BYTES
    rom = ROOT / 'build/verification/route-five-kd/kb-mmc3/smb-crossover-mmc3.nes'
    assert sha(rom) == '4720972962f8faf6c8e45536f95001e79ae66c7141dcbfa09c768440fa039c00'
    out = ROOT / 'build/roster-through-2-2' / v.tag
    out.mkdir(exist_ok=False)
    shutil.copyfile(Path(__file__),out/'driver.py')
    for src, name in [(v.policy, 'policy.lua'), (ROOT/'tools/playthroughs/roster_harness.lua', 'harness.lua'), (ROOT/'tools/playthroughs/roster_audit.lua', 'audit.lua')]:
        shutil.copyfile(src, out/name)
    # Retain every possible local Lua dependency and bind the live files at
    # both ends of the run. Nested historical policies otherwise silently
    # depend on files outside the copied top-level policy.
    dependencies=sorted((ROOT/'tools/playthroughs').glob('*.lua'))
    dependency_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in dependencies}
    with zipfile.ZipFile(out/'policy-source-bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in dependencies:z.write(p,p.relative_to(ROOT).as_posix())
    # The harness/audit/top policy run from immutable packet copies. Only
    # transitive dofile dependencies still read from the shared source tree.
    executed = {}
    pending = [v.policy.resolve()]
    visited = set()
    while pending:
        dependency = pending.pop()
        if dependency in visited: continue
        visited.add(dependency)
        content = dependency.read_text(encoding='utf-8-sig')
        for name in re.findall(r'/tools/playthroughs/([A-Za-z0-9_-]+\.lua)', content):
            child = ROOT/'tools/playthroughs'/name
            executed[child.relative_to(ROOT).as_posix()] = sha(child)
            pending.append(child)
    raw=(out/'policy.lua').read_text(encoding='utf-8-sig')
    guard='''\nlocal function kdread(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
emu.addEventCallback(function()
 if kdread('OperMode')==1 and kdread('OperMode_Task')==3 and kdread('GameEngineSubroutine')==8 then
  assert(kdread('SelectedCharacter')==ROSTER_CONFIG.character,'Actual selected identity')
  assert(kdread('CrossoverBehaviorVersion')==0,'Actual Easy behavior')
  if ROSTER_CONFIG.character==3 then assert(kdread('BillVariant')==ROSTER_CONFIG.variant,'Actual Bill/Lance alternate')end
 end
end,emu.eventType.endFrame)
return kdchoose
'''
    (out/'policy.lua').write_text('local kdchoose=(function()\n'+raw+'\nend)()\n'+guard,encoding='utf-8')
    cfg = dict(character=v.character, variant=v.variant, mapper='mmc3', limit=v.frames,
               out=out.as_posix()+'/', record=False, allowDeaths=False,
               policy=(out/'policy.lua').as_posix(),
               audit=(out/'audit.lua').as_posix() if v.audit else None,
               prefix=v.prefix.resolve().as_posix() if v.prefix else None,
               replay=v.replay.resolve().as_posix() if v.replay else None,
               workspaceCapBytes=CAP_BYTES)
    def lua(x): return 'nil' if x is None else str(x).lower() if isinstance(x, bool) else json.dumps(x)
    script=out/('run-'+v.tag+'.lua')
    script.write_text('ROSTER_CONFIG={\n'+''.join(f'{k}={lua(x)},\n' for k,x in cfg.items())+'}\ndofile('+json.dumps((out/'harness.lua').as_posix())+')\n')
    m=dict(rom_sha256=sha(rom), config=cfg, full_frame_audit=v.audit,
           controller_only=True, memory_or_register_writes=False,
           verified_through_2_2=False, workspace_bytes_before=used,
           driver_sha256=sha(out/'driver.py'),
           policy_dependency_hashes=dependency_hashes,
           executed_shared_dependency_hashes=executed,
           policy_bundle_sha256=sha(out/'policy-source-bundle.zip'),
           hashes={n:sha(out/n) for n in ['policy.lua','harness.lua','audit.lua',script.name]})
    for name in ['prefix','replay']:
        p=getattr(v,name)
        if p:m[name+'_sha256']=sha(p)
    (out/'manifest.json').write_text(json.dumps(m,indent=2))
    rc=run_mesen.run(script,rom,timeout=v.timeout,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    m['policy_dependencies_unchanged']=all(sha(ROOT/p)==digest for p,digest in executed.items())
    assert m['policy_dependencies_unchanged'],'Executed policy sources changed during run'
    if (out/'result.json').exists():
        m['result']=json.loads((out/'result.json').read_text())
        r=m['result']
        m['verified_through_2_2']=bool(rc==0 and v.replay and v.audit and r.get('cleared') and r.get('all_six_stages') and not r.get('failure') and r.get('deaths')==0)
    m['exit']=rc
    for n in ['inputs.csv','trace.csv','events.csv']:
        if (out/n).exists():m[n+'_sha256']=sha(out/n)
    (out/'manifest.json').write_text(json.dumps(m,indent=2))
    print(json.dumps(dict(output=str(out),result=m.get('result'),verified=m['verified_through_2_2'])),flush=True)
    return rc

if __name__=='__main__':raise SystemExit(main())
