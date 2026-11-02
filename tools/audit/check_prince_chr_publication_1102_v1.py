"""Reexecute current setter/menu/lag-NMI cuts for Prince's pooled proposal.

No ROM mutation or resource grant. The audio child remains the existing
explicit return port; real mapper/publisher/guard/RTI instructions execute.
"""
from pathlib import Path
import hashlib,json
import audit_prince_pool_1102_v1 as A
R,O=A.R,A.O


def main():
 assert A.sha(A.ROM)==A.SHA
 original=R/'tools/audit/check_metal_storm_chr_publication_1101_v10.py'
 cp=R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json'
 dp=R/'build/metal-storm-chr-closure-1101-v10/source-domains.json'
 raw=A.ROM.read_bytes();cur=json.loads(cp.read_text());changed=[]
 for span in cur['native_spans']:
  actual=raw[span['offset']:span['offset']+span['size']]
  if actual!=bytes.fromhex(span['hex']):
   assert span['name']=='MaaLagChrGuard'
   assert actual.hex()=='ad0260d006ad0a73c902603860eaeaea'
   changed.append(dict(name=span['name'],old=span['hex'],new=actual.hex()))
   span['hex']=actual.hex()
 cur['current_ROM_sha256']=A.SHA
 source=original.read_text()
 replacements={
  "OUT=ROOT/'build/metal-storm-chr-closure-1101-v10'":"OUT=ROOT/'build/prince-actor-1101-v1'",
  'TARGETS=set([247,248,249,250]+list(range(494,503))+list(range(827,832)))':'TARGETS=set('+repr(A.POOL)+')',
  "cp=OUT/'current-consumer-inputs.json';cur=json.loads(cp.read_text());domains=json.loads((OUT/'source-domains.json').read_text());assert domains['passed'];raw=(ROOT/'build/kirby-owner-main-1101-v2/candidate.nes').read_bytes();assert hashlib.sha256(raw).hexdigest()==cur['current_ROM_sha256']":"cp=CURPATH;cur=CUR;domains=json.loads(DOMAINPATH.read_text());assert domains['passed'];raw=ROM.read_bytes();assert hashlib.sha256(raw).hexdigest()==cur['current_ROM_sha256']",
  'lowtests=list(range(238,247))+list(range(59,64))':'lowtests='+repr(sorted({p&255 for p in A.POOL})),
  'for oldpage in[493,832]:':'for oldpage in[493,724,832]:',
  'for rawchar in range(1,36):':'for rawchar in range(1,38):',
  'assert {500,501,502,827,828,829,830,831}<=set(transient_targets),transient_targets':'assert TARGETS<=set(transient_targets),transient_targets',
  "OUT/'source-domains.json'":'DOMAINPATH',
 }
 for old,new in replacements.items():assert old in source,old;source=source.replace(old,new)
 env=dict(__file__=str(original),__name__='prince_publication_check',CUR=cur,CURPATH=cp,DOMAINPATH=dp,ROM=A.ROM)
 exec(compile(source,str(original),'exec'),env);env['main']()
 q=json.loads((O/'publication-CPU-controls.json').read_text())
 q.update(test_source_SHA256=hashlib.sha256(source.encode()).hexdigest(),wrapper_SHA256=A.sha(Path(__file__)),current_native_span_changes=changed,proposed_pages=A.POOL,scope='Current typed setter/menu restore/lag-NMI instruction cuts including all42 proposed pages as unpublished transient pairs. Actual audio child is an explicit return port. This proves the publication protocol, not complete gameplay reader closure or a resource grant.')
 (O/'publication-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
