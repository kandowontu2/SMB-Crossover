"""Exact final CV1 restore and ordinary full AudioUpdate differential controls."""
from pathlib import Path
import argparse,hashlib,itertools,json,random
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old,new=load(a.prepared/'baseline.nes'),load(a.prepared/'candidate.nes');rows=[];rng=random.Random(0xc31f)
 # Unique24-byte CV1 restore loop in C bank28; execute actual old bytes.
 raw=old['raw'][16+28*8192:16+29*8192]
 starts=[i for i in range(len(raw)-20)if raw[i:i+3]==b'\xa0\x17\xbe'and raw[i+15:i+20]==b'\x88\xc0\xff\xd0\xee'and int.from_bytes(raw[i+8:i+10],'little')==address(old,'RgAudioZp')]
 assert len(starts)==1,starts;start=0xc000+starts[0]
 zps=[*range(0xba,0xc0),*range(0xe0,0xf0),0x22,0x60]
 for case in range(256):
  qs=[Arena(b,5)for b in(old,new)];seed=[rng.randrange(256)for _ in range(256)];save=[rng.randrange(256)for _ in range(24)]
  states=[];cycles=[]
  for k,q in enumerate(qs):
   q.m.page(2,28);q.m[0:256]=seed;q.array('RgAudioCpuZp',save);q.array('RgAudioZp',[0x55]*32)
   c=NesMPU(memory=q.m,pc=start if not k else address(new,'Cv3RestoreAudioZp'));c.a,c.x,c.y,c.p,c.sp=0x55,17,63,case,0xfd
   if k:c.stPushWord(0x5aff)
   for _ in range(1000):
    if c.pc==(start+20 if not k else 0x5b00):break
    c.step()
   else:raise AssertionError('Restore timeout')
   states.append((c.a,c.x,c.y,c.p&0xcf,c.sp,bytes(q.m[:0x100]),bytes(q.m[address(q.b,'RgAudioZp'):address(q.b,'RgAudioZp')+32])))
   cycles.append(c.processorCycles)
  assert states[0]==states[1],(case,states)
  rows.append(dict(flags=case,old_cycles=cycles[0],new_cycles=cycles[1]))
 (a.output/'restore.json').write_text(json.dumps(rows,indent=2)+'\n')
 # Actual top-level audio update, bank restoration and all existing typed
 # cues. This exercises the actual imported music driver and shared mixer.
 regressions=[];deltas=[]
 for char,variant,effect in itertools.product((3,4,5),(0,3),range(26)):
  if char!=5 and variant:continue
  qs=[Arena(b,char)for b in(old,new)]
  for q in qs:q.put(Cv3Variant=variant,AreaMusicQueue=1,AvAudioRequest=0)
  for tick in range(40):
   for q in qs:
    q.put(GamePauseStatus=int(tick in(17,18)),AvAudioRequest=effect if tick==8 else 0)
   results=[q.invoke('AudioUpdate')[0]for q in qs]
   writes=[[(at,v)for at,v in q.m.writes if 0x4000<=at<=0x4017 or 0x5000<=at<=0x5015]for q in qs]
   assert writes[0]==writes[1],(char,variant,effect,tick,writes)
   exclude=set(range(0x100,0x200));before,after=qs[0].m,qs[1].m
   different=[i for i in range(0x8000)if i not in exclude and before[i]!=after[i]]
   assert not different,(char,variant,effect,tick,[hex(i)for i in different[:20]])
   assert qs[0].m.banks==qs[1].m.banks
   assert (results[0].a,results[0].x,results[0].y,results[0].p&0xcf,results[0].sp)==(results[1].a,results[1].x,results[1].y,results[1].p&0xcf,results[1].sp)
   deltas.append(results[1].processorCycles-results[0].processorCycles)
  regressions.append(dict(character=char,variant=variant,effect=effect,updates=40,passed=True))
 (a.output/'ordinary-audio.json').write_text(json.dumps(regressions,indent=2)+'\n')
 proof=dict(passed=True,accepted=False,ROM_sha256=sha(a.prepared/'candidate.nes'),baseline_ROM_sha256=sha(a.prepared/'baseline.nes'),tool_sha256=sha(__file__),restore_cases=len(rows),restore_exact='A/X/Y/NV-DIZC/SP, all256 CPUZP bytes and full32privatebytes; only helper call stack excluded',ordinary_full_AudioUpdate_cases=len(regressions)*40,ordinary_cues=26,ordinary_cycle_delta=[min(deltas),max(deltas)],ordinary_exact='All application RAM below8000 excluding stack; ordered hardware APU writes, mapper and final registers',scope='Actual assembled CPU paths; native interrupt/APU/visible checks are separate.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
