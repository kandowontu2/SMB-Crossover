"""Original37-identity ordinary wholeAudio controls plus expansion bus order."""
from pathlib import Path
import argparse,itertools,json,traceback
from smb3_host_current3b_cpu_v1 import sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from cv3_dmc_cpu_v1 import diff,regs,apu
from final_item_matrix import ROSTER

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);layout=json.loads((a.packet/'layout.json').read_text());base=Path(layout['parent_directory']);bundles=[scoped_load(q/'candidate.nes')for q in [base,a.packet]];rows=[]
 try:
  for name,slot,char,variant,value,family in ROSTER:
   costs=[]
   for mode,request in itertools.product([0,1],[(1,0),(2,0),(0,4),(1,8)]):
    qs=[Arena(b,char)for b in bundles]
    for q in qs:
     q.put(CrossoverBehaviorVersion=mode,AreaMusicQueue=request[0],EventMusicQueue=request[1])
     if variant:q.set(variant,value)
    for tick in range(32):
     for q in qs:
      q.put(GamePauseStatus=int(tick in(16,17)),AvAudioRequest=21 if tick==8 else 22 if tick==12 else 0)
      if tick==20:q.m[0x4015]=15
     cs=[q.invoke('AudioUpdate')[0]for q in qs]
     assert apu(qs[0])==apu(qs[1]),(name,mode,request,tick,'originalAPU')
     hardware=lambda q:[(at,v)for at,v in q.m.writes if 0x4000<=at<=0x5015 or at in [0x5115,0x5116,0x5117]]
     assert hardware(qs[0])==hardware(qs[1]),(name,mode,request,tick,'expansion+mapper order')
     diff(qs);assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks,(name,mode,request,tick,'wholeAXYP/SP/banks')
     d=cs[1].processorCycles-cs[0].processorCycles;assert d<=0,(name,mode,request,tick,'slower ordinary path',d);costs.append(d)
   rows.append(dict(identity=name,character=char,variant=variant,value=value,cases=len(costs),cycle_delta=[min(costs),max(costs)]));put(a.output/f'row-{len(rows):02}.json',rows[-1]);print(json.dumps(rows[-1]),flush=True)
  assert len(rows)==37
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(base/'candidate.nes'),ROM_sha256=sha(a.packet/'candidate.nes'),identities=37,CPU_mode_cells=74,full_AudioUpdate_calls=sum(r['cases']for r in rows),rows=rows,original_9472_input_assertions_retained=True,additional_ordered_expansion_APU_and_mapper_store_guard=True,all_ordinary_costs_no_slower=True,checker_sha256=sha(__file__),limits='Fresh exact parent/candidate assembled CPU. Both directly seeded modes, four original area/event requests, typed effects, pause and ended-DMC control. Complete nonstack flat application state/AXYP/SP and ordered original+expansion APU/map writes. No native selection, sample fetch/DMA/waveform/PPU/timing or every-item/campaign proof.'))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),identities_done=len(rows)));raise
if __name__=='__main__':main()
