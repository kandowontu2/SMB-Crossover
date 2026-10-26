"""Prepare ONE unlaunched00fb pilot with exact completed731450 controls."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
CANDIDATE=D/'mm-proto-body-priority-v3'
BASELINE=D/'root-presentation450-731-v1'
FROZEN=CANDIDATE/'ready-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists()and not a.output.resolve().is_relative_to(R)
    receipt=FROZEN/'receipt.json'
    assert sha(receipt)=='4fc29c37dd31d0cd386bfc87bbdd009252e160b19dba6b757fbb012cc1710e6a'
    freeze=json.loads(receipt.read_text());assert freeze['passed']and not freeze['native_run']
    for rel,q in json.loads((FROZEN/'catalog.json').read_text()).items():assert sha(FROZEN/rel)==q['sha256'],rel
    for name,h in json.loads((FROZEN/'dependency-bindings.json').read_text()).items():assert sha(name)==h,name
    baseline=json.loads((BASELINE/'native-receipt.json').read_text());oldready=json.loads((BASELINE/'readiness.json').read_text())
    assert baseline['passed']and baseline['result']['ROM_sha256']=='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
    module=R/'tools/audit/presentation_timing_preflight_v1.lua'
    assert sha(module)==oldready['bindings'][str(module.resolve())]
    command=[sys.executable,'-B',str(R/'tools/audit/presentation_timing_prepare_v1.py'),'--candidate',str(CANDIDATE),'--expected-ROM-sha256',freeze['ROM_sha256'],'--output',str(a.output)]
    z=subprocess.run(command,cwd=R,capture_output=True,text=True)
    if not a.output.exists():a.output.mkdir(parents=True)
    put(a.output/'preparer-launch.json',dict(command=command,exit=z.returncode,stdout=z.stdout,stderr=z.stderr))
    assert z.returncode==0,z.stdout+z.stderr
    ready=a.output/'readiness.json';base=json.loads(ready.read_text());shutil.copyfile(ready,a.output/'base-readiness.json')
    assert(a.output/'prefix.csv').read_bytes()==(BASELINE/'prefix.csv').read_bytes()
    original=json.loads((BASELINE/'config.json').read_text());cfg=json.loads((a.output/'config.json').read_text())
    for name in ['limit','hooks','ram','smc']:assert cfg[name]==original[name],name
    assert cfg['limit']==450
    assert base['environment']==oldready['environment']
    plan='''ONE prepared native launch, not granted. Exact00fb body-priority candidate.
Baseline is the actual completed clean731450 run, not an older recording.
Controller prefix bytes, observer module, hook bytes/RAM/SMC config, hardware
settings, finite guard thresholds and450PPU-frame limit are exact to731.
Capture all275actual PPU frames176..450, raw source/destination256-byte DMA
pages and stamps, input polls, IRQ31/NMI/5SMC/AXY/SP/deadline guards. No new
observer code or weakened byte masks. Same genuine E008 completion hook.
Original source/CPU receipts remain separate, and all earlier negatives exact.

After the single run, preserve any failure; no automatic retry. Independently
compare real input masks/poll stamps, complete DMA counts and actual cumulative
completion epochs at matching captured visible-frame CPU cutoffs. No-harm or
matched-state claims require those observations; fixed input alone does not
prove identical update counts/positions. Inspect actual early-game body/shot
pixels only where gameplay is admitted. Existing baseline lacks full per-frame
CHR/palette/player-state ownership, so do not invent an opaque per-part oracle
or whole-route/Proto/charge/death/publication-fairness result. Any unseen scope
remains open. Owned+159..160CPUcycles and starvation tradeoff remain risks.
No adoption or settings/default/production mutation is part of this pilot.
'''
    (a.output/'PILOT-PLAN.txt').write_text(plan)
    deps={receipt,FROZEN/'catalog.json',FROZEN/'qualification.json',FROZEN/'dependency-bindings.json',FROZEN/'source.zip',Path(__file__),a.output/'base-readiness.json',a.output/'preparer-launch.json',a.output/'PILOT-PLAN.txt'}
    deps|={BASELINE/name for name in ['readiness.json','config.json','prefix.csv','native-receipt.json','result.json','launch.json','direct-index.csv','direct.argb','timing.jsonl']}
    bindings=base['bindings']|{str(q.resolve()):sha(q)for q in sorted(deps)}
    final=base|dict(native_run=False,native_grant=False,source_receipt_sha256=sha(receipt),matched_reference_ROM_sha256=baseline['ROM_sha256'],matched_reference_receipt_sha256=sha(BASELINE/'native-receipt.json'),baseline_capture_actual=True,prefix_module_hooks_RAM_SMC_environment_and_guard_limits_exact=True,new_observer_code=False,bindings=bindings,limits=plan)
    put(ready,final)
    catalog={q.name:dict(bytes=q.stat().st_size,sha256=sha(q))for q in sorted(a.output.iterdir())if q.is_file()}
    put(a.output/'preparation-catalog.json',catalog)
    result=dict(passed=True,prepared_only=True,native_run=False,native_grant=False,maximum_launches=1,maximum_workers=1,ROM_sha256=freeze['ROM_sha256'],readiness_sha256=sha(ready),catalog_sha256=sha(a.output/'preparation-catalog.json'),binding_count=len(bindings),command=base['command'],launcher=str(R/'tools/audit/presentation_timing_launch_v1.py'),launcher_sha256=sha(R/'tools/audit/presentation_timing_launch_v1.py'),preparer_sha256=sha(__file__))
    put(a.output/'preparation.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
