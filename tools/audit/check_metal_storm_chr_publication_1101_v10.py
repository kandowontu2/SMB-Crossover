"""Actual current setter/clear/menu-restore with real lag NMI instruction cuts."""
from pathlib import Path
import collections,hashlib,json,sys,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
from arthur_cache_host_controls_v1 import OverlayMemory
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
OUT=ROOT/'build/metal-storm-chr-closure-1101-v10';V8=ROOT/'build/metal-storm-resource-host-1101-v8'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
TARGETS=set([247,248,249,250]+list(range(494,503))+list(range(827,832)))
def main():
 q=dict(passed=False,native=False,installed=False,resource_granted=False,global_CHR_consumer_closure=False)
 try:
  cp=OUT/'current-consumer-inputs.json';cur=json.loads(cp.read_text());domains=json.loads((OUT/'source-domains.json').read_text());assert domains['passed'];raw=(ROOT/'build/kirby-owner-main-1101-v2/candidate.nes').read_bytes();assert hashlib.sha256(raw).hexdigest()==cur['current_ROM_sha256']
  w=json.loads((V8/'native-witness.json').read_text());syms=dict(w['syms']);syms.update(cur['syms']);b=dict(raw=raw,syms=syms,segs=cur['segments']);digest=hashlib.sha256();minimum=224;pages=collections.Counter();actual_chr_writes=0;interrupts=0;audio_ports=0;pending_A_restores=collections.Counter()
  for s in cur['native_spans']:assert raw[s['offset']:s['offset']+s['size']]==bytes.fromhex(s['hex'])
  assert bytes.fromhex(next(s['hex']for s in cur['native_spans']if s['name']=='GameLoop')).startswith(bytes.fromhex('a9ff8d3901'))
  class Bus(OverlayMemory):
   def __setitem__(self,i,v):
    nonlocal actual_chr_writes
    super().__setitem__(i,v)
    if isinstance(i,int)and 0x5120<=i<=0x512b:
     page=self.chr_latches[i-0x5120];pages[page]+=1;actual_chr_writes+=1
     assert page not in TARGETS,('Unowned CHR page published',page,hex(i),v,self.upper)
  def put(m,**kw):
   for n,v in kw.items():m[address(b,n)]=v
  def field(m,n):return m[address(b,n)]
  def fresh(rawchar=22,variant=0,oldpage=493):
   m=Bus(b);m.raw_page(1,190);m.raw_page(2,215);put(m,CurrentBank=190,CurrentBankC=215,SelectedCharacter=rawchar,MarioVariant=variant,NmiDisable=255,FamilyMainCommit=1,DisableScreenFlag=0,Mirror_PPUCTRL=160,Mirror_PPUMASK=30,ReloadCHRBank=1,SsChrActive=0,InvHudActive=0,X5WideChrActive=1)
   init=[18,20,21,22,23,24,25,26,4,5,6,7]
   for i,low in enumerate(init):m[address(b,'CurrentCHRBank')+i]=low;m[address(b,'X5ChrMode')+i]=0
   m[address(b,'CurrentCHRBank')]=oldpage&255;m[address(b,'X5ChrMode')]=128|(oldpage>>8)
   m[0:11]=bytes((29*i+17)&255 for i in range(11));m[0x200:0x300]=bytes([240,0,0,0])*64
   # The initial known hardware publication precedes the cut fixtures. Its
   # source pairs are legal; no target-page selection is hidden by the model.
   publish(m);put(m,ReloadCHRBank=1);m.writes.clear();m.ram_writes.clear();return m
  def sub(m,pc,a=85,x=7,y=91,p=0x71):
   c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5ffe);return c
  def execute(c):
   nonlocal minimum
   for _ in range(100000):
    if c.pc==0x5fff:break
    minimum=min(minimum,c.sp);assert c.memory[c.pc]!=0,('BRK',hex(c.pc));c.step()
   else:raise AssertionError(('CPU bound',hex(c.pc)))
   assert c.sp==224;return c
  def publish(m):
   old=m.rawtags[1];oldbank=field(m,'CurrentBank');m.raw_page(1,190);put(m,CurrentBank=190);execute(sub(m,address(b,'X5PublishChr')));m.raw_page(1,old);put(m,CurrentBank=oldbank)
  def nmi(c):
   nonlocal minimum,interrupts,audio_ports
   m=c.memory;old=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp);maps=m.rawtags[:];zp=bytes(m[3:11]);before=actual_chr_writes;c.nmi()
   for _ in range(10000):
    if c.pc==old[0]and c.sp==old[5]:break
    minimum=min(minimum,c.sp)
    if c.pc==address(b,'AudioUpdate'):
     # Only the source audio child is ported. Actual guard, mapper publisher,
     # bank restoration, saved register frame and RTI still execute.
     audio_ports+=1;c.pc=(c.stPopWord()+1)&65535;continue
    assert m[c.pc]!=0,('NMI BRK',hex(c.pc),m.rawtags);c.step()
   else:raise AssertionError(('NMI bound',hex(c.pc)))
   assert(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp)==old,('Real ISR caller ABI',old,(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp))
   assert zp==bytes(m[3:11]),'Actual ISR foreground scratch preservation'
   if maps!=m.rawtags:
    # SharedFarCall has two real shadow-before-hardware store cuts. NMI
    # restores the new shadow one instruction early; foreground resumes in
    # resident SMC and repeats precisely that pending hardware write.
    assert old[0]in[0x166,0x175]and bytes(m[old[0]:old[0]+3])==bytes.fromhex('8d1551')
    assert maps[0]==m.rawtags[0]and maps[2:]==m.rawtags[2:]and m.rawtags[1]==field(m,'CurrentBank')==c.a
    pending_A_restores[old[0]]+=1
   interrupts+=1;return actual_chr_writes-before
  # The setter has nine instructions. Each case reconstructs the preexisting
  # Reload=1 source state and inserts exactly one lag NMI at the requested cut.
  # This deliberately includes intermediate shadow pairs naming proposed pages.
  cuts=0;transient_targets=collections.Counter();guestcases=0
  lowtests=list(range(238,247))+list(range(59,64))
  for oldpage in[493,832]:
   for low in lowtests:
    for upper in[1,2,3]:
     # If the completed page is itself proposed, it is not an existing owner
     # and cannot be admitted as a legal final setter argument.
     if low+256*upper in TARGETS:continue
     for win in[0,4,8,11]:
      for cut in range(10):
       m=fresh(oldpage=oldpage);m[address(b,'CurrentCHRBank')+win]=oldpage&255;m[address(b,'X5ChrMode')+win]=128|(oldpage>>8);c=sub(m,address(b,'X5SetPhysicalChr'),a=low,x=upper,y=win)
       for _ in range(cut):
        if c.pc==0x5fff:break
        c.step()
       mode=m[address(b,'X5ChrMode')+win];pair=(mode&3)*256+m[address(b,'CurrentCHRBank')+win]
       if pair in TARGETS:transient_targets[pair]+=1
       assert nmi(c)==0,'All selected nonzero owners retain previous hardwareCHR during busy frame'
       execute(c);assert m[address(b,'CurrentCHRBank')+win]==low and m[address(b,'X5ChrMode')+win]==128|upper
       publish(m);assert m.chr_latches[win]==low+256*upper;cuts+=1
  # All legal nonzero identity values take the same real native guard branch.
  for rawchar in range(1,36):
   m=fresh(rawchar=rawchar);c=sub(m,address(b,'X5SetPhysicalChr'),a=244,x=2,y=0);c.step();assert nmi(c)==0;execute(c);guestcases+=1
  for variant in[2]:
   m=fresh(rawchar=0,variant=variant);c=sub(m,address(b,'X5SetPhysicalChr'),a=244,x=2,y=0);c.step();assert nmi(c)==0;execute(c);guestcases+=1
  assert {500,501,502,827,828,829,830,831}<=set(transient_targets),transient_targets
  q.update(actual_typed_setter_instruction_cuts=cuts,real_busy_guard_identity_cases=guestcases,unpublished_transient_proposed_pairs=dict(sorted(transient_targets.items())))
  # Native Mario is the exception: its lag path DOES publish CHR. The actual
  # menu helper must therefore be safe at every instruction, not merely at
  # return. The private cache is not executed; this is real ROM menu/farcall.
  fm=next(s for s in cur['native_spans']if s['name']=='FmNativePrepare');fmbank=(fm['offset']-16)//8192
  def menu_case(variant,cut,style):
   m=fresh(rawchar=0,variant=variant,oldpage=493)
   source=[(493,129),(756,130),(832,131),(1019,131)]
   for i in range(12):
    page,mode=source[(i+style)%len(source)];m[address(b,'CurrentCHRBank')+i]=page&255;m[address(b,'X5ChrMode')+i]=mode
   put(m,SsChrPhysical=169,X5SpecialChrUpper=1,SsChrActive=1,InvHudPhysical=251,X5HudChrUpper=3,InvHudActive=1)
   publish(m);put(m,ReloadCHRBank=1);m.raw_page(1,128|fmbank);put(m,CurrentBank=128|fmbank);c=sub(m,address(b,'FmNativePrepare'))
   for _ in range(cut):
    if c.pc==0x5fff:break
    c.step()
   if c.pc==0x5fff:return False
   nmi(c);execute(c)
   assert bytes(m[address(b,'X5ChrMode'):address(b,'X5ChrMode')+12])==bytes(12)and not field(m,'X5WideChrActive')
   assert bytes(m[address(b,'CurrentCHRBank'):address(b,'CurrentCHRBank')+8])==bytes([18,20,21,22,23,24,25,26]);publish(m)
   return True
  nativecuts=0
  for variant in[0,1,3,4,5,6]:
   for style in range(4):
    for cut in range(160):
     if not menu_case(variant,cut,style):break
     nativecuts+=1
  q.update(actual_native_Mario_menu_clear_restore_cuts=nativecuts,actual_native_Mario_variants=[0,1,3,4,5,6],NmiDisable_alone_is_not_CHR_fence=True,FamilyMainCommit_alone_is_not_CHR_fence=True,source_safe_order='Current QueueSelection retires without newCHRstores, FmNativePrepare clears all12 interpretation modes +override upper fields/wide flag before assigning any new native low byte. Native-Mario lag publication remains harmless at every tested instruction.')
  q.update(passed=True,current_ROM_sha256=cur['current_ROM_sha256'],real_NMI_returns=interrupts,audio_child_ports=audio_ports,actual_CHR_hardware_writes=actual_chr_writes,physical_pages_published=sorted(pages),no_proposed_page_published=True,minimum_standalone_SP=minimum,pending_resident_A_store_cuts=dict(sorted(pending_A_restores.items())),scope='Actual linked source instructions, actual farcall/CHR publisher and actual lag-NMI guard/bank restores/RTI at instruction cuts. Audio child is an explicit return port. Resident166/175 shadow-before-hardware transport cuts may restore the pending A mapping early; exact saved AXYP/SP resumes the same STA5115 instruction. No hardware/raster/full audio/native emulator or full Main admission. Source domains plus this protocol test do not yet close12funding/2Karnov moved-writer ownership replacements.')
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),cp,OUT/'source-domains.json',V8/'native-witness.json']}
 except Exception:q['error']=traceback.format_exc();raise
 finally:(OUT/'publication-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','error','physical_pages_published']}))
if __name__=='__main__':main()
