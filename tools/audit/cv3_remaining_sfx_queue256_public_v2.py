"""Genuine checked compatibility entry: every byte input and full/world guards."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_remaining_sfx_queue256_support_v1 import init
from cv3_dmc_complete_cpu_v1 import regs
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);old=load(a.rom.parent/'baseline.nes');cases=[]
 negative=init(old,2);negative.invoke('Cv3FxSpawn',a=1,x=3,y=0x71,flags=0x69);assert negative.get('Cv3ShotType',3)==0x71 and negative.get('Cv3FxQueueHead')==negative.get('Cv3FxQueueTail')
 retained=dict(parent_ROM_sha256=sha(a.rom.parent/'baseline.nes'),input_type=1,inputY=0x71,actual_wrong_shot_type=negative.get('Cv3ShotType',3),cue_lost=True)
 for typ,world,occupancy,counter,flags in itertools.product(range(256),[0,21,26,32,33,255],[0,63,64],[0,255],[0x20,0x69]):
  qs=[init(b,2)]
  for q in qs:
   q.put(AvAudioRequest=world,Cv3FxQueueHead=counter,Cv3FxQueueTail=(counter-occupancy)&255,Cv3FxQueueOverflow=0)
  before=[bytearray(q.m[:0x8000])for q in qs];cs=[q.invoke('Cv3FxSpawn',a=typ,x=3,y=0x71,flags=flags)[0]for q in qs]
  assert(cs[0].a,cs[0].x,cs[0].y,cs[0].p&0xcf,cs[0].sp)==(typ,3,0x71,flags&0xcf,253)
  valid=1<=typ<=6 and(world==0 or 26<=world<=32);admitted=valid and occupancy<64
  for index,q in enumerate(qs):
   assert q.get('Cv3ShotType',3)==typ and q.get('AvAudioRequest')==world
   assert q.get('Cv3FxQueueHead')==(counter+int(admitted))&255 and q.get('Cv3FxQueueOverflow')==int(valid and occupancy==64)
   mask=255
   if admitted:assert q.get('Cv3FxQueue',counter&mask)==typ
   allowed=set(range(256,512))|{address(q.b,'Cv3ShotType')+3,address(q.b,'Cv3FxQueueHead'),address(q.b,'Cv3FxQueueOverflow')}
   if admitted:allowed.add(address(q.b,'Cv3FxQueue')+(counter&mask))
   after=bytearray(q.m[:0x8000])
   for at in allowed:before[index][at]=after[at]=0
   assert before[index]==after,('unexpected public write',typ,world,occupancy,counter,flags)
  cases.append(dict(type=typ,world=world,occupancy=occupancy,counter=counter,flags=flags,admitted=admitted,cycles=[c.processorCycles for c in cs]))
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),parent7b0_sha256=sha(a.rom.parent/'baseline.nes'),actual_checked_public_cases=len(cases),retained_parent_compatibility_failure=retained,all256_input_bytes=True,invalid_world_full_guards_and_slot_preservation=True,outer_AXYP_DI_SP_and_every_unrelated_RAM_byte_exact=True,scope='Actual genuine Cv3FxSpawn compatibility entry and checked producer. Corrected originalA contract is independently asserted; prior64 wrapper incorrectly passed savedY and remains a retained negative. The fast sole gameplay call has a separately proved literal-input/capacity contract. No native or public fast-entry arbitrary-input claim.',tool_sha256=sha(__file__))
 (a.output/'cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
