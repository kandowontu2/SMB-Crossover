"""Real buffered extra-row load and ordinary pickup call path."""
import json,itertools
import prepare_metal_storm_pickup_1101_v25 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU

def main():
 q=json.loads((P.O/'assembly.json').read_text())
 for p,h in q['bindings'].items():assert P.P.sha(p)==h,p
 b=scoped_load(P.O/'candidate.nes');seed=M.fresh(b)
 M.put(seed,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,NmiDisable=255,CurrentBank=151,CurrentBankC=215,HorizontalScroll=73,VerticalScroll=32,ReloadCHRBank=7,X5WideChrActive=0)
 seed.raw_page(1,151);seed.raw_page(2,215);seed.ppuctrl=160
 for i,v in enumerate([18,20,21,22,23,24,25,26,4,5,6,7]):seed[address(b,'CurrentCHRBank')+i]=v;seed[address(b,'X5ChrMode')+i]=0
 for bank in [2,3]:seed.ram[bank][:]=bytes((i*17+bank*29+7)&255 for i in range(8192))
 seed[0x16a]=85;seed[0x16c]=0x87;seed[0x16d]=0xaf
 c=NesMPU(memory=seed,pc=address(b,'FarCallCommon'));c.a,c.x,c.y,c.p,c.sp=244,7,91,0x71,224;c.stPushWord(0x5ffe)
 for _ in range(1000000):
  if c.pc==0x5fff:break
  if c.pc>=0x8000:assert seed.rawtags[(c.pc-0x8000)//8192]&128,hex(c.pc)
  assert seed[c.pc]!=0,hex(c.pc);c.step()
 else:raise AssertionError('cold bound')
 assert c.sp==224 and c.p&1
 page=b['raw'][16+1048576+499*1024:16+1048576+500*1024]
 assert seed.ram[2][0x1900:0x1d00]==page and seed.ppu_reads==24600,seed.ppu_reads
 assert all(seed.ram[k][0x1fe0:0x1ff0]==bytes.fromhex(q['cookie']) for k in [2,3])
 M.put(seed,DisableScreenFlag=0,Mirror_PPUMASK=24,FrameCounter=1,GamePauseStatus=0,Player_X_Position=40,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,CurrentPlayer=0,NumberofLives=2)
 M.invoke(seed,'HuMovement');assert seed.ram[2][0x800]==167
 def pickup(m,slot,typ=0,mature=128):
  M.put(m,ObjectOffset=slot,PlayerStatus=0,Square2SoundQueue=0)
  for n,v in [('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',mature),('PowerUpType',typ),('Enemy_X_Position',80),('Enemy_PageLoc',0),('Enemy_Y_Position',176),('Enemy_Y_HighPos',1)]:m[address(b,n)+slot]=v
 cases=0
 for slot,armor in itertools.product(range(6),[0,128]):
  m=M.fork(seed);pickup(m,slot);m.ram[2][0x5d0]=armor
  call=M.invoke(m,'HandlePowerUpCollision',x=slot)
  assert m.ram[2][0x5d0]==128 and m.ram[2][0x528]==48 and m.ram[2][0x7e7]==10,(slot,armor,call,[m.ram[2][a] for a in [0x5d0,0x528,0x7e7]],M.get(m,'PlayerStatus'))
  assert M.get(m,'PlayerStatus')==1 and m[address(b,'Enemy_Flag')+slot]==0
  assert M.get(m,'Square2SoundQueue')==address(b,'Sfx_PowerUpGrab')
  cases+=1
 rejects=0
 for slot,phase in itertools.product(range(6),[0,1,16,127]):
  m=M.fork(seed);pickup(m,slot,mature=phase);before=bytes(m.ram[2]);result=M.invoke(m,'HuPickup',x=slot)
  assert not result['P']&1 and m[address(b,'Enemy_Flag')+slot]==1 and m.ram[2]==before
  rejects+=1
 fallback=0
 for slot,typ in itertools.product(range(6),[2,3]):
  m=M.fork(seed);pickup(m,slot,typ=typ);reference=M.fork(m)
  M.invoke(m,'HandlePowerUpCollision',x=slot);M.invoke(reference,'MarioSourcePowerupCollision',x=slot)
  for name in ['Enemy_Flag','PlayerStatus','StarInvincibleTimer','NumberofLives','Square2SoundQueue','FloateyNum_Control']:
   assert M.get(m,name,slot if name in ['Enemy_Flag','FloateyNum_Control'] else 0)==M.get(reference,name,slot if name in ['Enemy_Flag','FloateyNum_Control'] else 0),(name,slot,typ)
  fallback+=1
 result=dict(passed=True,ROM_sha256=q['ROM_sha256'],cold_buffered_readback_rows=12,PPU_reads=24600,actual_cartridge_extra_image=True,mushroom_collection_cases=cases,emerging_pickup_rejections=rejects,native_star_life_comparisons=fallback,scope='Actual cold ROM loader/readback and HandlePowerUpCollision chain in CPU model. Pickup position/armor fixtures; not controller-earned or native Mesen injury proof. Flower and source armor graphics/audio remain incomplete.',installed=False)
 (P.O/'pickup-CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
