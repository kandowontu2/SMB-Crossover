"""One compact successor source/negative checkpoint, with frozen inputs retained."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/prince-actor-1101-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 prior={}
 for version,stem in [(47,'native-battle'),(63,'native-collision')]:
  q=json.loads((O/f'{stem}-checkpoint-v{version}.json').read_text());assert sha(O/f'{stem}-source-v{version}.zip')==q['checkpoint_SHA256']
  for name in q['explicit_source_commit_files']:assert sha(R/name)==q['member_SHA256'][name],name
  prior[str(version)]=q['checkpoint_SHA256']
 source=[]
 for version in [*range(67,95),96]:
  found=list((R/'tools/audit').glob(f'*prince*1102_v{version}.py'));assert len(found)==1,(version,found);source+=found
 source += [Path(__file__),R/'docs/qa/prince-post-return-1102-v95.md']
 generated=['player-pipeline-CPU-v67.json','native-render-CPU-v68.json','native-lifecycle-negative-v69.json','native-lifecycle-measurement-v70.json','native-lifecycle-CPU-v71.json','native-stack-negative-v72.json','death-ack-measurement-v73.json','death-ack-stack-negative-v74.json','deferred-death-measurement-v75.json','deferred-death-negative-v76.json','deferred-death-CPU-v77.json','post-return-measurement-v78.json','deferred-death-measurement-v78.json','deferred-death-CPU-v79.json','post-return-stack-negative-v80.json','post-return-foreign-CPU-v81.json','post-return-boundary-v82.json','tag-transport-CPU-v84.json','post-return-stack-negative-v85.json','post-return-stack-negative-v86.json','post-return-stack-negative-v88.json','cold-link-storage-v87.json','native-stack-CPU-v89.json','post-return-cold-CPU-v90.json','post-return-lifetime-proposal-v91.json','post-return-nested-IRQ-CPU-v92.json','post-return-respawn-negative-v93.json','post-return-life-negative-v94.json','native-contact-pit-CPU-v96.json']
 for version in [70,75,78]:generated += [f'native-{name}-v{version}.bin'for name in ['runtime','metadata','state']]
 generated += ['native-services-v70.s','native-audio-v70.s','native-services-v75.s','native-audio-v75.s','native-public-v75.s','native-labels-v78.json','native-fresh-v78.bin','native-contact-v78.bin','post-return-second-v78.bin','cold-pool-v87.bin']
 for name in ['services','battle','proxy','public','policies','audio','small']:generated += [f'native-{name}-v78.{s}'for s in ['s','cfg','lbl','bin']]
 for stem in ['post-return-v78','deferred-selector-v79','cold-worker-v87']:generated += [f'{stem}.{s}'for s in ['s','cfg','lbl','bin']]
 generated += [f'native-{name}-v87.lzdict'for name in ['runtime','metadata','state_code']]
 files={p.relative_to(R).as_posix():p.read_bytes()for p in source}
 files.update({'generated/'+name:(O/name).read_bytes()for name in generated})
 assert len(files)==len(source)+len(generated)and all(not name.endswith(('.nes','.dbg','.o','.png'))for name in files)
 target=O/'post-return-source-v95.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name,data in sorted(files.items()):z.writestr(name,data)
 with zipfile.ZipFile(target)as z:assert z.testzip()is None and all(z.read(name)==data for name,data in files.items())
 q=dict(passed=True,source_checkpoint_only=True,ROM_written=False,installed=False,menu_admitted=False,checkpoint=target.relative_to(R).as_posix(),checkpoint_SHA256=sha(target),checkpoint_bytes=target.stat().st_size,checkpoint_members=len(files),requires_existing_frozen_checkpoint_SHA256=prior,all_prior_frozen_source_hashes_unchanged=True,explicit_source_commit_files=[p.relative_to(R).as_posix()for p in source],member_SHA256={name:hashlib.sha256(data).hexdigest()for name,data in files.items()},binding_scope='Frozen47/63 are read-only dependencies, never recursively rehydrated or copied into this successor. Current source-injected old16a9 CPU proof only; v91 hooks/lifetimes ungranted. Root current9cf jointgate/currentcookie/carry correction rebase and actual full cold/respawn/native remain pending.',lag_correction='Historical positiveNmiDisable1 tests were regularNMI, including68/72; preserve sources/receipts but supersede their lag wording. ActualFF branch trace89 and6690 nestedIRQ92 are the lag qualification.',negative_scope='69/72/74 actual stack corruption;76 actual C09E ROM-write ingress;80/82/85/86 regularNMI observer/context distinctions;88 actual native AudioUpdate07DA difference;93 old cold500k harness bound after earned life;94 observer incorrectly required KillPlayer on direct native pit. No negative is relabeled as native gameplay pass.')
 (O/'post-return-checkpoint-v95.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['explicit_source_commit_files','member_SHA256']}))


if __name__=='__main__':main()
