"""Retain native Ryan displacement and exercise actual residual wall consumers."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from river_city_pipe_contact_controls_v2 import fixture,position,tile,pipe,step,state
from sunny_integrated_controls_v1 import seed,run,registers,app,cleanwrites
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def world(q):return q.get('Player_X_Position')+256*q.get('Player_PageLoc')
def hurt(b,x=2706,y=152,face=1):
 q=fixture(b)
 for xx in [2688,2704,2720]:tile(q,xx,144,0x51)
 position(q,x,y,-2);q.put(RcHurtMove=10,Player_X_Speed=24 if face==1 else 232,RcLastVx=24 if face==1 else 232,PlayerFacingDir=face,SavedJoypadBits=129 if face==1 else 130)
 q.set('MmVX',254 if face==1 else 1,2);q.set('MmVX',128,1);return q
def main():
 old=R/'build/river-city-shared-v5.nes';half=R/'build/river-city-shared-v7.nes';rom=R/'build/river-city-shared-v8.nes'
 assert sha(rom)=='4cbd019100ba4dfc51fd9f71c5d3cabd844828eb7d5d2a4aa39413e3579ab39a'
 bs=[scoped_load(p)for p in[old,half,rom]];rows=[]
 for b in bs:
  q=hurt(b);step(q);rows.append(dict(check='retained_hurt_under_real_brick_row',ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),after=world(q),state=state(q)))
 assert [z['after']for z in rows]==[2719,2719,2705],rows
 # Both source recoil directions, true block contacts and low-speed return:
 # real movement->BG, forty updates each. No mocked collision or warp allowed.
 for face,x,y in itertools.product((1,2),(2692,2702,2706,2710,2724),(150,152,156)):
  q=hurt(bs[-1],x,y,face);xs=[world(q)]
  for tick in range(40):
   step(q);xs.append(world(q));assert abs(xs[-1]-xs[-2])<=5,(face,x,y,tick,xs[-2:],state(q))
  rows.append(dict(check='recoil_ceiling_trajectory',face=face,start=[x,y],updates=40,maximum_horizontal_step=max(abs(a-b)for a,b in zip(xs,xs[1:]))))
 # Source-gated cold change adds a compare but must preserve every foreign
 # wall transaction, full final register flags/application RAM/ordered writes.
 base=scoped_load(R/'build/roster-union-celeste-mac-v1.nes');foreign=[]
 profiles=[(0,None,0),(8,None,0),(1,'ProtoVariant',1),(2,None,0),(3,'BillVariant',1),(4,'Z2Variant',0),(4,'Z2Variant',1),
   (5,'Cv3Variant',0),(5,'Cv3Variant',2),(6,None,0),(7,None,0),(9,'RlVariant',1),(10,None,0),(11,None,0),(12,'DarkwingVariant',1),
   (13,'KbVariant',1),(14,'CdVariant',1),(15,'MacVariant',0),(15,'MacVariant',1),(15,'MacVariant',2),(16,None,0),(17,'M3Variant',1),
   (18,'VvVariant',3),(19,'TnVariant',3),(20,'IcVariant',1),(23,None,0)]
 for (char,key,var),side,x,vx in itertools.product(profiles,(1,2),(0,146,255),(24,232)):
  pair=[]
  for b in(base,bs[-1]):
   q=seed(b,char)
   if key:q.set(key,var)
   q.put(R0=side,R3=0x61,Player_X_Position=x,Player_PageLoc=2,Player_X_Speed=vx,Player_MovingDir=1 if vx<128 else 2)
   c,w,_=run(q,'StopPlayerMove',a=0x61,x=0,y=0,p=0x71);pair.append((registers(c),app(q),q.m.banks,cleanwrites(q,w),c.processorCycles))
  assert pair[0][:4]==pair[1][:4],(char,key,var,side,x,vx,pair[0][0],pair[1][0])
  foreign.append(dict(character=char,variant=var,side=side,X=x,VX=vx,CPU_delta=pair[1][4]-pair[0][4]))
 target=R/'build/river-city-hurt-corner-controls-v8.json';assert not target.exists()
 target.write_text(json.dumps(dict(passed=True,native_run=False,ROM_sha256=sha(rom),rows=rows,foreign=foreign,
  limits=['Typed actual native consumers; native Hard route is a separate exact-hash receipt.','NMI fixture controls in composed proof use foreground-protocol lag path; not all audio-state or PPU timing proof.'],
  bindings=[dict(path=str(p),sha256=sha(p))for p in[Path(__file__),old,half,rom,rom.with_suffix('.dbg'),R/'src/river_city_wall_prepass_v2.inc']]),indent=2)+'\n')
 print(json.dumps(dict(passed=True,trajectories=30,updates=1200,foreign_wall_transactions=len(foreign))))
if __name__=='__main__':main()
