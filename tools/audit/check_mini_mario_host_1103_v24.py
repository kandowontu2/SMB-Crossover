"""Private native-host CPU contracts and unchanged original source Step."""
from pathlib import Path
import json,random,sys
from py65.devices.mpu6502 import MPU
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_world_1103_v11 as W
import prepare_mini_mario_host_1103_v22 as H
import check_mini_mario_step_1103_v18 as T
R,O=W.R,H.O

def main():
 q=json.loads((O/'mini-host-v22.json').read_text());data=(O/'mini-host-v22.bin').read_bytes();L=q['labels'];S=H.symbols();old=(W.O/'world-step-v16.bin').read_bytes();oldL=json.loads((W.O/'world-step-v16.json').read_text())['exports']
 def fresh(f=0):
  m=T.memory(data,L,f);m.memory[0xd300:0xd400]=(R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin').read_bytes();m.memory[0xd000:0xd160]=(R/'build/mini-mario-art-1103-v12/engine-animation-index.bin').read_bytes();m.memory[0xd160:0xd239]=(R/'build/mini-mario-art-1103-v12/engine-animation-frames.bin').read_bytes();return m
 def put(m,**values):
  for n,v in values.items():m.memory[S[n]]=v
 def call(m,n):return T.call(m,L[n])
 rng=random.Random(41);cases=0
 for state in[0,1,3,4,6,7,9,10,12,13]:
  for f in range(5):
   for _ in range(16):
    tier=rng.randrange(2);v=T.initial(state,rng.randrange(40*16,112*16),rng.randrange(112*16,207*16),rng.choice([0,1,2,4,0x41,0x42,0x80,0x81,0x82]),tier);v[0:2]=(rng.randrange(-5602,5603)&65535).to_bytes(2,'little');v[32:34]=(rng.randrange(-12288,8193)&65535).to_bytes(2,'little');v[36]=rng.randrange(2);v[65]=rng.randrange(3);v[66]=rng.randrange(3);v[67]=int(state in(6,7));v[73]=rng.choice([0,v[72]])
    if v[67]:v[86]=1
    pair=[T.memory(old,oldL,f),fresh(f)]
    for m in pair:m.memory[0xc200:0xc281]=v;m.memory[0xc22a:0xc22c]=[0,2]
    T.call(pair[0],oldL['MiniStep']);call(pair[1],'MiniStep')
    assert pair[0].memory[0xc200:0xc281]==pair[1].memory[0xc200:0xc281],cases
    cases+=1
 # True entrance: constructor sees nativeY0, first real8 sees nativeY176/high1.
 m=fresh();put(m,GameEngineSubroutine=0,Player_Y_Position=0,Player_Y_HighPos=0,Player_X_Position=0,Player_PageLoc=0,PlayerStatus=0,AreaType=1)
 call(m,'MiniHostFresh');assert m.memory[0xc300]==1
 call(m,'MiniHostMain');assert m.memory[0xc300]==1 and m.memory[0xc252:0xc254]==[0,0]
 put(m,GameEngineSubroutine=8,Player_X_Position=40,Player_Y_Position=176,Player_Y_HighPos=1,FrameCounter=0)
 call(m,'MiniHostMain');assert m.memory[0xc300]==2
 assert m.memory[S['Player_Y_Position']]==192 and m.memory[S['Player_Y_HighPos']]==1,(m.memory[S['Player_Y_Position']],m.memory[S['Player_Y_HighPos']])
 assert m.memory[0xc252]|m.memory[0xc253]<<8==3215
 before=bytes(m.memory[0xc200:0xc324]);call(m,'MiniHostMain');assert bytes(m.memory[0xc200:0xc324])==before,'sameepoch'
 cycles=[];ys=[];xs=[]
 for epoch in range(1,181):
  put(m,FrameCounter=epoch,SavedJoypadBits=0);cycles.append(call(m,'MiniHostMain'));xs.append(m.memory[S['Player_X_Position']]);ys.append(m.memory[S['Player_Y_Position']])
 assert min(xs)==max(xs)==40 and min(ys)==max(ys)==192
 idle=dict(updates=180,worldX=40,canvasY=192,cycles=[min(cycles),max(cycles)])
 # Timer/pause skip the complete original step and animation epoch.
 for field,value in [('TimerControl',1),('GamePauseStatus',1),('GameEngineSubroutine',7)]:
  n=fresh();n.memory=list(m.memory);put(n,FrameCounter=181);put(n,**{field:value});before=bytes(n.memory[0xc200:0xc324]);call(n,'MiniHostMain');assert bytes(n.memory[0xc200:0xc324])==before,field
 # Native position correction retains 1/16 fractional state.
 n=fresh();n.memory=list(m.memory);n.memory[0xc250]=(n.memory[0xc250]&240)|7;n.memory[0xc252]=(n.memory[0xc252]&240)|11;put(n,Player_X_Position=70,Player_Y_Position=180)
 call(n,'MiniHostImportX')if 'MiniHostImportX'in L else None
 # Export helper labels below are deliberately private in source; main shift
 # proof uses zero-time pre-Step capture via wrapping MPU entry.
 class Hook(MPU):
  def step(self):
   if self.pc==L['MiniStep']:
    self.anchor=(self.memory[0xc250]|self.memory[0xc251]<<8,self.memory[0xc252]|self.memory[0xc253]<<8)
   return super().step()
 h=Hook();h.memory=list(n.memory);put(h,FrameCounter=181,SavedJoypadBits=0);call(h,'MiniHostMain');assert h.anchor==(70*16+7,(180+8)*16+11),h.anchor
 # Exact body and getter projection packets.
 body=0
 for tier in[0,1,2]:
  for x in[0,1,15,127,249]:
   for y in[32,128,192,224]:
    n=fresh();put(n,Player_Rel_XPos=x,Player_Y_Position=y);n.memory[0xc254:0xc258]=[1,6,1 if tier==0 else 249,7];call(n,'MiniHostBox');assert n.memory[S['BoundingBox_UL_Corner']:S['BoundingBox_UL_Corner']+4]==[(x+1)&255,(y+8+(1 if tier==0 else -7))&255,(x+6)&255,(y+15)&255];assert n.x==n.y==0 and n.p&1;body+=1
 heads=0
 for page in[0,1,8,13]:
  for x in[0,8,120,248]:
   for y in[32,40,128,184,224]:
    n=fresh();put(n,GameEngineSubroutine=8,R0=0x55,R1=0xaa);addr=0x300+(page&1)*0xd0+((y&240)-32)+(x>>4);n.memory[0xc25c]=1;n.memory[0xc25d:0xc261]=[x,page,y,0];n.memory[0xc261]=0xc1;n.memory[0xc262:0xc264]=[addr&255,addr>>8];n.y=14;call(n,'MiniHostHead');row=(y&240)-32;assert n.memory[3:11]==[0x55,0xaa,row,0xc1,y&15,x,(addr-row)&255,(addr-row)>>8];assert n.a==0xc1 and n.x==0 and n.y==14 and not n.p&2 and n.memory[0xc25c]==0;heads+=1
 palettes=0
 for offset in[0,1,21,76,77,83]:
  for area in range(4):
   for ctrl in range(8):
    for tier in range(3):
     n=fresh();put(n,VRAM_Buffer1_Offset=offset,AreaType=area,BackgroundColorCtrl=ctrl,PlayerStatus=tier);n.a=81;n.x=82;n.y=83;n.p=0x68;call(n,'MiniHostColors');assert(n.a,n.x,n.y)==(81,82,83)and n.p&0xcf==0x69&0xcf
     if offset<77:assert n.memory[S['VRAM_Buffer1']+offset:S['VRAM_Buffer1']+offset+8]==[0x3f,0x10,4,[0x22,0x22,15,15,15,0x22,15,15][ctrl or area],0x27,0x37 if tier==2 else 0x16,0x16 if tier==2 else 0x18,0]
     else:assert n.memory[S['VRAM_Buffer1_Offset']]==offset
     palettes+=1
 out=dict(passed=True,component_bytes=len(data),component_SHA256=W.sha(data),frozen_source_full_state_differentials=cases,first_actual_entrance=dict(cold_nativeY=0,post_Entrance_nativeY=176,first_sourceY16_4=3215,exported_canvasY=192,source_first_Main_uses_actual_native_X40=True),idle=idle,duplicate_epoch_and_pause_timer_guards=True,fractional_import_correction=True,source_bounds_native_cases=body,head_projection_cases=heads,palette_native_packets=palettes,unimplemented_rows=q['unimplemented_reject_rows'],scope='Private CPU flat/wall source transport and typed native leaves only. No actual shared owner/cold/native IRQ or full1-1 acceptance. Explicit source wall adaptation requires native earned verification.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),H.INC,O/'mini-host-v22.json',W.O/'world-source-v21.json']})
 (O/'mini-host-CPU-v24.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
