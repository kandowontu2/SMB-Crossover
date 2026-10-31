"""Freeze exact lossless factor/source evidence; no ability implementation."""
from pathlib import Path
import hashlib,json,re,zipfile
R=Path(__file__).resolve().parents[2];P=R/'build/smb3plus-low-table-factor-host-1031-v4';J=P/'joint'
O=R/'docs/qa/checkpoints/2026-10-31/smb3plus-low-table-factor-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
def check(p):
 q=json.loads(p.read_text(encoding='utf-8'))
 if'passed'in q:assert q['passed'],p
 for n,h in q.get('bindings',{}).items():assert sha(n)==h,(p,n)
 return q

def main():
 assert not O.exists();assert sha(J/'candidate.nes')=='e54b91fa15b335bb17fd24fa7a0b667ef50bf31c8fad900d6c1a1ec38526116a'
 receipts=[P/n for n in['source-stage.json','regressions-factor-controls-v1.json','helper-factor-controls-v1.json','pixels-factor-controls-v1.json','menu-factor-controls-v1.json','whole-factor-controls-v1.json','foreign-factor-controls-v1.json','vectors-factor-controls-v1.json','refs-consumer-controls-v1.json','vectors-consumer-controls-v1.json','cf-67-byte-proposal.json']]
 for p in receipts:check(p)
 parent=R/'docs/qa/checkpoints/2026-10-31/smb3plus-current66-source-v1/handoff.json';check(parent)
 deps=set()
 for name in['main.dep','union.dep']:
  body=(J/name).read_text().split('\t',1)[1].splitlines()[0]
  for item in re.split(r'(?<!\\) +',body):
   item=item.replace('\\ ',' ').strip()
   if not item:continue
   p=Path(item);assert p.is_file(),item;deps.add(p.resolve())
 logs=[P/(n+'.json')for n in['main-build','union-build','final-link']];inputs=set()
 for p in logs:
  q=json.loads(p.read_text());assert q['returncode']==0 and q['validation']['outputs_validated_before_execution']
  for word in q['command']:
   z=Path(word)
   if z.is_file()and z.suffix in['.o','.s','.cfg']:inputs.add(z.resolve())
 tools=[Path(__file__),R/'tools/audit/check_smb3plus_low_table_factor_1031_v1.py',R/'tools/audit/smb3plus_low_table_consumer_controls_1031_v1.py']
 tools +=[R/f'tools/audit/prepare_smb3plus_low_table_factor_host_1031_v{i}.py'for i in range(1,5)]
 negatives=[R/'build/smb3plus-low-table-factor-host-1031-v1/preparation-negative.json',R/'build/smb3plus-low-table-factor-host-1031-v2/main-build.json',R/'build/smb3plus-low-table-factor-host-1031-v3/label-audit-negative.json']
 files=set(receipts+logs+tools+negatives+[J/'private.cfg',J/'main.dep',J/'union.dep',parent])
 files.update(p for p in deps if p.suffix.lower()not in['.nes','.o','.exe'])
 files.update(p for p in J.rglob('*')if p.is_file()and p.suffix in['.s','.inc','.cfg'])
 O.mkdir(parents=True)
 own=dict(actual_code_data_changes=[str(J/'src/smb3_mario_art.inc'),str(J/'src/smb3_mario_render.s')],new_private_root=str(P),installed_or_canonical_edits=[],native=False,new_lease=False,readiness_changes=False,reclaim_available_only_in_this_source_successor=True,CF67_proposal_not_reserved=True,source_pointer_exception='Only actualbank90 Chr+12/+17 R0/R1 stores classified by compiled expected pointers. Other ordered writes, finalAXYP/stack/maps and finalhighpointer exact.',preparation_negatives=[str(p)for p in negatives])
 put(O/'owned-files.json',own);files.add(O/'owned-files.json')
 (O/'README.txt').write_text('''Lossless SMB3+ low table factor on installed68 source01a4. Candidatee54b91fa changes439 owned bytes only. ExistingForm5Lo code, every otherpubliclabel/header/CHR/payload/cookie remains exact. Sevenlow pointers useForm0 plus sevenmod256 offsets; genuinecallerclampsX. Actual12B helper preserves X/Y/allP/resultA at typedcall, with23B footprint retained.

9072graphics and1344movement pairs pass.36288full64flag helper pairs and996 invalidform actualcaller cases pass.2156 donor pixel cases exact;112 preexistingdisabledKuribo records remain explicitly unsupported.2016 wholecontroller,81foreignmenus/768status,282completeMain (-3..0CPU),3364existingvectors and812pointer/helpervectors pass. No Mesen/native/install/performance/FPS claim.

Compilerrefs/realcaller bytes/source numeric-address consumers establish398 bytes unused in this successor:91:CE97..<CEE1,CF32..<CF83,CFD4..<D025,D076..<D0C7,D1BA..<D20B. Nothing allocated to anotherowner here. Root67B CFproposal mustcompose factor first; those bytes are LIVE oldtable data in installed01a4. Abilityimplementation absent and requires rootreviewed donor-source plan.
''',encoding='utf-8');files.add(O/'README.txt')
 archive=O/'source-and-controls.zip';members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)}
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(archive)as z:
  assert len(z.namelist())==len(members)
  for n,h in members.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 put(O/'source-members.json',members)
 bound=files|deps|inputs|{archive,O/'source-members.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl'}
 q=dict(status='FROZEN_LOSSLESS_LOW_TABLE_FACTOR_SOURCE_CPU_PASS',candidate=sha(J/'candidate.nes'),parent='01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9',source=True,native=False,installed=False,new_lease=False,qualified_same_owner_reclaim_bytes=398,CF67_reserved=False,ability_implemented=False,archive_members=len(members),archive_bytes=archive.stat().st_size,bindings={str(p.resolve()):sha(p)for p in sorted(bound)})
 put(O/'handoff.json',q);check(O/'handoff.json');print(json.dumps(dict(handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(q['bindings']),members=len(members),bytes=archive.stat().st_size)))
if __name__=='__main__':main()
