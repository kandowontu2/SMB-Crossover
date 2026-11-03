"""Minimal real native Mini pickup/update adapters; memory-only source proof."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_power_contract_1103_v51 as P
import prepare_mini_mario_chr_override_1103_v39 as A
import prepare_mini_owner_payload_1103_v19 as PACK
import prepare_mini_mario_native_smoke_1103_v25 as B
import check_hogan_current_bounded_v1 as N
from check_tmnt_render_oa import address,location
W,R,O=P.W,P.R,P.O
def bundle(raw):
 text=B.GLOBALS.with_suffix('.dbg').read_text();b=dict(raw=bytes(raw),syms={},segs={})
 for line in text.splitlines():
  if not line.startswith(('sym\t','seg\t')):continue
  z=dict(x.split('=',1)for x in line[4:].split(',')if '='in x)
  if line.startswith('seg\t'):b['segs'][z['id']]=z
  elif 'val'in z:b['syms'][z['name'].strip('"')]=z
 b['segs']['mini_current65']=dict(start=str(0xa000),ooffs=str(16+65*8192))
 for name,pc in [('MiniScene',0xb013),('MiniCheck',0xaee2)]:b['syms'][name]=dict(val=str(pc),seg='mini_current65')
 return b
def main():
 raw=P.ROM.read_bytes();assert W.sha(raw)==P.PIN;b=bundle(raw);old=(P.HOST/'mini-host-v48.bin').read_bytes()
 src=(P.HOST/'mini-host-v48.s').read_text();flag=address(b,'Enemy_Flag');target=address(b,'FarcallJmpTarget_SMC');far=address(b,'FarCallCommon')
 defs=f'.export MiniHostPickup,MiniHostPowerup\nEnemy_Flag=${flag:04x}\nMiniNativeTarget=${target:04x}\nMiniFarCall=${far:04x}\n'
 assert src.count(' jmp MiniHostNo           ;24 native fallback')==1 and src.count(' jmp MiniHostNo           ;33 source capability absent')==1
 src=src.replace(' jmp MiniHostNo           ;24 native fallback',' jmp MiniHostPickup       ;24 genuine native whole pickup, erased recursive inventory returnsCLC')
 src=src.replace(' jmp MiniHostNo           ;33 source capability absent',' jmp MiniHostPowerup      ;33 actual native power freeze/update')
 def native(name,tail=False):
  pc=address(b,name);bank=((location(b,name)-16)//8192)|128
  return f' lda #${pc&255:02x}\n sta MiniNativeTarget+1\n lda #${pc>>8:02x}\n sta MiniNativeTarget+2\n lda #${bank:02x}\n '+('jmp'if tail else'jsr')+' MiniFarCall\n'
 leaf='MiniHostPickup:\n lda Enemy_Flag,x\n beq @erased\n'+native('MarioSourcePowerupCollision')+' sec\n rts\n@erased:\n clc\n rts\nMiniHostPowerup:\n'+native('GuestPowerupUpdate',True)
 assert src.count('MiniHostEnd:\n')==1;src=defs+src.replace('MiniHostEnd:\n',leaf+'MiniHostEnd:\n')
 data,L=A.assemble(O/'mini-host-v56',src,0xa000,0x2000);assert len(data)<=5120
 # Complete component/cookie rebinding in memory only, never write a ROM.
 at=lambda page:1048592+page*1024
 oldim=PACK.component(old,raw[at(967):at(968)],raw[at(968):at(969)],W.sha(old));im=PACK.component(data,raw[at(967):at(968)],raw[at(968):at(969)],W.sha(data))
 cookie_at=16+65*8192+0xb003-0xa000;assert raw[at(962):at(967)]==oldim['code']and raw[cookie_at:cookie_at+16]==oldim['cookie']
 after=bytearray(raw);after[at(962):at(967)]=im['code'];after[cookie_at:cookie_at+16]=im['cookie'];base=bundle(after)
 m=N.fresh(base);N.put(m,SelectedCharacter=41,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
 cold=N.invoke(m,'MiniScene');assert bytes(m.ram[3][:len(data)])==data and m.ram[2][0x300]==1
 N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,OperMode_Task=3,GameEngineSubroutine=8,PlayerStatus=0,PlayerSize=1,ObjectOffset=5,Player_X_Position=418,Player_PageLoc=1,Player_Y_Position=176,Player_Y_HighPos=1)
 # Native low-byte X only; source fixture keeps the actual mature native item.
 N.put(m,Player_X_Position=418&255)
 for name,v in [('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',128),('PowerUpType',0)]:m[address(base,name)+5]=v
 trace=[];counts={};cls=N.NesMPU;low=[255]
 points={(((location(base,n)-16)//8192)|128,address(base,n)):n for n in ['MarioSourcePowerupCollision','GuestBeginPowerup','GuestPowerupUpdate','EraseEnemyObject','HandlePowerUpCollision']}
 points.update({(3,L[n]):n for n in ['MiniHostPickup','MiniHostPowerup']})
 class Trace(cls):
  def step(self):
   low[0]=min(low[0],self.sp)
   if self.pc>=0x8000:
    name=points.get((self.memory.rawtags[(self.pc-0x8000)//8192],self.pc))
    if name:
     counts[name]=counts.get(name,0)+1
     if len(trace)<24:trace.append(dict(name=name,SP=self.sp,X=self.x,A=self.a,flag5=self.memory[address(base,'Enemy_Flag')+5]))
   return cls.step(self)
 N.NesMPU=Trace
 try:
  pickup=N.invoke(m,'HandlePowerUpCollision',a=205,x=5,y=46,p=0x21)
  assert N.get(m,'GuestPowerupActive')==1 and N.get(m,'GuestPowerupTarget')==1 and N.get(m,'GameEngineSubroutine')==9
  assert m[address(base,'Enemy_Flag')+5]==0 and counts.get('EraseEnemyObject')==1 and counts.get('MarioSourcePowerupCollision')==1
  assert counts.get('MiniHostPickup')==1,('One whole native pickup only; real inventory path need not reenter private row24',counts,trace)
  erased=N.invoke(m,'HuPickup',a=41,x=5,y=46,p=0x21)
  assert not erased['P']&1 and counts.get('EraseEnemyObject')==1,'Already-erased callback cannot recurse or consume twice'
  ages=[]
  for _ in range(60):
   N.invoke(m,'NrNativePowerupDispatch',a=0,x=0,y=0,p=0x21);ages.append(N.get(m,'GuestPowerupAge'))
  assert N.get(m,'PlayerStatus')==1 and N.get(m,'GuestPowerupActive')==0 and N.get(m,'GameEngineSubroutine')==8
 finally:N.NesMPU=cls
 out=dict(passed=True,source_CPU_only=True,ROM_written=False,native_admitted=False,bytes=len(data),SHA256=W.sha(data),five_pages_spare=5120-len(data),labels=L,vectors=[int.from_bytes(data[i*3+1:i*3+3],'little')for i in range(38)],parent_ROM_SHA256=P.PIN,expected_memory_only_ROM_SHA256=W.sha(after),cookie=im['cookie'].hex(),patches=[dict(file_offset=at(962),old_hex=oldim['code'].hex(),new_hex=im['code'].hex(),role='Only Mini five owned codepages'),dict(file_offset=cookie_at,old_hex=oldim['cookie'].hex(),new_hex=im['cookie'].hex(),role='Existing complete Mini payload cookie')],actual_cold=cold,actual_native_pickup=pickup,native_calls=counts,trace=trace,minimum_SP_conservative_native_calls=low[0],native_power_age_sequence=ages,final_status=N.get(m,'PlayerStatus'),scope='Minimal actual native pickup/update bridge. Original native item erase,score,Sfx,GuestBegin andGuestUpdate execute; erasedflag prevents recursive wholecollect on nativeInventory callback. Generic native60update/+1 target remains declared host adaptation, not original Mini30/35/type target/sourceChangeSize/projectile fidelity. Actual IRQ/FF and native qualification pending.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),P.HOST/'mini-host-v48.bin',P.HOST/'mini-host-v48.s',P.HOST/'mini-host-v48.json',Path(PACK.__file__),R/'src/guest_powerups.s',R/'src/mario_source.s',O/'earned-mushroom55/capture/result.json']})
 (O/'mini-host-v56.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','bytes','SHA256','five_pages_spare','minimum_SP_conservative_native_calls','native_calls','expected_memory_only_ROM_SHA256','cookie']}))
if __name__=='__main__':main()
