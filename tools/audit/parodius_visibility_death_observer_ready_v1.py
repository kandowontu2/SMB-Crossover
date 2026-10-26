"""Freeze finite source-only death-observer readiness; no native grant/run."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','records-cpu','observer-cpu','area-cpu','negative-final','parent-ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);files=set();receipts={}
 for n in ['records_cpu','observer_cpu','area_cpu']:
  folder=getattr(a,n);q=json.loads((folder/'proof.json').read_text());assert q['passed'] and not q['native_run'] and q['ROM_sha256']==SHA
  receipts[n]=dict(path=str(folder/'proof.json'),sha256=sha(folder/'proof.json'))
  files.update(f.resolve()for f in folder.rglob('*')if f.is_file())
  for f,h in q.get('bindings',{}).items():assert sha(f)==h;files.add(Path(f).resolve())
  if (folder/'manifest.json').exists():
   for f,h in json.loads((folder/'manifest.json').read_text()).items():assert sha(f)==h;files.add(Path(f).resolve())
 for folder in [a.negative_final,a.parent_ready]:
  ledger=json.loads((folder/'manifest.json').read_text())
  for f,h in ledger.items():assert sha(f)==h;files.add(Path(f).resolve())
  files.update(f.resolve()for f in folder.rglob('*')if f.is_file())
 files.update(f.resolve()for f in a.preparation.rglob('*')if f.is_file())
 z=json.loads((a.preparation/'death/preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256'] and sha(script.with_name('candidate.nes'))==SHA
 assert not(script.parent/'proof.json').exists() and not(script.parent/'lifecycle-proof.json').exists()
 cfg=json.loads(script.with_name('config.json').read_text());assert cfg['mode']==0 and cfg['variant']==1 and cfg['limit']==2200
 for f,h in z['dependencies'].items():assert sha(f)==h;files.add(Path(f).resolve())
 oldenv=json.loads((a.parent_ready/'environment.json').read_text());envdir=a.output/'environment';envdir.mkdir()
 for field in ['emulator','core','worker_settings','user_settings']:
  f=Path(oldenv[field]);assert sha(f)==oldenv[field+'_sha256'];files.add(f.resolve())
  if field.endswith('settings'):shutil.copy2(f,envdir/(field+'.json'))
 (a.output/'environment.json').write_text(json.dumps(oldenv,indent=2)+'\n');files.update(f.resolve()for f in a.output.rglob('*')if f.is_file())
 toolnames=['parodius_visibility_death_observer_ready_v1.py','parodius_visibility_death_observer_prepare_v1.py',
            'parodius_visibility_death_observer_cpu_v1.py','parodius_visibility_death_records_cpu_v1.py',
            'parodius_visibility_death_records_cpu_v2.py','parodius_visibility_area_controller_cpu_v1.py',
            'parodius_visibility_hud_static_observer_v1.lua','parodius_visibility_hud_static_observer_v2.lua',
            'parodius_visibility_hud_transition_run_v1.py']
 files.update((ROOT/'tools/audit'/n).resolve()for n in toolnames)
 failed=a.output.parent/'parodius-hud-death-records-cpu-v1';files.update(f.resolve()for f in failed.rglob('*')if f.is_file())
 report=ROOT/'docs/qa/parodius-death-observer-source-2026-10-26.txt';files.add(report.resolve())
 ledger={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(ledger,indent=2)+'\n')
 q=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,
        profiles=[dict(kind='death',limit=2200,actual_mode_required=0,actual_variant_required=1,packet=str((a.preparation/'death').resolve()),
                       preparation_sha256=sha(a.preparation/'death/preparation.json'),script_sha256=sha(script))],
        receipts=receipts,original_negative_final_sha256=sha(a.negative_final/'proof.json'),
        original131live_records_exact=True,death_records_narrowly_owned=13,environment=oldenv,
        manifest_bindings=len(ledger),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),tool_sha256=sha(Path(__file__)),
        stable_command='python -B tools/audit/parodius_visibility_hud_transition_run_v1.py --ready "'+a.output.as_posix()+'" --profile death --native-grant',
        limits='SOURCE-ONLY readiness for ONE unchanged-controller death2200 observer successor. No grant, retry, native timing/death/new-life success or production/adoption permission. Original death/area failures remain false. Area controller/source window diagnosis is a separate unrun followup, not a second launch profile. Existing hardware/PPU/NMI/IRQ/scroll/font/generation guards remain; original RTI callback denotes entry before RTI.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=q['manifest_sha256'],bindings=len(ledger),report_sha256=q['report_sha256'],script_sha256=sha(script)),indent=2))


if __name__=='__main__':main()
