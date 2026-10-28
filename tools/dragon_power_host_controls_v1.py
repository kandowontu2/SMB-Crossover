"""Real compiled host renderer/publisher and bounded caller/IRQ controls.

CPU+mapper model only, not a PPU/NMI/native timing observation.
"""
import json,re,sys
import dragon_power_component_v1 as B
import dragon_power_controls_v1 as C
import dragon_power_art_v1 as A
from py65.devices.mpu6502 import MPU
sys.path.insert(0,str(B.ROOT/'tools/audit'))
from verify_native_relocation import NesMPU
class Memory:
 base=None
 smc=None
 def __init__(self,code,s):
  if Memory.base is None:
   Memory.base=B.HOST.with_suffix('.nes').read_bytes()
   for line in B.HOST.with_suffix('.dbg').open():
    if line.startswith('seg\t')and 'name="SMCCODE"'in line:
     d=dict(re.findall(r'(\w+)=("[^"]*"|[^,\r\n]+)',line));a=int(d['start'],0);o=int(d['ooffs'],0);n=int(d['size'],0)
     Memory.smc=(a,o,n);break
  self.rom=bytearray(Memory.base);self.ram=bytearray(32768)
  self.bank=[126,86,85,127];self.log=[]
  self.rom[16+86*8192+0x800:16+86*8192+0x800+len(code)]=code
  art=(B.OUT/'art.bin').read_bytes();self.rom[16+85*8192+0x900:16+85*8192+0x900+len(art)]=art
  a,o,n=Memory.smc;self.ram[a:a+n]=self.rom[o:o+n]
  self.ram[s['CurrentBank']]=0xd6;self.ram[s['CurrentBankC']]=0xd5
  for n,v in dict(SelectedCharacter=24,NumberofLives=2,AreaType=1,AreaAddrsLOffset=0,WorldNumber=0,
   Player_Y_Position=100,Player_Y_HighPos=1,Player_X_Position=100,Player_PageLoc=0,
   Player_Rel_XPos=100,PlayerFacingDir=1,GameEngineSubroutine=8,DpReady=0x44,DpLife=2,
   DpArea=32,DpWorld=0,DpHP=100).items():self.ram[s[n]]=v
  self.ram[0x5204]=128
 def __getitem__(self,a):
  if isinstance(a,slice):return bytes(self[i]for i in range(*a.indices(65536)))
  a&=65535
  return self.ram[a]if a<32768 else self.rom[16+self.bank[(a-32768)//8192]*8192+(a&8191)]
 def __setitem__(self,a,v):
  if isinstance(a,slice):
   ids=list(range(*a.indices(65536)));assert len(ids)==len(v)
   for p,q in zip(ids,v):self[p]=q
   return
  a&=65535;v&=255;self.log.append((a,v))
  if a<32768:self.ram[a]=v
  if 0x5114<=a<=0x5117:self.bank[a-0x5114]=v&127
def symbols():
 s=B.labels(B.HOST.with_suffix('.lbl'))
 return s
def execute(m,pc,inject=None,**kw):
 c=NesMPU(memory=m,pc=pc);c.a=kw.get('a',0);c.x=kw.get('x',0);c.y=kw.get('y',0);c.p=kw.get('p',0x20);c.sp=0xfd
 c.lowest_sp=c.sp
 m[0x1fe]=255;m[0x1ff]=5;trace=[];irq=None
 for _ in range(40000):
  c.lowest_sp=min(c.lowest_sp,c.sp)
  if c.pc==0x600:return c,trace,irq
  if c.pc==inject and irq is None:
   before=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,list(m.bank))
   smc_before=bytes(m.ram[Memory.smc[0]:Memory.smc[0]+Memory.smc[2]])
   c.irq()
   for _ in range(2000):
    c.lowest_sp=min(c.lowest_sp,c.sp)
    c.step()
    if c.pc==before[0]:break
   after=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,list(m.bank))
   assert after==before,('actualIRQcontext',before,after)
   assert bytes(m.ram[Memory.smc[0]:Memory.smc[0]+Memory.smc[2]])==smc_before,'actualIRQallSMCrestore'
   irq=dict(pc=f'{before[0]:04X}',state='exactCPU/SP/mapper/entireSMCCODErestore')
  trace.append(c.pc);assert m[c.pc]!=0,('BRK',hex(c.pc),trace[-10:]);c.step()
 raise AssertionError(('noRTS',hex(c.pc)))
