"""Postrun genuine opening: original executable source and full hardware receipts."""
from pathlib import Path
import argparse,json,traceback
from smb3_host_current3b_cpu_v1 import RAW,TraceBus,D,R,sha,put
from verify_native_relocation import NesMPU

def seq(v):return []if v=={} else v
def verify(packet):
 cfg=json.loads((packet/'configuration.json').read_text());folder=packet/'native';rows=[json.loads(s)for s in(folder/'smb3-music-native.jsonl').read_text().splitlines()];source=None;calls=[];original_APU=0;source_enables=0
 for row in rows:
  if row['kind']!='original-source-call':continue
  call=row['call'];kind=call['kind'];inp=call['registers']
  if kind=='init':source=TraceBus(RAW)
  assert source is not None,'Source play must follow actual original init';source.events=[];source.mapper=[];source.nonstack_writes=[]
  c=NesMPU(memory=source);c.pc=0x9000 if kind=='init'else 0xa000;c.a,c.x,c.y,c.p=inp[:4];c.sp=(inp[4]+2)&255;c.stPushWord(0x7eff)
  for _ in range(10000):
   if c.pc==0x7f00:break
   source.pc=c.pc;source.pc_physical=source.physical(c.pc);c.step()
  else:raise AssertionError('Original source timeout')
  actual=call['return_registers'];assert[actual[0],actual[1],actual[2],actual[3]&207,actual[4]]==[c.a,c.x,c.y,c.p&207,c.sp],('Native/source AXYP_SP',call['serial'])
  assert seq(call['logical'])==[list(z)for z in source.events],('Native ordered logical sourceAPU',call['serial'],call['logical'],source.events)
  inverse=dict(zip(cfg['music']['source_state_addresses'],cfg['music']['original_source_addresses']));ram=[[inverse[a],v]for a,v in seq(call['RAM'])]
  assert ram==[list(z)for z in source.nonstack_writes],('Native ordered sourceRAM',call['serial'])
  assert seq(call['maps'])==[list(z)for z in source.mapper],('Native virtual map order',call['serial'])
  assert call['finish_state']==[source[a]for a in cfg['music']['original_source_addresses']],('Native original source state',call['serial'])
  original_APU+=len(source.events);source_enables+=sum(a==0x4015 and v&16!=0 for a,v in source.events);calls.append(dict(serial=call['serial'],kind=kind,source_APU=len(source.events),native_source_cycles=call['complete']['cpu']-call['entry']['cpu'],original_source_cycles=c.processorCycles))
 result=json.loads((folder/'result.json').read_text());music=json.loads((folder/'smb3-music-native-result.json').read_text());render=json.loads((folder/'render-observation-result.json').read_text());motion=json.loads((folder/'completed-loop-motion.json').read_text());body=json.loads((folder/'chr-commit.json').read_text())
 assert result['component_complete'] and result['world_1_1_seen'] and result['frames']==1200 and result['deaths']==0,result
 assert music['passed'] and music['actual_mode']==0 and music['actual_character']==17 and music['actual_variant']==0,music
 assert render['passed'] and render['fullPPUframes']==1200 and render['nmiChecks']>0 and render['irqChecks']>0,render
 assert motion['passed'] and body['passed'],(motion,body)
 assert len(calls)==music['source_calls'] and len(calls)>300 and not music['source_call_pending']
 if source_enables:assert music['DMC_starts']>0 and music['DMC_fetches']>0 and music['DMC_complete_fetches']>0,('Actual expected DMC fetch coverage',music)
 dma=[json.loads(z)for z in(folder/'ability-dma-epochs.jsonl').read_text().splitlines()];transfers=[q for q in dma if q['kind']=='completed-DMA-before-render-enable'];enables=[q for q in dma if q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']]
 assert transfers and all(not q['differences']and len(q['writes'])==256 and q['source']==q['hardware']for q in transfers)
 assert all(q['safe']for q in enables),'Actual scoped render deadline'
 assert(folder/'actual-ppu.argb').stat().st_size==1200*256*240*4
 return dict(passed=True,native_run=True,ROM_sha256=cfg['music']['ROM_sha256'],actual_source_calls=len(calls),original_ordered_logical_APU_stores=original_APU,original_source_DMC_enable_stores=source_enables,source_calls=calls,music=music,render=render,motion=motion,body=body,complete256_DMA_epochs=len(transfers),scoped_enable_epochs=len(enables),full_PPU_frames=1200,main_cadence='Observed exact updates/draws/publications in route-observation.jsonl/index. No actual same-input3b parent native control exists; no strict differential cadence pass is asserted.',limits='Actual cold natural-input opening only. Logical original source fidelity plus physical sample request/fetch and existing hardware guards; no waveform/original physical pulse-store ordering/othertrack/pause/title/allroster claim.',checker_sha256=sha(__file__))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 try:q=verify(a.packet);put(a.output/'proof.json',q);print(json.dumps({k:q[k]for k in ['passed','actual_source_calls','original_ordered_logical_APU_stores','complete256_DMA_epochs','scoped_enable_epochs']}))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
