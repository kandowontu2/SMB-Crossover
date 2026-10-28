"""Finite real-input airborne Arrow source controls and one compact ready."""
from pathlib import Path
from argparse import Namespace
import hashlib,json
from current_darkwing_arrow_route_source_v1 import scene,world,block
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from current_roster_compact_11_v1 import prepare,linked,lua,ROOT,sha
ROM=ROOT/'build/darkwing_hang_floor.nes'
EXPECTED='3e5ee17fb7cc0413df4b758c94499ace1f33d8b66dd519fcdb92959e79b2ac1d'
POLICY=ROOT/'tools/playthroughs/current_roster_darkwing_air_arrow_v7.lua'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

class Controller:
 """One-source-update mirror; no Lua/native polling equivalence claim."""
 def __init__(self,top):self.phase='acquire';self.top=top;self.slot=None;self.transitions=[]
 def change(self,q,p):
  if self.phase!=p:self.phase=p;self.transitions.append(dict(phase=p,x=world(q),y=q.get('Player_Y_Position'),gas=q.get('DwGas'),hang=q.get('DwHang')))
 def stable(self,q):
  if self.slot is None:return False
  i=self.slot;a=q.get('RgShotImpact',i)-1;sx=q.get('RgShotX',i)+256*q.get('RgShotPage',i)
  return(q.get('RgShotType',i)==6 and q.get('RgShotDir',i)==1 and q.get('SsMode',i)==0 and 0<=a<6
   and q.get('Enemy_Flag',a)==1 and q.get('Enemy_ID',a)==38 and q.get('Enemy_State',a)==32|i
   and 736<=sx+12<768 and q.get('Enemy_X_Position',a)+256*q.get('Enemy_PageLoc',a)==sx-12
   and q.get('Enemy_Y_Position',a)==q.get('RgShotY',i)and q.get('RgShotY',i)<=self.top+20)
 def buttons(self,q):
  p=self.phase;x=world(q);prev=q.get('DwPrevious');ground=q.get('Player_State')==0;y=q.get('Player_Y_Position')
  if p=='acquire':
   if q.get('DwAdaptor')==2 and q.get('DwGas')>=3:self.change(q,'select-release')
   else:
    for i in range(6):
     if q.get('Enemy_Flag',i)==1 and q.get('Enemy_ID',i)==46 and q.get('Enemy_State',i)>=128 and q.get('InvPickupOwner',i)==12 and q.get('InvPickup',i)==38:
      ix=q.get('Enemy_X_Position',i)+256*q.get('Enemy_PageLoc',i);return 1 if x<ix-4 else 2 if x>ix+8 else 0
    return 1
  if self.phase=='select-release':
   if q.get('DwMode')==1:self.change(q,'takeoff-release')
   elif not prev&32:self.change(q,'select-press')
  if self.phase=='select-press':
   if q.get('DwMode')==1:self.change(q,'takeoff-release')
   else:return 33
  if self.phase=='takeoff-release':
   if ground and not prev&128:self.change(q,'rise');return 129
   return 1
  if self.phase=='rise':
   if not ground and y<=self.top and not prev&64:self.change(q,'fire');return 193
   return 129
  if self.phase=='fire':
   for i in range(10):
    if(q.get('RgShotType',i)==8 and q.get('RgShotImpact',i)==2 or q.get('RgShotType',i)==5)and q.get('RgShotDir',i)==1 and q.get('RgShotAge',i)<13:
     self.slot=i;self.change(q,'hang');return 1
   return 129 if prev&64 else 193
  if self.phase=='hang':
   if self.stable(q)and q.get('DwHang')==128|self.slot:
    if not prev&128:self.change(q,'hang-jump');return 129
   elif ground and self.stable(q)and not prev&128:return 129
   return 1
  if self.phase=='hang-jump':
   if ground and y+32<=self.top and x+8>=736:self.change(q,'top')
   return 129
  if self.phase=='top':return 1
  return 1