def decoded(chr,page,oam,origin=(100,100)):
 px={}
 for y,t,p,x in reversed(oam):
  pair=chr[page*1024+(t&63)//2*32:page*1024+(t&63)//2*32+32]
  for yy in range(16):
   for xx in range(8):
    sy=15-yy if p&128 else yy;sx=7-xx if p&64 else xx;at=sy//8*16+sy%8
    v=(pair[at]>>(7-sx)&1)|((pair[at+8]>>(7-sx)&1)<<1)
    if v:px[x-origin[0]+xx,y+1-origin[1]+yy]=(v,p&3)
 return px
def main():
 code,s=B.build();s.update({k:v for k,v in symbols().items()if k not in s})
 chr=(B.OUT/'chr.bin').read_bytes();renders=[]
 for pose,wave in [(i,False)for i in range(32)]+[(0,True)]:
  for face in [0,64]:
   m=Memory(code,s);m[s['DpPose']]=pose;m[s['DpAttribute']]=face
   if wave:
    m[s['DpShotState']]=0x82 if face==0 else 0x43;m[s['DpShotX']]=100;m[s['DpShotY']]=116
   c,trace,_=execute(m,s['DpDrawShots']if wave else s['DpDrawBody'])
   n=m[s['CurrentOAMOffset']];o=[tuple(m[i:i+4])for i in range(0x200,0x200+n,4)]
   source,_,_=A.pixels(pose,face,wave);expected={(x,y+16):v for (x,y),v in source.items()}
   page=m[s['SmChrBank']]-788%256
   assert decoded(chr,page,o)==expected,('actualnativepixels',pose,face,wave,page)
   assert m.bank[1]==86 and m[s['CurrentBank']]==0xd6
   assert m.bank[2]==85 and m[s['CurrentBankC']]==0xd5
   assert all(not 0x4000<=p<=0x4017 for p,v in m.log),'NohardwareAPU/DMAfromrenderCPUcontrol'
   renders.append(dict(pose=pose,wave=wave,face=face,actual_parts=len(o),cycles=c.processorCycles,page=788+page,min_SP=c.lowest_sp))
 # Preserve all foreign gameplay state: imported hooks do not trust an overlay.
 foreign=0
 for char in range(256):
  if char==24:continue
  for name in ['DpEnsure','DpMovement','DpPickup','DpInjuryStart','DpCollisionBounds','DpStompPolicy',
   'DpGraphics','DpGraphicsBank','DpDrawBody','DpDrawShots','DpPalettePointer','DpPublish','DpRender','DpSetRecord','DpBuildAttackPoint','DpTryContact']:
   m=Memory(code,s);m[s['SelectedCharacter']]=char;before=bytes(m.ram)
   c,_,_=execute(m,s[name],a=1,x=0)
   assert m.ram[:0x100]==before[:0x100]and m.ram[0x200:]==before[0x200:],('foreign',char,name)
   assert m.bank==[126,86,85,127]
   foreign+=1
 # ActualHP protection budget: source-owned queued injury, eightupdate cadence.
 health=[]
 for hp in [1,30,31,100,149,150]:
  for damage in [0,1,5,6,255]:
   m=Memory(code,s);m[s['DpHP']]=hp
   execute(m,s['DpInjuryStart'],a=damage)
   for tick in range(1,65):
    m[s['DpClock']]=tick;m[s['DpCueCount']]=0
    execute(m,s['DpHealthTick'])
    assert m[s['DpHP']]==max(0,hp-min(damage,tick//8))
    assert m[s['DpProtection']]==max(0,damage-tick//8)
   health.append([hp,damage,m[s['DpHP']],m[s['DpProtection']]])
 original_health=[]
 for hp in [1,30,31,100]:
  for damage in [0,1,5]:
   for period in [0,1,3]:
    for flags in [0,32]:
     a=A.O.Memory(0);a.ram[0x2e]=hp;a.ram[0x2f]=damage;a.ram[0xd9]=flags
     a.ram[0xe5]=int(period==0);a.ram[0xf9]=int(period==3)
     for p in range(0x688,0x700,20):a.ram[p]=255
     m=Memory(code,s);m[s['DpHP']]=hp;m[s['DpProtection']]=damage
     m[s['DpFlags']]=flags;m[s['DpHungerPeriod']]=period
     cues=0
     for tick in range(1,129):
      a.ram[0x26]=tick&255;a.ram[0x27]=tick%60
      m[s['DpClock']]=tick&255;m[s['DpSecondPhase']]=tick%60;m[s['DpCueCount']]=0
      A.O.call(a,0x9a33);execute(m,s['DpHealthTick'])
      assert [m[s[n]]for n in ['DpHP','DpProtection','DpHunger']]==[a.ram[0x2e],a.ram[0x2f],a.ram[0x2b]],('originalHealth',hp,damage,period,flags,tick)
      expected=[v for p,v in a.writes if p==0x16]
      assert list(m[s['DpCues']:s['DpCues']+m[s['DpCueCount']]])==expected,('originalHealthCues',expected)
      cues+=len(expected)
     original_health.append([hp,damage,period,flags,m[s['DpHP']],m[s['DpProtection']],m[s['DpHunger']],cues])
 # Genuine original point construction and asymmetrical collision primitives.
 point_cases=0
 for pose in [0,5,6,0x15,0x16,0x1a]:
  for face in [0,128]:
   a=A.O.Memory(0);a.ram[0x30]=pose;a.ram[0x35]=face;a.ram[0xf7]=100;a.ram[0xf8]=116
   A.O.call(a,0xfbb9)
   m=Memory(code,s);m[s['DpPose']]=pose;m[s['DpHorizontal']]=face;m[s['DpX']]=100;m[s['DpY']]=116
   execute(m,s['DpSourceBuildPoint'])
   assert [m[s[n]]for n in ['DpAttackX','DpAttackY','DpAttackKind']]==[a.ram[0x85],a.ram[0x86],a.ram[0x44b]]
   for dx in [-9,-8,-1,0,7,8,9]:
    for dy in [-13,-12,-1,0,11,12,13]:
     a.ram[0x503]=(a.ram[0x85]+dx)&255;a.ram[0x502]=(a.ram[0x86]+dy)&255
     m[s['DpTargetX']]=a.ram[0x503];m[s['DpTargetY']]=a.ram[0x502]
     ca=A.O.call(a,0xfc22,x=0);cb,_,_=execute(m,s['DpSourceTestPoint'])
     assert cb.p&1==ca['P']&1
     point_cases+=1
 # Actual parentIRQ may interrupt each observed caller instruction; no PPU/NMI
 # or automatic hardware IRQ scheduler is modelled. Source restoration only.
 baseline=Memory(code,s);baseline[s['DpPose']]=6
 end,trace,_=execute(baseline,s['DpDrawBody'])
 unique=sorted(set(pc for pc in trace if pc>=0xa800 and pc<0xc000))
 irqs=[]
 for pc in unique:
  m=Memory(code,s);m[s['DpPose']]=6
  c,_,q=execute(m,s['DpDrawBody'],inject=pc)
  assert q and (c.a,c.x,c.y,c.p&0xcf,c.sp)==(end.a,end.x,end.y,end.p&0xcf,end.sp)
  assert m.ram[0x5c00:0x5c80]==baseline.ram[0x5c00:0x5c80]
  irqs.append(q)
 proof=dict(status='PASS_FINITE_COMPILED_SOURCE_HOST_CONTROLS',parent=A.O.D.binding(B.HOST.with_suffix('.nes')),
  render_cases=renders,foreign_hooks=foreign,queued_health_cases=health,original_health_128_update_campaigns=original_health,original_point_cases=point_cases,
  actual_parent_IRQ_cases=irqs,art=A.O.D.binding(B.OUT/'art.bin'),core=A.O.D.binding(B.OUT/'component.bin'),
  limits=['CPU/mapper model, no nativePPU/NMI/audio/cadence proof','IRQ branch has controlled nativeIRQ MMIO; not allhardwareinterruptphases; nonhardwareB/U bits excluded, allNV/D/I/Z/C physical flags strict',
   'Caller must perform real enemyeligibility/HPdamage/epoch and block-output consumption','Two native palette roles require shared integration; no fullpalette image queued'])
 p=B.OUT/'host-controls.json';p.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(output=A.O.D.binding(p),renders=len(renders),foreign=foreign,health=len(health),points=point_cases,IRQ=len(irqs)),indent=2))
if __name__=='__main__':main()
