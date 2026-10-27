"""Freeze corrected finite Bill/Lance preparation with all source-only proofs."""
from pathlib import Path
import argparse,json
from final_bill_lance_hard_gallery_source_v1 import ROOT,D,SHA,sha,put


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old=a.ready/'proof.json';assert sha(old)=='ec6a0cd28366d06a897f6f753cc0fb9c430327249b3b4939e2c749b0a5c1d9a2'
 q=json.loads(old.read_text());assert q['prepared']and q['observer_version']==2 and not q['native_run']and q['ROM_sha256']==SHA
 source=json.loads((a.ready/'manifest.json').read_text());bindings={Path(z['path']):z['sha256']for z in source['bindings']}
 for f,h in bindings.items():assert sha(f)==h,f
 receipts=[a.ready/n for n in ['render-controls-v1/proof.json','render-rejection-controls-v1/proof.json','render-rejection-controls-v1/transformation.json','additional-controls-v2/proof.json','additional-controls-v2/spatial-contacts.json','additional-controls-v2/finalizer-models.json']]
 for f in receipts:
  z=json.loads(f.read_text());assert z['passed']and not z.get('native_run',False),f
 render=json.loads(receipts[0].read_text());negative=json.loads(receipts[1].read_text());controls=json.loads(receipts[3].read_text())
 assert render['cases']==negative['cases']==16 and render['complete_RemainingDraw_calls']==negative['complete_RemainingDraw_calls']==64
 assert sum(x['admitted_advanced_draws']for x in render['rows'])==32 and sum(x['admitted_advanced_draws']for x in negative['rows'])==0
 assert controls['actual_spatial_cases']==28 and controls['synthetic_finalizer_cases']==15
 for f in receipts:
  z=json.loads(f.read_text())
  deps=z.get('bindings',{})
  if isinstance(deps,list):deps={x['path']:x['sha256']for x in deps}
  for p,h in deps.items():assert sha(p)==h,p;bindings[Path(p)]=h
 report=ROOT/'docs/qa/final-bill-lance-hard-gallery-prepared-2026-10-26.txt'
 extras={old,a.ready/'manifest.json',Path(__file__),report}|set(receipts)
 extras.update(f for f in a.ready.rglob('*')if f.is_file()and not f.is_relative_to(a.output))
 extras.update(ROOT/'tools/audit'/n for n in ['final_bill_lance_hard_gallery_controls_v1.py','final_bill_lance_hard_gallery_render_controls_v1.py','final_bill_lance_hard_gallery_render_rejection_controls_v1.py'])
 bindings.update({f:sha(f)for f in extras})
 for f,h in bindings.items():assert sha(f)==h,f
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=h,bytes=f.stat().st_size)for f,h in sorted(bindings.items())]))
 commands={z['profile']:'python -B tools/audit/final_bill_lance_hard_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --profile '+z['profile']+' --native-grant'for z in q['profiles']}
 final=q|dict(native_granted=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),commands=commands,
  supersedes_only_unrun_observer_preparation=True,prior_original_ready_preserved=str(old),prior_original_ready_sha256=sha(old),
  complete_source_receipts=[dict(path=str(f),sha256=sha(f))for f in receipts],report_sha256=sha(report),freeze_tool_sha256=sha(__file__))
 put(a.output/'proof.json',final)
 put(a.output/'commands.json',commands)
 print(json.dumps(dict(prepared_only=True,native_run=False,proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),commands=commands)))


if __name__=='__main__':main()
