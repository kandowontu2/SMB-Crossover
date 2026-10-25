"""Actual original TMNT damage and accepted-hit consumption leaves. Seeded CPU components."""
from pathlib import Path
from py65.devices.mpu6502 import MPU
import hashlib,json,argparse
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();raw=Path('C:/NES/Teenage Mutant Ninja Turtles (USA).nes').read_bytes();assert hashlib.sha256(raw).hexdigest()=='15e112c3790add361157dfa42854c3159c956f72e6acd8fabc518615f1ce8525'
def byte(bank,at):return raw[16+bank*16384+(at&16383)]
actors=[byte(7,0xe103+k)for k in range(1,5)];assert actors==[0x1a,0x1a,0x27,0x28]
class SourceMem(list):
 def __setitem__(self,k,v):
  # The SFX-busy flag suppresses switched-bank sound execution. Mapper serial
  # writes occur in fixed code and return tobank6 before its next opcode fetch.
  if isinstance(k,int)and k>=0x8000:return
  super().__setitem__(k,v)
def cpu():
 m=SourceMem([0]*65536);m[0x8000:0xc000]=raw[16+6*16384:16+7*16384];m[0xc000:]=raw[16+7*16384:16+8*16384];return MPU(memory=m)
def run(c,pc,stop=0xfff0):
 c.pc=pc;c.x=5;c.y=2;c.sp=0xfd;c.memory[0x1fe]=0xef;c.memory[0x1ff]=0xff
 for i in range(20000):
  if c.pc==stop:return
  c.step()
 raise AssertionError(hex(c.pc))
rows=[];hits=[]
for v in range(4):
 for hp in [32,128]:
  for selected in [0,1]:
   for equipped in range(5):
    for kind,actor in enumerate(actors,1):
     c=cpu();m=c.memory;m[0x67]=v;m[0x77+v]=hp;m[0x5b]=selected;m[0x73+v]=equipped;m[0x442]=actor;m[0x565]=100
     run(c,0x9978,stop=0x99a5);damage=(100-c.a)&255;index=(v if not selected else equipped+3)*2+(hp<64);assert damage==byte(6,0x9bcb+index)
     rows.append(dict(turtle=v,hp=hp,selected=selected,current_equipment=equipped,inflight_kind=kind,source_actor=actor,damage=damage))
   for kind,actor in enumerate(actors,1):
    for target_hp in [1,100]:
     c=cpu();m=c.memory;m[0x67]=v;m[0x77+v]=hp;m[0x5b]=selected;m[0x73+v]=kind;m[0x442]=actor;m[0x445]=0x10;m[0x565]=target_hp;m[0x2f]=128;m[0x5c]=1;m[0xd1]=2
     run(c,0x9978);kill=target_hp==1;consumed=kill and kind in[1,2];assert(m[0x442]==0)==consumed
     hits.append(dict(turtle=v,hp=hp,selected=selected,equipment=kind,source_actor=actor,target_HP=target_hp,defeated=kill,projectile_erased=consumed,remaining_HP=m[0x565]))
q=dict(passed=True,source_ROM_sha256=hashlib.sha256(raw).hexdigest(),source_actor_table=actors,cases=len(rows),rows=rows,accepted_hit_cases=len(hits),accepted_hits=hits,scope='Actual original9978..99A5 damage arithmetic;9978..9A7E accepted-hit damage/despawn state machine with source SFX-busy flag only. Mapper writes are not ROM edits. Incoming accepted collision RAM seeded. No natural campaign/audio claim.',supersedes='original-damage-context.json used non-source actor IDs25/26 in the same selector-independent leaf; arithmetic unchanged, actor provenance corrected here.');args.output.write_text(json.dumps(q,indent=2)+'\n');print('PASS original context',len(rows),'full accepted-hit cases',len(hits))
