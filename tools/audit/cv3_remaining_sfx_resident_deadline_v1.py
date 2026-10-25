"""Actual HELD draw boundary: hardware NMI stack, publication and net resumed work."""
from pathlib import Path
import argparse,csv,hashlib,json
from check_tmnt_render_oa import load,address,location

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return[{k:int(v)if v.lstrip('-').isdigit()else v for k,v in r.items()}for r in csv.DictReader(p.open())]

def context(b,r):
 pc=r['interruptedPC'];bank=r['interruptedBank'];offset=16+8192*bank+(pc&8191);hits=[]
 if pc>=0x8000:
  for name,s in b['syms'].items():
   if 'seg'not in s or'size'not in s or'val'not in s:continue
   size=int(s['size'],0);start=int(s['val'],0)
   if size<8 or not start<=pc<start+size:continue
   try:physical=(location(b,name)-16)//8192
   except Exception:continue
   if physical==bank:hits.append(dict(name=name,start=start,size=size,offset=pc-start))
 return dict(physical_bank=bank,PC=pc,ROM_bytes=b['raw'][offset:offset+8].hex()if pc>=0x8000 else None,containing_symbols=sorted(hits,key=lambda h:h['size'])[:4],hardware_stack_P=r['stackP'])

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);base=a.prepared/'native-timing-v2';b=load(a.prepared/'candidate.nes');cases=[]
 for cp in sorted(base.glob('candidate-*')):
  bp=base/cp.name.replace('candidate-','baseline-',1);assert json.loads((cp/'native-proof.json').read_text())['passed']and json.loads((bp/'native-proof.json').read_text())['passed'];cr,br=[read(p/'deadline-timing.csv')for p in[cp,bp]];oldnmi={r['wall']:r for r in br if r['kind']=='NMI-entry'};extra=[]
  for n in cr:
   if n['kind']!='NMI-entry'or not n['nmiDisable']&128:continue
   bn=oldnmi[n['wall']]
   if bn['nmiDisable']&128:continue
   pub=next(r for r in cr if r['kind']=='publication-write'and r['cpuCycle']>n['cpuCycle']);nr=next(r for r in cr if r['kind']=='NmiReturn'and r['cpuCycle']>n['cpuCycle']);assert nr['cpuCycle']<pub['cpuCycle']
   previous_game=max((r for r in cr if r['kind']=='GameLoop'and r['cpuCycle']<n['cpuCycle']),key=lambda r:r['cpuCycle']);previous_draw=max((r for r in cr if r['kind']in['NoLagSoDraw','SkipDrawingCauseLagged']and r['cpuCycle']<n['cpuCycle']),key=lambda r:r['cpuCycle']);baseline_pub=max((r for r in br if r['kind']=='publication-write'and r['cpuCycle']<bn['cpuCycle']),key=lambda r:r['cpuCycle'])
   irqs=[]
   for irq in cr:
    if irq['kind']!='IrqScrollSplit'or not nr['cpuCycle']+6<=irq['cpuCycle']<pub['cpuCycle']:continue
    end=next(r for r in cr if r['kind']=='IrqReturn'and r['cpuCycle']>=irq['cpuCycle']);assert end['cpuCycle']<pub['cpuCycle'];irqs.append(dict(entry=irq,return_RTI=end,body_plus_RTI_cycles=end['cpuCycle']+6-irq['cpuCycle'],hardware_IRQ_entry_cycles=7))
   # Callback is at RTI entry. RTI takes6 native CPU cycles here; all selected
   # Sypha arenas have no DMC fetch/start, so no DMA stalls can extend that RTI.
   fetch=read(cp/'dmc-fetch.csv');assert not fetch,'Selected Sypha deadline case has no actual DMC bus fetches'
   main_resume=nr['cpuCycle']+6;elapsed=pub['cpuCycle']-main_resume;irq_pauses=sum(x['body_plus_RTI_cycles']+7 for x in irqs);net=elapsed-irq_pauses;assert net>=0
   next_skip=next((r for r in cr if r['kind']=='SkipDrawingCauseLagged'and r['cpuCycle']>pub['cpuCycle']),None)
   extra.append(dict(NMI_entry=n,interrupted_context=context(b,n),actual_prior_GameLoop=previous_game,actual_prior_draw_decision=previous_draw,actual_NMI_return_RTI=nr,actual_publication_write=pub,publication_after_entry_cycles=pub['cpuCycle']-n['cpuCycle'],actual_NMI_body_plus_RTI_cycles=main_resume-n['cpuCycle'],main_thread_after_RTI_to_publication_cycles=elapsed,subsequent_IRQs=irqs,main_thread_instruction_cycles_remaining_at_interrupt=net,baseline_entry=bn,baseline_last_publication=baseline_pub,baseline_publication_margin_to_entry_cycles=bn['cpuCycle']-baseline_pub['cpuCycle'],next_actual_catchup_skip=next_skip,counterfactual_limit='Exact observed main-thread work remaining after RTI, with any subsequent IRQ service removed. This is not an exact globally sufficient saving: CPU interrupt sampling/instruction phase and prior-frame scheduling can change under optimization. Hardware entry adds7 cycles before the entry callback; frame deadline versus sampled entry is explicit.'))
  assert extra,cp.name;cases.append(dict(name=cp.name,candidate_proof_sha256=sha(cp/'native-proof.json'),baseline_proof_sha256=sha(bp/'native-proof.json'),candidate_timing_sha256=sha(cp/'deadline-timing.csv'),baseline_timing_sha256=sha(bp/'deadline-timing.csv'),extra_lag_NMI_boundaries=extra))
 result=dict(passed=True,accepted=False,status='HELD_EXACT_NATIVE_DEADLINES',ROM_sha256=sha(a.prepared/'candidate.nes'),cases=cases,case_count=len(cases),all_timing_instrumentation_observation_only=True,tool_sha256=sha(__file__),scope='Actual paired same-work cold numeric-mode pilots; exact NMI entry/stackedPC/publication/draw observations. No acceptance, waveform or complete campaign claim.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=[dict(name=r['name'],extra=[dict(wall=n['NMI_entry']['wall'],PC=n['interrupted_context']['PC'],bank=n['interrupted_context']['physical_bank'],physical_late=n['publication_after_entry_cycles'],main_remaining=n['main_thread_instruction_cycles_remaining_at_interrupt'],baseline_margin=n['baseline_publication_margin_to_entry_cycles'])for n in r['extra_lag_NMI_boundaries']])for r in cases]),indent=2))
if __name__=='__main__':main()
