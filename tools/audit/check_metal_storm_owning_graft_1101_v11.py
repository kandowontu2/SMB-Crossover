"""Execute owning-ROM loader, real copied code/gates and donor differential."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback,collections
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_owning_graft_1101_v11 as P
import metal_storm_cpu_1101_v2 as M
from arthur_cache_host_controls_v1 import OverlayMemory
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
from check_metal_storm_palette_host_1101_v9 import sourcepixels
O=P.O;sha=P.sha

class Bus(OverlayMemory):
 def __init__(self,b):self.state_reads=0;self.fault=None;self.armed=False;super().__init__(b)
 def __getitem__(self,a):
  if isinstance(a,int)and 0xc000<=a<0xcd00 and self.rawtags[2]==2:self.state_reads+=1
  return super().__getitem__(a)
 def __setitem__(self,a,v):
  if isinstance(a,int)and a>=0x8000 and self.fault:
   raw=self.rawtags[(a-0x8000)//8192]
   if not raw&128 and (raw&3,a&8191)==self.fault and v:self.armed=True;self.corrupt_at=self.fault
  super().__setitem__(a,v)

def main():
 q=dict(passed=False,native=False,installed=False,menu_admitted=False,PRG_granted=False,RAM_granted=False)
 try:
  stage=json.loads((O/'owning-link.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  assert sha(O/'candidate.nes')==stage['ROM_sha256'];b=qualified(O/'candidate.nes');raw=b['raw'];lab=stage['labels'];cookie=bytes.fromhex(stage['cookie'])
  # No source/opcode/CHR patch or synthetic helper overlay is applied to b.
  minimum=224;maxcycles=0;hits=collections.Counter();ports=collections.Counter();digest=hashlib.sha256();executed=set()
  smc=[address(b,n)+d for n,d in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
  def put(m,**kw):
   for n,v in kw.items():m[address(b,n)]=v
  def run(m,pc,a=85,x=7,y=91,p=0x71,callback_ports=(),cold=False,deny_state=False):
   nonlocal minimum,maxcycles
   c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5ffe);start=c.processorCycles
   if deny_state:m.state_reads=0
   for _ in range(1000000):
    if c.pc==0x5fff:break
    minimum=min(minimum,c.sp)
    if c.pc in callback_ports:ports[c.pc]+=1;c.pc=(c.stPopWord()+1)&65535;continue
    if isinstance(m,Bus)and c.pc>=0x8000:
     tag=m.rawtags[(c.pc-0x8000)//8192];executed.add(tag)
     if cold:assert tag&128,('Coldloader RAM opcode',hex(c.pc),tag)
     if deny_state:assert tag&128,('Unauthenticated opcode',hex(c.pc),tag)
     for n,t in [('MetaspriteRenderLoop',132),('X5SetPhysicalChr',190),('X5PublishChr',190)]:
      if tag==t and c.pc==address(b,n):hits[n]+=1
    assert m[c.pc]!=0,('BRK',hex(c.pc),getattr(m,'rawtags',None));c.step()
   else:raise AssertionError(('CPU bound',hex(c.pc)))
   assert c.sp==224
   if deny_state:assert m.state_reads==0,m.state_reads
   maxcycles=max(maxcycles,c.processorCycles-start)
   return c.a,c.x,c.y,c.p&0xcf
  def make(bankc=215,wide=0):
   m=Bus(b)
   for bank in range(4):m.ram[bank][:]=bytes((i*17+bank*29+7)&255 for i in range(8192))
   m.raw_page(1,223);m.raw_page(2,bankc)
   put(m,CurrentBank=223,CurrentBankC=bankc,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,NmiDisable=255,HorizontalScroll=73,VerticalScroll=32,ReloadCHRBank=7,SsChrActive=0,InvHudActive=0,X5WideChrActive=wide,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0,GamePauseStatus=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Player_SprAttrib=0,VRAM_Buffer1_Offset=0)
   m.ppuctrl=160
   init=[18,20,21,22,23,24,25,26,4,5,6,7]
   for i,v in enumerate(init):m[address(b,'CurrentCHRBank')+i]=v;m[address(b,'X5ChrMode')+i]=0
   for i in range(11):m[i]=(i*31+15)&255
   for i,at in enumerate(smc):m[at]=43+i*17
   m.writes.clear();m.ram_writes.clear();return m
  def direct(m,bank,name,**kwargs):
   m.raw_page(1,128|bank);put(m,CurrentBank=128|bank);return run(m,lab[name],**kwargs)
  def load(m,expect=True):
   m.raw_page(1,223);put(m,CurrentBank=223)
   maps=m.rawtags[:];fore=bytes(m[:11]);saved=bytes(m[i]for i in smc);others=[bytes(z)for z in m.ram[:2]];oldreload=m[address(b,'ReloadCHRBank')]
   got=run(m,lab['Ms8Load'],cold=True);assert got==(85,7,91,0x41 if expect else 0x40),got
   assert m.rawtags==maps and bytes(m[:11])==fore and bytes(m[i]for i in smc)==saved
   assert others==[bytes(z)for z in m.ram[:2]]and m[address(b,'ReloadCHRBank')]==oldreload
  def exact(m):
   actor=(O/'actor.bin').read_bytes();render=(O/'render.bin').read_bytes();a=bytearray([255])*8192;a[:len(actor)]=actor;a[0x1fe0:0x1ff0]=cookie
   c=bytearray(8192);c[0xd00:0xd00+len(render)]=render;c[0xd00+len(render):0x1900]=bytes(0x1900-0xd00-len(render));c[0x1fe0:0x1ff0]=cookie
   assert bytes(m.ram[3])==a and bytes(m.ram[2])==c
  def publish(m):
   old=m.rawtags[1];m.raw_page(1,190);put(m,CurrentBank=190);run(m,address(b,'X5PublishChr'));m.raw_page(1,old);put(m,CurrentBank=old)
  cold=0
  for bankc,wide in itertools.product([2,3,215],[0,1]):
   m=make(bankc,wide);publish(m);latches=m.chr_latches[:];load(m);exact(m)
   assert m.ppu_reads==22550 and m.chr_latches==latches and m.ppuctrl==160
   assert m.ppu_log[-2:]==[(0x2005,73),(0x2005,32)]
   before=m.ppu_reads;writes=len(m.ram_writes);load(m);assert m.ppu_reads==before and len(m.ram_writes)==writes
   digest.update(bytes(m.ram[3]));digest.update(bytes(m.ram[2]));cold+=1
  failures=0
  render=(O/'render.bin').read_bytes();last_nonzero=next(i for i in range(0x800,len(render))if render[i])
  for fault in[(3,17),(3,0x1c00),(2,0xd00),(2,0x1100),(2,0xd00+last_nonzero)]:
   m=make();m.fault=fault;load(m,False);assert m.armed and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0;failures+=1
  auth=0
  for bank,index,name in itertools.product([2,3],range(16),['MsRenderGate','Ms11UpdateGate']):
   m=make();load(m);m.ram[bank][0x1fe0+index]^=1;m.raw_page(2,2);put(m,CurrentBankC=2);m[0xc800]=167
   before=[bytes(z)for z in m.ram];got=direct(m,78,name,deny_state=True)
   assert got==(85,7,91,0x40)and before==[bytes(z)for z in m.ram];auth+=1
  # Every body/shot source packet uses the actual loaded C2 producer and the
  # exact physical pages emitted by Main. Deliberate player palette adaptation
  # is compared by bitplane indices, shapes/alpha/facings/gravity stay exact.
  art=json.loads((P.V7/'art.json').read_text());pixelcases=0
  def image(m):
   out={}
   for off in range(0,m[address(b,'CurrentOAMOffset')],4):
    yy,t,a,xx=m[0x200+off:0x204+off];slot=(t&1)*4+((t&254)*16)//1024;at=1048592+m.chr_latches[slot]*1024+((t&254)*16)%1024
    for xy,v in sourcepixels([dict(dx=xx,dy=yy+1,pattern_index=0,attributes=a)],raw[at:at+32],(0,0)).items():out.setdefault(xy,v)
   return out
  m=make();load(m);m.raw_page(2,2);put(m,CurrentBankC=2);publish(m);world=m.chr_latches[:]
  for kind,records in [('body',art['body_packets']),('shot',art['shot_packets'])]:
   for r in records:
    if kind=='shot'and r['type']==131 and r['phase']>2:continue
    m[0xc000:0xc8a1]=bytes(0x8a1);m[0xc800]=167;put(m,CurrentOAMOffset=0)
    if kind=='body':
     values={0x480:128,0x4b0:112,0x510:128,0x4e0:r['state'],0x4f8:r['frame'],0x540:r['facing']|r['gravity']};data=(P.V7/'body.chr').read_bytes();mapping=[0,1,3,1]
    else:values={0x482:128,0x4b2:112,0x512:128,0x52a:r['type'],0x542:r['flags'],0x55a:0 if r['vertical']else 12,0x632:r['phase']};data=(P.V7/'shots.chr').read_bytes();mapping=[0,1,2,3]
    for a,v in values.items():m[0xc000+a]=v
    fore=bytes(m[:11]);saved=bytes(m[i]for i in smc);got=direct(m,78,'MsRenderGate');assert got==(85,7,91,0x41)
    assert bytes(m[:11])==fore and bytes(m[i]for i in smc)==saved
    publish(m);expected=sourcepixels(r['cells'],data,mapping=mapping,palette0=True);actual=image(m)
    assert expected==actual,(kind,r,len(expected),len(actual));assert all(m.chr_latches[i]==world[i]for i in[1,2,3,4,7,8,9,10,11])
    digest.update(repr(sorted(actual.items())).encode());pixelcases+=1
  # Original donor differential through the new ROM Update entry. The original
  # source constructor was separately proven against911B/90EB/9371/943C in v5;
  # here it is actually reached from the authenticated owning-ROM gate.
  fields=json.loads((R/'build/metal-storm-objects-host-1101-v6/assembly.json').read_text())['source_fields']
  def terrain(om,nm):
   for row,col in itertools.product(range(15),range(20)):
    solid=row>=13;om[0x300+row*20+col]=248 if solid else 0
    if row>=2:nm[0x300+(col//16)*208+(row-2)*16+(col&15)]=97 if solid else 0
  def original_draw(om):
   camera=bytes(om[0x710:0x714]);om.regs[6:8]=[12,13];om.map();table=om[0x800e]+256*om[0x800f];om[0x24]=table&255;om[0x25]=table>>8
   om[0x61]=0;om[0x710]=om[0x711]=om[0x713]=0;om[0x42]=252
   for slot in([3,2,1,0]if om[0x53]&1 else[0,1,2,3]):
    if om[0x510+slot]&128:run(om,0xf282,x=slot,y=om[0x61])
   om[0x710:0x714]=camera;om.regs[6:8]=[0,1];om.map()
  frames=duplicates=paused=shots=0;gravity=set();boundary_ports={0x5000,0x5006,0x5009,0x5018}
  for axis in['walk','jump','reverse','shoot-right','shoot-up','shoot-down']:
   nm=make();load(nm);nm.raw_page(2,2);put(nm,CurrentBankC=2,Player_X_Position=72,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,GamePauseStatus=1)
   # Source C1 means handled, including paused/duplicate epochs. Deltas and
   # durable state, rather than carry, prove no repeated simulation.
   first=direct(nm,78,'Ms11UpdateGate',a=255,x=7,callback_ports=boundary_ports)
   assert first==(255,7,91,0x41),('first paused constructor update',first,nm[0xc800],nm[0xc732],nm[0xc733])
   assert nm[0xc800]==167 and nm[0xc732]==255 and nm[0xc733]==7
   om=M.machine().memory;om.regs[6:8]=[0,1];om.map();om[:2048]=bytes(nm[0xc000:0xc800]);terrain(om,nm);put(nm,GamePauseStatus=0)
   for tick in range(96):
    pad=(1 if tick<48 else 2)if axis=='walk'else(129 if tick%48<20 else 1)if axis=='jump'else(136 if tick in[4,5]else 132 if tick in[48,49]else 0)if axis=='reverse'else 64 if axis=='shoot-right'else 72 if axis=='shoot-up'else 68
    nm[fields['SavedJoypadBits']]=pad;nm[fields['FrameCounter']]=(tick+200)&255
    run(om,0xad8c,callback_ports={0x8874,0x9ed7,0xff18,0xff39});om.regs[6:8]=[4,5];om.map()
    for slot in[3,2,1]:
     if om[0x510+slot]&128:run(om,0x8e54 if om[0x528+slot]==131 else 0x8eae,x=slot)
    om.regs[6:8]=[0,1];om.map();fore=bytes(nm[:11]);saved=bytes(nm[i]for i in smc)
    assert direct(nm,78,'Ms11UpdateGate',callback_ports=boundary_ports)==(85,7,91,0x41)
    assert bytes(nm[:11])==fore and bytes(nm[i]for i in smc)==saved
    om[0x31]=int(f'{pad:08b}'[::-1],2);original_draw(om);put(nm,CurrentOAMOffset=0);direct(nm,78,'MsRenderGate')
    diffs=[(hex(i),om[i],nm[0xc000+i])for i in range(0x480,0x750)if not 0x6a8<=i<0x6ac and om[i]!=nm[0xc000+i]];assert not diffs,(axis,tick,diffs[:12])
    before=bytes(nm[0xc000:0xc800]);native_before=bytes(nm[fields[n]]for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos'])
    assert direct(nm,78,'Ms11UpdateGate',callback_ports=boundary_ports)[3]&1
    assert before==bytes(nm[0xc000:0xc800])and native_before==bytes(nm[fields[n]]for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']);duplicates+=1
    put(nm,GamePauseStatus=1);assert direct(nm,78,'Ms11UpdateGate',callback_ports=boundary_ports)[3]&1;assert before==bytes(nm[0xc000:0xc800]);put(nm,GamePauseStatus=0);paused+=1
    gravity.add(om[0x734]);shots+=bool(om[0x512]|om[0x513]);frames+=1;digest.update(bytes(nm[0xc480:0xc750]))
  assert gravity=={0,128}and shots
  q.update(passed=True,ROM_sha256=stage['ROM_sha256'],code_or_helper_overlays=False,owning_carrier_loader_cases=cold,cold_buffered_reads=22550,owning_carrier_readback_failure_cases=failures,owning_full_header_rejections=auth,owning_source_pixel_cases=pixelcases,owning_original_constructor_routes=6,donor_differential_frames=frames,duplicate_guards=duplicates,pause_guards=paused,gravity_directions=sorted(gravity),shot_frames=shots,original_physics_exact=True,R0_R7_and_NMI00_02_and_fiveSMC_preserved=True,minimum_standalone_SP=minimum,maximum_standalone_cycles=maxcycles,actual_native_helper_hits=dict(hits),original_unported_callback_ports={hex(k):v for k,v in ports.items()if k in boundary_ports},original_callback_ports_disclosed=True,aggregate_sha256=digest.hexdigest(),scope='Private owning ROM, actual buffered CHR coldcopy/readback/auth/gate, real native block/OAM/CHR helpers, original donor differential. Source callback ports are explicit. No actual Main/ISR/scene/menu retirement or native admission.')
  inputs=[Path(__file__),Path(P.__file__),P.REF,Path(M.__file__),M.ROM,O/'owning-link.json',O/'candidate.nes',O/'candidate.dbg',O/'cookie.bin',P.V7/'art.json',R/'build/metal-storm-terrain-host-1101-v5/CPU-controls.json',R/'build/metal-storm-objects-host-1101-v6/assembly.json']
  q['bindings']={str(p.resolve()):sha(p)for p in inputs}
 except Exception:q['error']=traceback.format_exc();raise
 finally:(O/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','error']}))
if __name__=='__main__':main()
