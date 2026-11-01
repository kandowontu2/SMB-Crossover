"""Selected-worker differential and actual native clipped shoe/OAM tests."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O,P,PIN,V2,REF,labels
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN
 raw=bytearray(b['raw']);raw[1048592+502*1024:1048592+503*1024]=(O/'art-code502.bin').read_bytes();b=dict(b,raw=bytes(raw))
 new=labels(O/'visible.lbl');old=labels(V2/'host.lbl');image=(O/'code501.bin').read_bytes()+(O/'art-code502.bin').read_bytes();oldcode=(V2/'host.bin').read_bytes();seed=M.fresh(b);measure={}
 def fresh(**fields):
  m=M.fork(seed);m.ram[2][0x1600:0x1e00]=image
  M.put(m,SelectedCharacter=0,MarioVariant=7,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0,PlayerStatus=2,PlayerSize=0,Player_State=0,Player_CollisionBits=3,Player_Y_Position=96,Player_Y_HighPos=1,Player_X_Position=96,Player_PageLoc=0,PlayerFacingDir=1,Player_MovingDir=1,AreaType=1,ObjectOffset=0,NmiDisable=255,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,Player_Y_Speed=253,GuestOamRotationActive=0,ObjectVerticalFlip=0)
  M.put(m,**fields);return m
 def call(m,name,oldworker=False,**regs):
  d=old if oldworker else new;target=d[name]
  m[address(b,'SafecallA_SMC')+1]=regs.get('a',85);m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
  c=NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a=2;c.x=regs.get('x',0);c.y=regs.get('y',3);c.p=regs.get('p',0x31);c.sp=224;c.stPushWord(0x5aff);low=c.sp
  for _ in range(300000):
   if c.pc==0x5b00:break
   assert m[c.pc]!=0,(name,hex(c.pc),m.rawtags);c.step();low=min(low,c.sp)
  else:raise AssertionError((name,'Bounded',hex(c.pc)))
  assert c.sp==224 and m.rawtags[1]==M.get(m,'CurrentBank')and m.rawtags[2]==M.get(m,'CurrentBankC')
  k=name+('_old'if oldworker else'');q=measure.setdefault(k,dict(calls=0,max_cycles=0,minimum_SP=224));q['calls']+=1;q['max_cycles']=max(q['max_cycles'],c.processorCycles);q['minimum_SP']=min(q['minimum_SP'],low)
  return c.a,c.x,c.y,c.p
 def state(m,c):
  omit=set(range(0x100,0x200))|set(range(0x2000,0x5c00))|{address(b,n)for n in ['CurrentBank','CurrentBankC','safecall_a']}
  rams=[bytes(r)for r in m.ram];rams[2]=bytes(m.ram[2][:0x1600])+bytes(m.ram[2][0x1e00:])
  return c,bytes(v for i,v in enumerate(m[:0x8000])if i not in omit),rams
 differential=0
 cases=[]
 for status,p in itertools.product(range(3),[0x30,0x31,0x71,0xf9]):
  for name in ['MtHostContact','MtHostInjury','MtHostMovement','MtHostBeginPowerup','MtHostGrowthUpdate','MtTerrainHeadProbe','MtTerrainSideProbe']:
   cases.append((name,dict(PlayerStatus=status,PlayerSize=int(status==0),Enemy_ID=0,Enemy_Flag=1,Enemy_State=0,Enemy_Y_Position=96,Enemy_Y_HighPos=1,Enemy_X_Position=112,Enemy_PageLoc=0,Enemy_MovingDir=1,PowerUpType=1),p))
 for state_,swim,lr,ab in itertools.product(range(4),range(2),range(4),[0,64,128,192]):cases.append(('MtHostMovement',dict(Player_State=state_,SwimmingFlag=swim,Left_Right_Buttons=lr,A_B_Buttons=ab,Up_Down_Buttons=4 if lr==3 else 0,PreviousA_B_Buttons=0,Player_X_Speed=24,Player_XSpeedAbsolute=24),0x31))
 for timer,size in itertools.product([0,195,196,197,247,248,249,255],[0,1]):cases.append(('MtHostGrowthUpdate',dict(TimerControl=timer,GameEngineSubroutine=9,PlayerSize=size,PlayerChangeSizeFlag=0),0x31))
 for name,fields,p in cases:
  left=fresh(**fields);right=M.fork(left);right.ram[2][0x1600:0x1e00]=bytes(2048);right.ram[2][0x1600:0x1600+len(oldcode)]=oldcode
  x=call(left,name,p=p);y=call(right,name,oldworker=True,p=p);assert state(left,x)==state(right,y),(name,fields,p,x,y);differential+=1
 # Actual native body then selected post-render. Distinct world OAM survives;
 # two reserved cells precede the original four cells, including clipping.
 records=json.loads((V2/'shoe-mask-candidate.json').read_text())['records'];oam=address(b,'Sprite_Data');render=0;clipped=0
 for rec,px,py,off,frame in itertools.product(records,[-3,0,120,251],[[-5,1],[96,1],[250,1],[3,2]],[0,5,63],[0,2]):
  lo,hi=py;worldx=px&0xffff;m=fresh(Player_X_Position=worldx&255,Player_PageLoc=worldx>>8,Player_Y_Position=lo&255,Player_Y_HighPos=hi,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,PlayerFacingDir=1 if rec['face']=='R'else 2,ObjectMetasprite=rec['pose'],ObjectVerticalFlip=off,FrameCounter=frame,CurrentOAMOffset=0,Player_SprAttrib=32)
  for i in range(64):m[oam+4*i:oam+4*i+4]=[248,55,0,i]
  M.invoke(m,'DrawMetasprite',x=rec['pose'],y=0)
  body=bytes(m[oam:oam+16]);world=bytes(m[oam+24:oam+256]);call(m,'MtArtPostV5')
  assert bytes(m[oam+8:oam+24])==body and bytes(m[oam+24:oam+256])==world
  # Native renderer reverses record order. Its signed offsets and 16bit
  # screen clipping must agree with the independently packed source parts.
  oy=(hi<<8)+(lo&255)+(off if off<32 else off-64)
  for j,part in enumerate(reversed(rec['parts'])):
   at=oam+j*4;xx=px+part['x'];yy=oy+part['y'];visible=0<=xx<256 and 256<=yy<512
   if visible:
    assert list(m[at:at+4])==[yy&255,0x41+2*part['mask'],part['hardware_flip']|32|((frame>>1)&3),xx],(rec['face'],rec['pose'],px,py,off,list(m[at:at+4]),part)
   else:assert m[at]==248;clipped+=1
  if len(rec['parts'])==1:assert m[oam+4]==248
  assert M.get(m,'CurrentOAMOffset')==24 and m.ram[2][0x88a]==0
  render+=1
 pickup=0
 for status,frame in itertools.product(range(3),range(8)):
  m=fresh(PlayerStatus=status,FrameCounter=frame,ObjectMetasprite=0,Enemy_Flag=0,PowerUpType=0,ObjectOffset=5,CurrentOAMOffset=0);m[address(b,'Enemy_Flag')+5]=1;m[address(b,'PowerUpType')+5]=1
  before=bytes([((i*37)+11)&255 for i in range(256)]);m[oam:oam+256]=list(before)
  for field,value in dict(Enemy_ID=address(b,'PowerUpObject'),Enemy_State=128,Enemy_X_Position=112,Enemy_PageLoc=0,Enemy_Y_Position=96,Enemy_Y_HighPos=1,Enemy_SprAttrib=0,Enemy_OffscreenBits=0).items():m[address(b,field)+5]=value
  M.invoke(m,'DrawPowerUp',x=5,y=0);assert m[address(b,'EnemyMetasprite')+5]==64
  M.invoke(m,'DrawMetasprite',x=64,y=6);assert list(m[oam+1:oam+16:4])==[122,122,120,120]
  expected=bytearray(m[oam:oam+256])
  for at in range(1,256,4):
   if expected[at]in[120,122]:expected[at]=103 if expected[at]==120 else 105
  call(m,'MtArtPostV5');assert bytes(m[oam:oam+256])==expected;pickup+=1
 q=dict(passed=True,current_ROM_sha256=PIN,selected_worker_native_differential_cases=differential,native_shoe_render_cases=render,independent_signed_clip_checks=clipped,native_pickup_preservation_cases=pickup,worker_bytes=721,visible_bytes=len((O/'visible.bin').read_bytes()),metadata_bytes=224,foreign_shared_entry_not_modified=True,owning_Main=False,native_Mesen=False,installed=False,measure=measure,limits=['Preloaded conditional RAM2 component. ROM gates,24B reservation, menu admission and two-row loader must be source-wired before native qualification.','Inverted native death art deliberately has no shoe overlay; ordinary Y offsets and both source faces are tested.','Pickup tile uniqueness is limited here to native fixed atlas; dynamic source closure remains an owning-source requirement.'],bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in [REF,Path(__file__),O/'worker.bin',O/'visible.bin',O/'metadata.bin']})
 (O/'visible-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k.endswith('cases')or k in['passed','worker_bytes','visible_bytes','independent_signed_clip_checks']}))
if __name__=='__main__':main()
