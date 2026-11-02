"""Actual weapon dispatch: source rectangle edges, scores, exclusions and idle cost."""
import json,itertools
import prepare_metal_storm_shots_1101_v35 as P
import check_hogan_current_bounded_v1 as M
import metal_storm_cpu_1101_v2 as D
from link_pit_rygar_sophia_audit_cpu import scoped_load

def main():
 b=scoped_load(P.O/'candidate.nes');seed=M.fresh(b)
 for bank,at,f in [(3,0,'native-actor.bin'),(2,0xd00,'native-render.bin'),(2,0x1ba0,'native-extra.bin')]:
  d=(P.O/f).read_bytes();seed.ram[bank][at:at+len(d)]=d
 for bank in [2,3]:seed.ram[bank][0x1fe0:0x1ff0]=(P.O/'native-cookie.bin').read_bytes()
 M.put(seed,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,ObjectOffset=4)
 for i in range(6):seed[M.address(b,'Enemy_Flag')+i]=0
 donor=D.machine();donor.memory.regs[6:8]=[0,1];donor.memory.map()
 cases=0;cycles=[];minimum=255
 for kind,slot,camera in itertools.product([128,129],[2,3],[0,240,512]):
  index=slot+(4 if kind==129 else 0)
  left,right,top,bottom=[donor.memory[a+index] for a in [0xe8ce,0xe92e,0xe98e,0xe9ee]]
  assert [left,right,top,bottom]==([2,5,6,9] if kind==128 else [0,15 if slot==2 else 7,0,15])
  for dx,dy in itertools.product([left-16,left-15,0,right,right+1], [top-24,top-23,0,bottom,bottom+1]):
   m=M.fork(seed);shotx=camera+100;ex=shotx+dx;ey=100+dy
   M.put(m,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
         Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=ex&255,
         Enemy_PageLoc=ex>>8,Enemy_Y_Position=ey,Enemy_Y_HighPos=1)
   for at,v in {0x510:128,0x528:kind,0x480:shotx&255,0x498:shotx>>8,0x4b0:100,0x4c8:0}.items():m.ram[2][at+slot]=v
   before=bytes(m.ram[2][:2048]);z=M.invoke(m,'HuWeaponTail');cycles.append(z['CPU']);minimum=min(minimum,z['minimum_SP'])
   hit=left<=dx+15 and dx<=right and top<=dy+23 and dy<=bottom
   assert bool(M.get(m,'Enemy_State')&32)==hit,(kind,slot,camera,dx,dy,hit)
   assert (m.ram[2][0x510+slot]==0)==hit
   assert M.get(m,'ObjectOffset')==4
   assert [z[k] for k in ['A','X','Y']]==[85,7,91]
   if hit:
    assert M.get(m,'FloateyNum_Control')==1 and M.get(m,'Square1SoundQueue')==8
   else:assert bytes(m.ram[2][:2048])==before
   cases+=1
 exclusions=0
 for enemy in [0x15,0x24,0x25,0x26,0x2e,0x2f]:
  m=M.fork(seed);M.put(m,Enemy_Flag=1,Enemy_ID=enemy,Enemy_State=0,Enemy_X_Position=100,Enemy_PageLoc=0,Enemy_Y_Position=100,Enemy_Y_HighPos=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
  for a,v in {0x512:128,0x52a:128,0x482:100,0x49a:0,0x4b2:100,0x4ca:0}.items():m.ram[2][a]=v
  M.invoke(m,'HuWeaponTail');assert M.get(m,'Enemy_State')==0 and m.ram[2][0x512]==128;exclusions+=1
 idle=M.invoke(M.fork(seed),'HuWeaponTail')['CPU']
 q=dict(passed=True,ROM_sha256=P.P.sha(P.O/'candidate.nes'),actual_dispatch='HuWeaponTail',rectangle_cases=cases,source_table_verified=True,excluded_object_cases=exclusions,cycle_range=[min(cycles),max(cycles)],idle_callback_cycles=idle,minimum_SP=minimum,scope='Authenticated cache fixtures through real weapon bridge/native defeat; actual Goomba state/score/SFX and shot retirement, page crossings and edge negatives. Native Mesen gameplay, Main/IRQ budget and full1-1 remain pending.')
 (P.O/'shot-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
