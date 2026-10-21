"""Successor Land review: bind each reached DEC-absolute cycle correction."""
from pathlib import Path
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent49-rush-h-a';O=V/'root49-rush-land-root-review-hx';W=V/'root49-rush-land-root-review-hw'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 assert not O.exists();O.mkdir()
 packet=H/'audio-freeze-ao.json';assert sha(packet)=='5733862cb1ac7f7dc3a1cc15062103aacb93ccbc219d6047e35505d30413380b';j=read(packet)
 aq=H/'audio-size-supplement-aq.json';assert sha(aq)=='b2d6a9b3ac10079071e4e326c7e7078195d8b64ccdca14ca4c2a91bb98cd61db';sizes=read(aq)
 cp=R/'build/checkpoints/roster-audit-v49-sophia-block-origin-hu/manifest.json';c=read(cp);assert sha(cp)=='e2018d6fa9524c466c8c3af88c2d7e02c80d283056ca70e853d1b8dab7a261a5'
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for n,h in j['source_catalog'].items():assert sha(R/j['source_path']/n)==h,n
 for n,z in j['artifacts'].items():assert sha(H/n)==z['sha256']and(H/n).stat().st_size==z['bytes'],n
 for n,z in j['receipts'].items():assert sha(H/n)==z['sha256']and(H/n).stat().st_size==z['bytes'],n
 assert(len(j['source_catalog']),len(j['artifacts']),len(j['receipts']))==(471,32,1201)
 for n,z in j['changes_from_frozen_RushC'].items():assert sha(H/j['overlay']/n)==z['after']
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+30000000<100000000000
 (O/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),packet_sha256=sha(packet),AQ_sha256=sha(aq),current_HU_sha256=sha(cp),workspace_before=used,global_cap=100000000000,phase_cap=30000000,reserve=10000000,HW_negative='First3native caller reports reexecute literally, but added cycle-equality check fails MMC3 world calls17..43 by3cycles. Frozen AO never claimed universal native/instruction-cycle identity. All HW files retained.'),indent=2)+'\n',encoding='utf-8')
 groups=[]
 for number,z in enumerate(j['reproduction']):
  assert sha(H/z['tag']/'binding.json')==z['actual_binding_sha256']
  original=H/'review_ad.py';code=original.read_text(encoding='utf-8');old="dest=H/f'caller-review-{a.suffix}.json'";assert code.count(old)==1
  modified=code.replace(old,"dest=ROOT_OUTPUT/f'caller-review-{a.suffix}.json'")
  anchor="m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)";assert modified.count(anchor)==1
  patched=anchor+'''
ROOT_OLD_CPU=m.q.core.NesMPU
assert ROOT_OLD_CPU.cycletime[0xce]==3
ROOT_CPUS=[]
class RootCycleCPU(ROOT_OLD_CPU):
 cycletime=list(ROOT_OLD_CPU.cycletime);cycletime[0xce]=6
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.root_dec=[];ROOT_CPUS.append(self)
 def step(self):
  if self.memory[self.pc]==0xce:
   self.root_dec.append(dict(PC=self.pc,bank=self.memory.banks[self.pc&0xe000],opcode=0xce,old_cycles=3,correct_cycles=6))
  return super().step()
m.q.core.NesMPU=RootCycleCPU
'''
  modified=modified.replace(anchor,patched)
  if number==0:(O/'review_ad.py.txt').write_text(modified,encoding='utf-8')
  previous=sys.argv;suffix=f'{number:02d}';sys.argv=[str(original),'--tag',z['tag'],'--suffix',suffix];stream=io.StringIO();namespace={'__name__':'__main__','__file__':str(original),'ROOT_OUTPUT':O}
  try:
   with contextlib.redirect_stdout(stream):exec(compile(modified,str(original),'exec'),namespace)
  finally:
   sys.argv=previous
   if 'ROOT_OLD_CPU'in namespace:namespace['m'].q.core.NesMPU=namespace['ROOT_OLD_CPU']
  (O/f'caller-{number:02d}.log').write_text(stream.getvalue(),encoding='utf-8')
  got=read(O/f'caller-review-{suffix}.json');parent=read(H/('caller-review-audio-ad-'+z['tag']+'.json'));assert len(got['calls'])==43==len(namespace['ROOT_CPUS'])
  corrections=[];expected=read(H/('caller-review-audio-ad-'+z['tag']+'.json'))
  for index,(a,b,cpu)in enumerate(zip(parent['calls'],got['calls'],namespace['ROOT_CPUS'])):
   delta=3*len(cpu.root_dec);assert b['instruction_cycles']==a['instruction_cycles']+delta==b['native_cycles'],(z['tag'],index,a,b,cpu.root_dec)
   expected['calls'][index]['instruction_cycles']+=delta
   if delta:corrections.append(dict(call_id=b['id'],instruction_cycle_delta=delta,attained_DEC_opcodes=cpu.root_dec))
  assert got==expected,'No other report field or original oracle may change'
  groups.append(dict(tag=z['tag'],mapper=z['mapper'],actual_semantics=z['actual_semantics'],calls=len(got['calls']),actual_interrupts=sum(r['actual_interrupts']for r in got['calls']),report_sha256=sha(O/f'caller-review-{suffix}.json'),all_original_fields_literal_except_exact_attained_DEC_cycle_delta=True,cycle_corrections=corrections))
  print('LAND_CALLERS',z['tag'],43,groups[-1]['actual_interrupts'],'DEC-adjusted calls',len(corrections),flush=True)
 assert sum(z['calls']for z in groups)==516 and sum(z['actual_interrupts']for z in groups)==462
 specs=[('review_ag.py','source-audio-review-ag.json','8793d4224d7d6fb1ab80d81f70a28c223edde011b957193686adae446864c1f9'),('review_af.py','nonland-cost-reset-af.json','5197986977da3cb0b91fc95938052a0261b5ca622c0a34f3f460d686b8eb24bf'),('profile_aj.py','helper-cost-aj.json','2bb68a6d896227b3a42e42d923dc47d722e8218ee05b4466d1d1262e29c99403'),('profile_al.py','helper-protocol-al.json','0273870a790a73375cd19ef8fd098e91587400c41ba082cf566b92697bb429ca'),('check_an.py','constructor-closure-an.json','c767398870ba5edf621495662aa8a193a863de457be17db1eae6e5c4b5f0f72f')]
 for script,name,pinned in specs:
  original=H/script;assert sha(H/name)==pinned;code=original.read_text(encoding='utf-8');old="p=H/"+repr(name);assert code.count(old)==1
  modified=code.replace(old,"p=ROOT_OUTPUT/"+repr(name));(O/(script+'.txt')).write_text(modified,encoding='utf-8');stream=io.StringIO()
  with contextlib.redirect_stdout(stream):exec(compile(modified,str(original),'exec'),{'__name__':'__main__','__file__':str(original),'ROOT_OUTPUT':O})
  (O/(script+'.log')).write_text(stream.getvalue(),encoding='utf-8');assert read(O/name)==read(H/name)
  print('LAND_SOURCE_LIFECYCLE',name,'PASS',flush=True)
 cost=read(O/'nonland-cost-reset-af.json');assert len(cost['pairs'])==144 and sum(z['cases']for z in cost['direct_reset'])==512
 assert all(not z['individually_traced_dead_stack_differences']for z in cost['pairs'])
 assert sum(len(z['constructor_cases'])for z in read(O/'constructor-closure-an.json')['maps'])==24
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 for b in c['builds']:
  for z in b['artifacts'].values():assert sha(R/z['path'])==z['sha256']
 result=dict(status='PASS_ROOT_RUSH_LAND_SOURCE_516_EXACT_NATIVE_CALLS_462_IRQS_AND_BOUND_DEC_CYCLE_CORRECTION',script_sha256=sha(__file__),packet_sha256=sha(packet),AQ_sha256=sha(aq),source_files=471,artifacts=32,receipts=1201,source_overlay_files=len(j['changes_from_frozen_RushC']),native_groups=groups,additional_reviews={name:sha(O/name)for _,name,_ in specs},source_owned_mask=10,source_frames='six encoded frames matching raw audible source updates2..7; release nextupdate',source_retrigger_frames=[1,5],nonLand_pairs=144,nonLand_added_cycles=42,reset_allP_cases=512,constructor_dirty_cases=24,all144_nonLand_pairs_all10240RAM_literal=True,per_mapper_segment_deltas=sizes['per_mapper_segment_deltas'],contextual_bank_protocol=j['contextual_bank_protocol'],cost=j['cost'],limits=j['limits']+['Root rehashes every frozen source/artifact/receipt. Callers retain every original assertion and every report field except instruction_cycles gains exactly3 per individually recorded reached$CE/absoluteDEC; corrected instruction cycles equal native cycles for516calls. HW failing cycle-equality evidence is retained.','All516nativecalls preserve exactAXYP/SP/PC/all10240RAM/stack/SMC/orderedwrites/banks with462attainedIRQs; original source/lifecycle/cost/constructor output JSONs reproduce literally.','Land is private component evidence, not yet composed with HU/Arm/HUD/Ryu/visibleWater or installed. No finalroute/movie proof.'],main_changed=False,installed=False,goal_complete=False)
 result['outputs']={str(p.relative_to(O)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in O.rglob('*')if p.is_file()}
 out=O/'review.json';out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');assert workspace_bytes(O)+10000000<30000000
 print('ROOT_LAND',sha(out),flush=True)
if __name__=='__main__':main()