def campaign(b,height,mode):
 q=scene(b);q.set('CrossoverBehaviorVersion',mode);top=208-height
 end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
 assert b['raw'][location(b,'E_GroundArea2')-1]==255
 for row in range(6,11):
  for x in [736,752]:q.set('Block_Buffer_1',0,x//256%2*208+row*16+x%256//16)
 for y in range(top,208,16):
  for x in [736,752]:q.set('Block_Buffer_1',(16 if x==736 else 17)if y==top else(20 if x==736 else 21),x//256%2*208+(y-32)//16*16+x%256//16)
 c=Controller(top);rows=[];events=[];tick=0;original=NesMPU.step
 names=['DwRecovery::Spawn','DwGiveItem','DwShotInit','DwAttachArrow','DwValidateHang']
 owners={(address(b,n),(location(b,n)-16)//8192):n for n in names}
 def step(cpu):
  k=q.m.banks[(cpu.pc-32768)//8192]if cpu.pc>=32768 else-1;n=owners.get((cpu.pc,k))
  if n in names[:-1]:events.append(dict(update=tick,owner=n,pc=cpu.pc,bank=k,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),gas=q.get('DwGas'),mode=q.get('DwMode')))
  original(cpu)
 NesMPU.step=step
 try:
  for tick in range(450):
   bits=c.buttons(q);q.put(SavedJoypadBits=bits);q.invoke('GameLoop')
   row=dict(update=tick,phase=c.phase,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vy=q.get('Player_Y_Speed'),buttons=bits,previous=q.get('DwPrevious'),gas=q.get('DwGas'),adaptor=q.get('DwAdaptor'),mode=q.get('DwMode'),hang=q.get('DwHang'),slot=c.slot,
    arrows=[[i,q.get('RgShotType',i),q.get('RgShotAge',i),q.get('RgShotX',i)+256*q.get('RgShotPage',i),q.get('RgShotY',i),q.get('SsMode',i),q.get('RgShotImpact',i)]for i in range(10)if q.get('RgShotType',i)])
   rows.append(row);assert q.get('GameEngineSubroutine')==8 and q.get('MmDeathFlag')==0,('Typed source death',row)
   ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
   if world(q)>800 and q.get('Player_State')==0:break
 finally:NesMPU.step=original
 result=dict(height=height,mode=mode,updates=len(rows),transitions=c.transitions,events=events,rows=rows)
 assert world(q)>800,('Air Arrow did not clear',height,mode,c.transitions,rows[-8:])
 assert sum(e['owner']=='DwRecovery::Spawn'for e in events)==1 and sum(e['owner']=='DwGiveItem'for e in events)==1
 shots=[e for e in events if e['owner']=='DwShotInit'];assert len(shots)==1 and shots[0]['state']!=0 and shots[0]['y']<=top
 assert q.get('DwGas')==7 and q.get('DwAdaptor')==2 and any(r['hang']>=128 for r in rows)
 assert any(r['state']==0 and r['y']+32<=top and r['x']>=736 for r in rows)
 return result

def main():
 assert sha(ROM)==EXPECTED
 b=scoped_load(ROM);proofpath=ROOT/'build/darkwing_air_arrow_source_v1.json';assert not proofpath.exists()
 cases=[]
 try:
  for height in[64,80]:
   for mode in[0,1]:
    z=campaign(b,height,mode);cases.append(z);print(json.dumps(dict(source_PASS=True,height=height,mode=mode,updates=z['updates'])),flush=True)
 except Exception as e:
  put(ROOT/'build/darkwing_air_arrow_trial_negative.json',dict(passed=False,native_run=False,ROM_sha256=EXPECTED,error=repr(e),completed_cases=cases));raise
 proof=dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,source_cases=cases,
  scope='Complete genuine GameLoop, typed pipe64/80/floor208/player721/176/camera632, genuine cold inventory/recovery acquisition10gas, Select, airborne B debit3, charge12/attach/hang/freshA/collision/landing. No player/resource/input-consumer/outcome writes after setup. VRAM source consumer drained separately; not PPU/NMI timing, native exact map reconstruction, input-poll cadence, Lua execution or route proof.',
  bindings={str(p):sha(p)for p in[Path(__file__),ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),ROOT/'tools/audit/current_darkwing_arrow_route_source_v1.py']})
 put(proofpath,proof);print(json.dumps(dict(passed=True,path=str(proofpath),sha256=sha(proofpath))),flush=True)

if __name__=='__main__':main()
