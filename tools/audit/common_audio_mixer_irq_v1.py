"""Actual resident IRQ at changed common-audio instruction boundaries."""
from pathlib import Path
import argparse,json,traceback
from smb3_host_current3b_cpu_v1 import sha,put
from smb3_host_current3b_owners_v2 import PeripheralMemory
from smb3_host_current3b_boundaries_v2 import execute
from common_audio_mixer_controls_v1 import memory
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True);b=scoped_load(a.packet/'candidate.nes');layout=json.loads((a.packet/'layout.json').read_text());rows=[]
 try:
  cases=[dict(entry='GuestExpansionFlush',mask=k,char=17,owner=0,cold=0)for k in [0,1,2,3,11,15]]+[dict(entry='GuestAudioBegin',mask=3,char=char,owner=owner,cold=cold)for char,owner,cold in [(17,0,0),(17,1,1),(17,3,1),(9,1,0),(2,3,1)]]
  if layout['parent_name']=='hot6':cases +=[dict(entry='GuestAudioBegin',mask=3,char=17,owner=4,cold=1)]
  for spec in cases:
   initial=memory(b,1)
   for n,v in [('SelectedCharacter',spec['char']),('GuestAudioCharacter',(spec['char']+1)%20 if spec['cold']else spec['char']),('BassDmcActive',spec['owner']),('Cv3DmcPriority',128 if spec['owner']>=3 else 1),('Square1SoundQueue',85),('Square2SoundQueue',71),('NoiseSoundQueue',43),('GuestMixMask',spec['mask']),('GuestMixChanged',3),('GameEngineSubroutine',8),('GuestSweepControl',0xe7),('GuestSweepDivider',0),('GuestSweepReload',1),('GuestSweepPeriod',0xff)]:initial[address(b,n)]=v
   initial[address(b,'GuestSweepPeriod')+1]=7
   for i in range(8):initial[address(b,'GuestFxDirty')+i]=1
   for n in ['BassAudioInit','BassAudioPreviousMask','BassAudioLastDeath','BassAudioLastGround','BassSourceId']:initial[address(b,n)]=91
   start_E=125 if spec['owner']==3 else 70 if spec['owner']==4 else 127
   initial.page(3,start_E);initial.hwdmc=bool(spec['owner']);initial.hw[21]=31 if spec['owner']else 15
   snapshot=list(initial);banks=initial.banks[:];hw=initial.hw[:];hwdmc=initial.hwdmc
   def fresh():
    m=PeripheralMemory(b);list.__setitem__(m,slice(None),snapshot);m.banks=banks[:];m.hw=hw[:];m.hwdmc=hwdmc;return m
   base=fresh();c,trace=execute(b,base,spec['entry'],record=True)
   raw=lambda m:bytes(m[:256]+m[512:2048]+m[0x6000:0x8000]);bus=lambda m:[(at,v)for i,(at,v)in enumerate(m.writes)if i not in m.irq_write_indices and not 256<=at<512]
   expected=([c.a,c.x,c.y,c.p&207,c.sp],raw(base),base.banks[:],base.hw[:],bus(base));keys=sorted(set(tuple(x)for x in trace));deltas=[]
   for key in keys:
    m=fresh();after,_=execute(b,m,spec['entry'],inject=key);actual=([after.a,after.x,after.y,after.p&207,after.sp],raw(m),m.banks[:],m.hw[:],bus(m));assert actual==expected,('IRQ continuation',spec,key)
    irq=[(at,v)for at,v in m.irq_writes if not 256<=at<512];assert irq==[(0x2006,0),(0x5128,0),(0x2005,32),(0x2005,0),(0x2006,128)],('IRQ actual bus',spec,key,irq)
    deltas.append(after.processorCycles-c.processorCycles)
   assert set(deltas)=={120},set(deltas)
   rows.append(dict(**spec,start_E=start_E,actual_instruction_boundaries=len(keys),IRQ_added_cycles=sorted(set(deltas)),uninterrupted_cycles=c.processorCycles));print(json.dumps(rows[-1]),flush=True)
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(a.packet/'candidate.nes'),cases=rows,actual_IRQ_cases=sum(r['actual_instruction_boundaries']for r in rows),full_RAM_OAM_images_sweep_dirty_AXYP_SP_banks_shadow_and_ordered_main_bus_exact=True,actual_five_IRQ_PPU_writes_literal=True,only_tagged_IRQ_stores_removed_from_ordered_main_bus=True,checker_sha256=sha(__file__),limits='Actual IRQ/RTI and hardware-vector execution at every reached instruction boundary in finite legal isolated common-audio calls. Source aliases125/70 where owned are genuine mapped clone bytes. Not physical PPU/APU/DMA timing, native cadence or arbitrary foreground workload proof.'))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),contexts_done=len(rows)));raise
if __name__=='__main__':main()
