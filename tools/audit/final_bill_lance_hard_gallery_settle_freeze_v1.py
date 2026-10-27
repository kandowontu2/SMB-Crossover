"""Freeze the one-guard source successor, all negatives and review payload."""
from pathlib import Path
import argparse,difflib,json,shutil
from final_bill_lance_hard_gallery_source_v1 import D,ROOT,SHA,sha,put


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--public',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 prior=D/'final-bill-lance-hard-gallery-ready-v4';oldready=prior/'final-freeze-v1';negative=D/'final-bill-lance-hard-gallery-negative-v1'
 assert sha(a.ready/'proof.json')=='573c40248c9af37caf75bedf3ffe869c52f5bc5d11f8dda00b7bfdd8a1304cb1'
 q=json.loads((a.ready/'proof.json').read_text());assert q['prepared']and q['observer_version']==3 and not q['native_run']and q['ROM_sha256']==SHA
 assert sha(negative/'proof.json')=='546abdcd733efbb747b29d391194875ef41ed24abe774ed61918cb022fdc3e1b'
 before=(ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v2.lua').read_text();after=(ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua').read_text()
 old=" assert(r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Weapon upgrade remains the seeded mushroom form; no invented tier transform')"
 new=" if phase~='settle'then assert(r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Weapon upgrade remains the seeded mushroom form; no invented tier transform')end"
 assert before.count(old)==1 and after==before.replace(old,new,1)
 equality=[]
 for z in q['profiles']:
  current=Path(z['output']);previous=prior/'profiles'/z['profile']/'native'
  assert json.loads((current/'config.json').read_text())==json.loads((previous/'config.json').read_text())
  x=(previous/'run.lua').read_text().split('\n',1)[1];y=(current/'run.lua').read_text().split('\n',1)[1]
  assert x.count(old)==1 and y==x.replace(old,new,1)
  assert (current/'inherited-NMI-stack-APU-guards.lua').read_bytes()==(previous/'inherited-NMI-stack-APU-guards.lua').read_bytes()
  assert not(current/'launch.json').exists()
  equality.append(dict(profile=z['profile'],config_semantically_exact=True,whole_generated_body_single_assertion_wrapper_only=True,all_previous_guards_literal=True,game_ROM_exact=True,native_run=False))
 models=a.ready/'settle-controls-v2/proof.json';extra=a.ready/'additional-controls-v1/proof.json'
 for f in [models,extra]:assert json.loads(f.read_text())['passed']and not json.loads(f.read_text())['native_run']
 assert len(json.loads(models.read_text())['models'])==10
 assert json.loads(extra.read_text())['actual_spatial_cases']==28
 bindings={}
 for manifest in [a.ready/'manifest.json',negative/'manifest.json']:
  for z in json.loads(manifest.read_text())['bindings']:
   assert sha(z['path'])==z['sha256'],z['path'];bindings[Path(z['path'])]=z['sha256']
 for f in [models,extra]:
  for name,h in json.loads(f.read_text())['bindings'].items()if isinstance(json.loads(f.read_text())['bindings'],dict)else[(z['path'],z['sha256'])for z in json.loads(f.read_text())['bindings']]:
   assert sha(name)==h,name;bindings[Path(name)]=h
 report=ROOT/'docs/qa/final-bill-lance-hard-gallery-settle-2026-10-26.txt'
 files={Path(__file__),report,a.ready/'proof.json',a.ready/'manifest.json',negative/'proof.json',negative/'manifest.json'}
 files.update(f for f in a.ready.rglob('*')if f.is_file()and not f.is_relative_to(a.output))
 files.update([ROOT/'tools/audit/final_bill_lance_hard_gallery_settle_controls_v1.py',ROOT/'tools/audit/final_bill_lance_hard_gallery_negative_freeze_v1.py'])
 bindings.update({f:sha(f)for f in files})
 patch=''.join(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile='native_v2.lua',tofile='native_v3.lua'))
 (a.output/'observer-only.patch').write_text(patch,encoding='utf-8')
 put(a.output/'source-equality.json',dict(passed=True,source_only=True,native_run=False,game_code_changed=False,profiles=equality,source_art_owner_unchanged=True,old64positive_and64negative_render_cells_are_historical_v4=True,actual_native_v4_Bill_remains_FALSE=True,Lance_remains_unrun=True))
 bindings.update({f:sha(f)for f in a.output.iterdir()if f.is_file()})
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=h,bytes=f.stat().st_size)for f,h in sorted(bindings.items())]))
 commands={z['profile']:'python -B tools/audit/final_bill_lance_hard_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --profile '+z['profile']+' --native-grant'for z in q['profiles']}
 final=q|dict(native_granted=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),commands=commands,
  actual_v4_native_remains_FALSE=True,old_Lance_grant_not_portable=True,cold_settle_source_models=10,fresh_spatial_controls=28,fresh_finalizer_models=15,
  source_equality_sha256=sha(a.output/'source-equality.json'),report_sha256=sha(report),freeze_tool_sha256=sha(__file__))
 put(a.output/'proof.json',final);put(a.output/'commands.json',commands)
 a.public=a.public.resolve();a.public.mkdir(parents=True,exist_ok=False)
 native=prior/'profiles/bill-hard/native'
 payload={
  'ready/proof.json':a.output/'proof.json','ready/manifest.json':a.output/'manifest.json','ready/commands.json':a.output/'commands.json',
  'observer-only.patch':a.output/'observer-only.patch','source-equality.json':a.output/'source-equality.json',
  'observer/native_v2.lua':ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v2.lua','observer/native_v3.lua':ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua',
  'source-controls/cold-settle-flow.json':models,'source-controls/additional28-and15.json':extra,
  'source-controls/current-static-and-terrain.json':a.ready/'static-controls.json',
  'retained-native-FALSE/native-proof.json':native/'proof.json','retained-native-FALSE/first-failure.json':native/'first-failure.json',
  'retained-native-FALSE/cadence.csv':native/'bill-cadence.csv','retained-native-FALSE/freeze-proof.json':negative/'proof.json',
  'retained-native-FALSE/actual-first-failure.png':negative/'actual-first-failure.png',
  'old-grants-not-portable/Bill.json':oldready/'ROOT-grant-bill-hard.json','old-grants-not-portable/Lance-unused.json':oldready/'ROOT-grant-lance-hard.json',
  'reports/original-prepared.txt':ROOT/'docs/qa/final-bill-lance-hard-gallery-prepared-2026-10-26.txt','reports/settle-successor.txt':report,
  'source-model-negative/initial-lexical-scope-failure.json':a.ready/'settle-controls-v1/failure.json'}
 rows=[]
 for name,f in payload.items():
  target=a.public/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target);assert sha(target)==sha(f)
  rows.append(dict(path=name,source=str(f),sha256=sha(f),bytes=f.stat().st_size))
 owned=sorted(str(f.relative_to(ROOT)).replace('\\','/')for f in(ROOT/'tools/audit').glob('final_bill_lance_hard_gallery*')if f.is_file())
 owned+=['docs/qa/final-bill-lance-hard-gallery-prepared-2026-10-26.txt','docs/qa/final-bill-lance-hard-gallery-settle-2026-10-26.txt']
 (a.public/'OWNED-FILES.txt').write_text('\n'.join(owned)+'\n'+str(a.public.relative_to(ROOT)).replace('\\','/')+'/\n',encoding='utf-8')
 (a.public/'README.txt').write_text('''SOURCE-ONLY SETTLE SUCCESSOR; ORIGINAL NATIVE BILL FALSE / LANCE UNRUN.
No ROM or game source change. The exact3b controlled seven-case gallery
stopped at its first cold settle finish: a later seeded-form assertion ran
before its explicit update30 seed. Original native failure/grants remain;
unused oldLance grant is NOT portable. ONE new assertion wrapper exempts
only settle; update30 already changes phaseNext, so same/postseed finish
still strictly requires status1/no transform. Ten literal full-flow models,
fresh28compiled contacts/15finalizers and fresh static/terrain controls pass.
The entire controller/mechanics/art-owner/guard body is reverse-exact apart
from that wrapper; prior64positive/64synthetic-rejection render controls stay
historicalv4 evidence, not new runs. Two future separately granted profiles
are PREPARED ONLY; no retries or native success/adoption is claimed here.
This payload excludes ROM/emulator/settings/raw PPU/APU/log media. Complete
external path/hash bindings are retained for local reproduction and review.
OWNED-FILES is ROOT's explicit stable review list, not a Git operation.
''',encoding='utf-8')
 put(a.public/'REVIEW-FILES.json',dict(first_actual_failure=['retained-native-FALSE/native-proof.json','retained-native-FALSE/cadence.csv','retained-native-FALSE/actual-first-failure.png'],minimal_correction=['observer-only.patch','source-equality.json'],controls=['source-controls/cold-settle-flow.json','source-controls/current-static-and-terrain.json'],scope=['reports/settle-successor.txt','README.txt']))
 put(a.public/'manifest.json',dict(prepared_only=True,native_run=False,original_native_aggregate_FALSE=True,ROM_sha256=SHA,new_readiness_sha256=sha(a.output/'proof.json'),payloads=rows,stable_owned_files=[dict(path=f,sha256=sha(ROOT/f),bytes=(ROOT/f).stat().st_size)for f in owned],checker_sha256=sha(__file__)))
 total=sum(f.stat().st_size for f in a.public.rglob('*')if f.is_file())
 print(json.dumps(dict(prepared_only=True,native_run=False,proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),public_bytes=total,public_manifest_sha256=sha(a.public/'manifest.json'),owned_files=len(owned),commands=commands)))


if __name__=='__main__':main()
