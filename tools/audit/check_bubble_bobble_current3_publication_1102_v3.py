"""Re-run actual current publisher and lag-NMI cuts for the nine-page proposal."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'build/bubble-bobble-source-1101-v1'
ROM=R/'build/excitebike-pose-1101-v3/current3.nes'
PIN='37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c'


def main():
 raw=ROM.read_bytes();assert hashlib.sha256(raw).hexdigest()==PIN
 original=R/'tools/audit/check_metal_storm_chr_publication_1101_v10.py'
 cp=R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json'
 dp=R/'build/metal-storm-chr-closure-1101-v10/source-domains.json'
 cur=json.loads(cp.read_text());changed=[]
 for s in cur['native_spans']:
  now=raw[s['offset']:s['offset']+s['size']]
  if now!=bytes.fromhex(s['hex']):
   assert s['name']=='MaaLagChrGuard'and now.hex()=='ad0260d006ad0a73c902603860eaeaea'
   changed.append(dict(name=s['name'],old=s['hex'],new=now.hex()));s['hex']=now.hex()
 cur['current_ROM_sha256']=PIN
 source=original.read_text()
 substitutions={
  "OUT=ROOT/'build/metal-storm-chr-closure-1101-v10'":"OUT=ROOT/'build/bubble-bobble-source-1101-v1'",
  'TARGETS=set([247,248,249,250]+list(range(494,503))+list(range(827,832)))':'TARGETS={301,305,337,362,363,440,819,666,441}',
  "cp=OUT/'current-consumer-inputs.json';cur=json.loads(cp.read_text());domains=json.loads((OUT/'source-domains.json').read_text());assert domains['passed'];raw=(ROOT/'build/kirby-owner-main-1101-v2/candidate.nes').read_bytes();assert hashlib.sha256(raw).hexdigest()==cur['current_ROM_sha256']":"cp=CURPATH;cur=CUR;domains=json.loads(DOMAINPATH.read_text());assert domains['passed'];raw=ROM.read_bytes();assert hashlib.sha256(raw).hexdigest()==cur['current_ROM_sha256']",
  'lowtests=list(range(238,247))+list(range(59,64))':'lowtests=sorted({p&255 for p in TARGETS})',
  'for oldpage in[493,832]:':'for oldpage in[493,724,832]:',
  'for rawchar in range(1,36):':'for rawchar in range(1,39):',
  'assert {500,501,502,827,828,829,830,831}<=set(transient_targets),transient_targets':'assert TARGETS<=set(transient_targets),transient_targets',
  "OUT/'source-domains.json'":'DOMAINPATH',
 }
 for a,b in substitutions.items():assert source.count(a)>=1,a;source=source.replace(a,b)
 env=dict(__file__=str(original),__name__='bb_current_publication',CUR=cur,CURPATH=cp,DOMAINPATH=dp,ROM=ROM)
 exec(compile(source,str(original),'exec'),env);env['main']()
 q=json.loads((O/'publication-CPU-controls.json').read_text());assert q['passed']
 q.update(current_native_span_changes=changed,adapted_test_SHA256=hashlib.sha256(source.encode()).hexdigest(),wrapper_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Actual current379590 setter/publisher/native-menu-clear and lag NMI/RTI instruction cuts, all9 proposed physical pages included as unpublished transient pairs. Audio child is an explicit return port; no new owner loader/admission/retirement or native emulator qualification. Separate finite-domain and owner-retirement evidence required before grant.')
 (O/'publication-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
