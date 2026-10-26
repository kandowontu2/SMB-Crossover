"""Freeze finite native Chip cost attribution; no new emulator run or optimization."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load,address,Memory
from verify_native_relocation import NesMPU
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);f=a.root/'fixture-v4';native=read(f/'profile-verification/proof.json');assert native['passed'];rows=[json.loads(x)for x in(f/'profile-spans.jsonl').read_text().splitlines()];events=[json.loads(x)for x in(f/'profile-boundaries.jsonl').read_text().splitlines()];snapshots=[json.loads(x)for x in(f/'profile-snapshots.jsonl').read_text().splitlines()];q=read(a.root/'main-cpu-v4/Main-1.json');chosen=[]
 for i in range(4):
  r=read(a.root/f'main-cpu-v4/Main-{i}.json');observed=[x for x in rows if x['name']=='PlayerCtrlRoutine'and r['actual_native_entry']['cpuCycle']<=x['startCycle']<r['actual_native_Main']['endCycle']];modeled=[x for x in r['native_regions']if x['name']=='PlayerCtrlRoutine'];assert len(observed)==len(modeled)==1 and observed[0]['cpuCycles']==modeled[0]['cycles'];chosen.append(dict(native_PlayerCtrl=observed[0],CPU_PlayerCtrl=modeled[0],whole_Main_native=r['actual_native_CPU_cycles'],whole_Main_CPU=r['counterfactual_CPU_cycles'],whole_Main_exact=r['cycles_exact']))
 first=next(e for e in events if e['kind']=='NMI-entry'and e['nmiDisable']==255);publication=next(e for e in events if e['kind']=='NmiDisable-write'and e['value']==0 and e['cpuCycle']>first['cpuCycle']);isrs=[e for e in events if e['kind']in['NMI-pre-RTI','IRQ-pre-RTI']and first['cpuCycle']<=e['cpuCycle']<publication['cpuCycle']];interrupt=sum(e['complete_hardware_entry_and_RTI_cycles']for e in isrs);conditional=publication['cpuCycle']-interrupt-first['last_foreground_instruction_boundary'];assert conditional==1931
 prep=read(f/'preparation.json');b=load(Path(prep['ROM']));cfg=read(f/'configuration.json');snap=next(x for x in snapshots if x['kind']=='post-hardware-NMI-entry');m=Memory(b)
 for slot,k in enumerate(snap['banks']):m.page(slot,k)
 raw=(f/'profile-snapshots.ram').read_bytes();payload=raw[snap['ramOffset']:snap['ramOffset']+snap['ramBytes']];pos=0
 for lo,hi in cfg['ram_ranges']:
  for at in range(lo,hi+1):list.__setitem__(m,at,payload[pos]);pos+=1
 c=NesMPU(memory=m,pc=snap['detail']['interruptedPC']);c.a,c.x,c.y=snap['a'],snap['x'],snap['y'];c.p=snap['detail']['stackedP'];c.sp=snap['detail']['foregroundSP'];m.writes=[];nops=0
 for steps in range(20000):
  nops+=m[c.pc]==234;before=len(m.writes);c.step()
  if any(at==address(b,'NmiDisable')and v==0 for at,v in m.writes[before:]):break
 else:raise AssertionError('tail timeout')
 assert c.processorCycles==1925
 summary=read(f/'profile-summary.json');regions={n:[r['cycles']for r in q['native_regions']if r['name']==n]for n in['BlockBufferColli_Head','BlockBufferColli_Side','BoundingBoxCore']};far=q['farcall_records'];scope=[r for r in far if r['nativeRegion']=='PlayerCtrlRoutine'];assert len(scope)==32 and sum(r['scaffoldCycles']for r in scope)==1696
 result=dict(passed=True,scope='Native read-only attribution only. Original1300 880DMA deficit remains. No optimization/native acceptance. Four PlayerCtrl CPU replays exactly match native; wholeMain CPU replays remain HELD24/48cycles low outside that region.',ROM_sha256=prep['ROM_sha256'],native_summary=summary,original_native_proof=native,first_boundary=dict(NMI=first,publication=publication,intervening_ISR=isrs,conditional_uninterrupted_publication_lateness=conditional,source_only_tail_cycles=c.processorCycles,tail_vs_conditional_difference=c.processorCycles-conditional,tail_NOP_cycles=2*nops,qualification='Conditional subtraction is not an emulated NMI/PPU replay. Tail snapshot retains posthardware stack bytes; foregroundPC/P/SP reconstructed. First normal Main entry/prior Audio2 were not captured because active admission began after Engine became8.'),exact_PlayerCtrl_replays=chosen,normal_PlayerCtrl_farcall_count=len(scope),normal_PlayerCtrl_farcall_scaffold_cycles=sum(r['scaffoldCycles']for r in scope),normal_CPU_leaf_cycles=regions,movement=dict(outer_X5_farcall=1369,authentic_CdMovement=506,difference=863,qualification='Nested inclusive costs must not be summed. Difference includes retained camera/dispatch work; not a promised saving.'),side=dict(outer_Tn_fast_gate_each=305,authentic_native_query_each=118,calls=4,difference_each=187,qualification='Includes retained native query and caller scaffolding; actual shortcut saving requires complete assembled caller/SMC differential.'),proposal='One bounded Chip-only hot-control routing candidate: reach original CdMovement within retained X5 camera wrapper; directly admit native Chip side query. Preserve actual head/feet/pipe semantics, callerAXYP, complete RAM/SMC/banks and every foreign identity. Authentic music/source clock untouched. Source-only implementation/qualification required; this packet contains no game patch.',remaining_model_gap='WholeMain differences24/48cycles, localized CdWeapons18/CdGraphics3/DrawAll24/outer3, remain unexplained. Mapping all captured PRG windows in v3/v4 did not resolve them; no causal claim that the old mapping-shadow defect explained the difference.',native_worker_released=True)
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');bindings=[]
 for d in[f,a.root/'main-cpu-v1',a.root/'main-cpu-v2',a.root/'main-cpu-v3',a.root/'main-cpu-v4']:
  for z in sorted(d.rglob('*')):
   if z.is_file():bindings.append(dict(path=str(z.resolve()),sha256=sha(z),bytes=z.stat().st_size))
 for n in ['chip_idle_profile_main_cpu_v1.py','chip_idle_profile_main_cpu_v2.py','chip_idle_profile_main_cpu_v3.py','chip_idle_profile_main_cpu_v4.py','chip_idle_profile_attribution_v1.py']:
  z=Path(__file__).parent/n;bindings.append(dict(path=str(z.resolve()),sha256=sha(z),bytes=z.stat().st_size))
 (a.output/'bindings.json').write_text(json.dumps(dict(proof=dict(path=str((a.output/'proof.json').resolve()),sha256=sha(a.output/'proof.json')),bindings=bindings),indent=2)+'\n');print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),bindings_sha256=sha(a.output/'bindings.json'),bindings=len(bindings),worker_released=True)))
if __name__=='__main__':main()
