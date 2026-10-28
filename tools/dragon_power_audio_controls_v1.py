"""Original/ported audio source and actual host callback controls, CPU only."""
import json,hashlib,statistics,re
import dragon_power_audio_prepare_v1 as A
import dragon_power_host_controls_v1 as H
import dragon_power_reference_v1 as O

def main():
 code,s=A.build();s.update({k:v for k,v in H.symbols().items()if k not in s})
 frozen=H.B.OUT/'component.bin';fs=H.B.labels(H.B.OUT/'component.lbl')
 for line in (H.B.OUT/'component.dbg').read_text().splitlines():
  if not line.startswith('sym\t'):continue
  n=re.search(r'name="(Dp[^"]+)"',line);v=re.search(r'val=0x([0-9A-Fa-f]+)',line)
  if n and v:fs[n[1]]=int(v[1],16)
 s.update({k:v for k,v in fs.items()if k not in s})
 assert s['DpAudioNativeEnd']-s['DpAudioNativeStart']==5152
 class Memory(H.Memory):
  def __init__(self):
   super().__init__(frozen.read_bytes(),s)
   self.rom[16+96*8192+0x980:16+96*8192+0x980+len(code)]=code
   self.bank[1]=96;self.ram[s['CurrentBank']]=0xe0;self.images=[]
  def __setitem__(self,p,v):
   if isinstance(p,int):
    if s['GuestNativeApu']<=p<s['GuestNativeApu']+16:self.images.append((0x4000+p-s['GuestNativeApu'],v&255))
    if p==s['GuestNativeEnable']:self.images.append((0x4015,v&255))
   super().__setitem__(p,v)
 callbacks={s['GuestNativeStatusSTA']:(0x4015,False),s['DpAudioStore08']:(0x4008,False)}
 callbacks.update({s['GuestNativeStoreSTA'+f'{n:02x}'+'Y']:(0x4000+n,True)for n in range(4)})
 def call(m,pc,**kw):
  c=H.NesMPU(memory=m,pc=pc);c.a=kw.get('a',0);c.x=kw.get('x',0);c.y=kw.get('y',0);c.p=kw.get('p',0x20);c.sp=0xfd
  m[0x1fe]=255;m[0x1ff]=5;c.source_requests=[];c.lowest_sp=c.sp;c.visited=set();c.irq_receipt=None
  for _ in range(40000):
   if c.pc==0x600:return c
   c.visited.add(c.pc)
   if c.pc==kw.get('inject')and c.irq_receipt is None:
    prior=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,list(m.bank))
    zp=bytes(m.ram[:256]);smc=bytes(m.ram[H.Memory.smc[0]:H.Memory.smc[0]+H.Memory.smc[2]])
    private=actual(m)+bytes(m.ram[s['RgAudioCpuZp']:s['RgAudioCpuZp']+160])
    c.irq()
    for _ in range(2000):
     c.lowest_sp=min(c.lowest_sp,c.sp);c.step()
     if c.pc==prior[0]:break
    assert (c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,list(m.bank))==prior,'actualIRQCPU/stack/banks'
    assert bytes(m.ram[:256])==zp and actual(m)+bytes(m.ram[s['RgAudioCpuZp']:s['RgAudioCpuZp']+160])==private,'actualIRQaudio/ZP'
    assert bytes(m.ram[H.Memory.smc[0]:H.Memory.smc[0]+H.Memory.smc[2]])==smc,'actualIRQentireSMCCODE'
    c.irq_receipt=dict(pc=f'{c.pc:04X}',min_SP=c.lowest_sp)
   if isinstance(m,Memory)and c.pc in callbacks:
    expected_bank=96 if c.pc==s['DpAudioStore08']else 127
    assert m.bank[(c.pc-0x8000)//8192]==expected_bank,'genuineCallbackPhysicalBank'
    register,indexed=callbacks[c.pc];c.source_requests.append((register+(c.y if indexed else 0),c.a))
   c.lowest_sp=min(c.lowest_sp,c.sp);assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
  raise AssertionError(('noRTS',hex(c.pc)))
 def source():
  a=O.Memory(3)
  for p in range(0x688,0x700,20):a.ram[p]=255
  for event in range(4):call(a,0x98a8,a=event)
  return a
 def mapped(v):
  if 0x8040<=v<0x8f62:return s['DpAN8040']+v-0x8040
  return v
 def expected(a):
  state=bytearray(a.ram[0x688:0x700]+a.ram[0x3f0:0x3fc]+a.ram[0x12:0x17])
  for p in list(range(2,120,20))+[132,134]:
   v=mapped(state[p]|state[p+1]<<8);state[p:p+2]=v.to_bytes(2,'little')
  return bytes(state)
 def actual(m):return bytes(m.ram[s['DpAudioState']:s['DpAudioState']+137])
 valid=[i for i in range(109)if i not in list(range(33,36))+list(range(39,45))]
 campaigns=[];raw_exact=0;public_exact=0;digest=hashlib.sha256();costs=[]
 for event in [None]+valid:
  a=source();m=Memory()
  seed=bytes((i*37+19)&255 for i in range(256));m.ram[:256]=seed
  # Reinitialize actual IRQ hardware-source register after arbitrary ZP fill.
  c=call(m,s['DpAudioInit'],a=0x87,x=0x34,y=0x56,p=0x61)
  assert (c.a,c.x,c.y,c.p&0xcf,c.sp)==(0x87,0x34,0x56,0x61&0xcf,255)
  assert bytes(m.ram[:256])==seed and actual(m)==expected(a),('initialState',event)
  if event is not None:
   call(a,0x98a8,a=event);call(m,s['DpAudioRequestEvent'],a=event)
   assert actual(m)==expected(a),('request',event)
  ec=[];pcost=[];totalstores=0
  for frame in range(64):
   a.writes=[];m.images=[];m.log=[]
   old=call(a,0x8f68,a=0x34,x=0x56,y=0x78,p=0x21)
   c=call(m,s['DpAudioTick'],a=0x34,x=0x56,y=0x78,p=0x21)
   want=[(p,v)for p,v in a.writes if 0x4000<=p<=0x4017]
   assert c.source_requests==want,('orderedOriginalRequestsAtRealCallbacks',event,frame,want,c.source_requests)
   composed=[q for p,v in want for q in ([(p,v)]*2 if p==0x4015 else[(p,v)])]
   assert m.images==composed,('fullComposedImage',event,frame,composed,m.images)
   assert actual(m)==expected(a),('driverState',event,frame)
   assert (c.a,c.x,c.y,c.p&0xcf,c.sp)==(0x34,0x56,0x78,0x21&0xcf,255)
   assert bytes(m.ram[:256])==seed,('borrowedForegroundZP',event,frame)
   assert m.bank==[126,96,85,127]
   assert not any(0x4010<=p<=0x4014 for p,v in m.log),'sourceNoDMC'
   digest.update(json.dumps([event,frame,want,list(actual(m))],separators=(',',':')).encode())
   ec.append(old.processorCycles);pcost.append(c.processorCycles);totalstores+=len(want)
   costs.append([old.processorCycles,c.processorCycles]);public_exact+=1
  campaigns.append(dict(event=event,ticks=64,stores=totalstores,source_cycles=[min(ec),max(ec)],
   callback_cycles=[min(pcost),max(pcost)]))
 # Raw request/driver AXYP/SP comparison includes real source pointer relocation.
 # Public callbacks above deliberately preserve caller registers instead.
 a=source();m=Memory();call(m,s['DpAudioInit'])
 for frame in range(120):
  for i,p in enumerate(range(0x12,0x17)):m.ram[p]=m.ram[s['DpAudioState']+132+i]
  a.writes=[];m.images=[]
  ca=call(a,0x8f68,a=0x84,x=0x73,y=0x26,p=0x61)
  cb=call(m,s['DpAN8F68'],a=0x84,x=0x73,y=0x26,p=0x61)
  assert (cb.a,cb.x,cb.y,cb.p&0xcf,cb.sp)==(ca.a,ca.x,ca.y,ca.p&0xcf,ca.sp),('rawAXYP',frame)
  for i,p in enumerate(range(0x12,0x17)):m.ram[s['DpAudioState']+132+i]=m.ram[p]
  assert actual(m)==expected(a)
  raw_exact+=1
 raw_requests=0
 for event in valid:
  for i,p in enumerate(range(0x12,0x17)):m.ram[p]=m.ram[s['DpAudioState']+132+i]
  ca=call(a,0x98a8,a=event,x=0x73,y=0x26,p=0x69)
  cb=call(m,s['DpAN98A8'],a=event,x=0x73,y=0x26,p=0x69)
  assert (cb.a,cb.x,cb.y,cb.p&0xcf,cb.sp)==(ca.a,ca.x,ca.y,ca.p&0xcf,ca.sp),('rawRequestAXYP',event)
  for i,p in enumerate(range(0x12,0x17)):m.ram[s['DpAudioState']+132+i]=m.ram[p]
  assert actual(m)==expected(a)
  raw_requests+=1
 # Every public foreign call returns exact CPU/RAM/banks; invalid genuine holes
 # are explicit refused requests, never silently replaced by another song.
 foreign=0;invalid=[]
 for char in range(256):
  if char==24:continue
  for name in ['DpAudioInit','DpAudioTick','DpAudioRequestEvent','DpAudioMute']:
   m=Memory();m.ram[s['SelectedCharacter']]=char;before=bytes(m.ram)
   c=call(m,s[name],a=0x43,x=0x25,y=0x96,p=0x65)
   assert m.ram[:256]==before[:256]and m.ram[512:]==before[512:]
   assert(c.a,c.x,c.y,c.p&0xcf)==(0x43,0x25,0x96,0x65&0xcf)
   assert m.bank==[126,96,85,127];foreign+=1
 for event in range(256):
  if event in valid:continue
  m=Memory();before=actual(m);call(m,s['DpAudioRequestEvent'],a=event)
  assert actual(m)==before
  assert m.ram[s['RgAudioRequest']]==255;invalid.append(event)
 # Actual native mixer composition on a bounded no-world-effect path. The
 # original driver's unused4009/400D writes remain in its image, while the
 # existing hardware flush legitimately excludes those unused registers.
 lifecycle=[];a=source();m=Memory();call(m,s['DpAudioInit']);m.ram[s['OperMode']]=1
 for tick in range(24):
  if tick==8:
   state=actual(m)
   for _ in range(7):
    call(m,s['DpAudioMute']);m.ram[s['GamePauseStatus']]=1
    m.bank[1]=29;m.ram[s['CurrentBank']]=0x9d;finished=call(m,s['GuestAudioFinish'])
    m.bank[1]=96;m.ram[s['CurrentBank']]=0xe0
    if actual(m)!=state:
     path=A.OUT/'first-parent-silent-owner-negative.json'
     if not path.exists():path.write_text(json.dumps(dict(status='REAL_COMPILED_CPU_PARENT_SILENT_OWNER_CONFLICT',
      core=A.D.binding(A.OUT/'component.bin'),source_state_before=state.hex(),after=actual(m).hex(),
      changed_offsets=[i for i,(a,b)in enumerate(zip(state,actual(m)))if a!=b],
      actual_parent_callback='GuestAudioFinish Silent->Cv3DmcResetOwner->Cv3FxOwnerInit unconditionally clears RgAudioZp aliases for foreignraw24',
      actual_visited=[f'{p:04X}'for p in sorted(finished.visited)],no_native_run=True),indent=2)+'\n')
    assert actual(m)==state,'actualParentSilentMustNotCorruptDragonDriver'
   m.ram[s['GamePauseStatus']]=0
   assert m.ram[s['GuestNativeEnable']]==0
   lifecycle.append('7mute callbacks preserve137Bsource state and foreground ZP')
  a.writes=[];m.images=[]
  old_status=m.ram[s['DpAudioState']+120];resume=bool(m.ram[s['RgAudioSilenced']])
  call(a,0x8f68);c=call(m,s['DpAudioTick'])
  want=[(p,v)for p,v in a.writes if 0x4000<=p<=0x4017]
  assert c.source_requests==([(0x4015,old_status)]if resume else[])+want
  assert actual(m)==expected(a)
  flush=[]
  if m.ram[s['GuestNativeEnable']]!=m.ram[s['GuestCombinedEnable']]:flush.append((0x4015,m.ram[s['GuestNativeEnable']]))
  for reg in range(16):
   if reg in [9,13]:continue
   value=m.ram[s['GuestNativeApu']+reg]
   if value!=m.ram[s['GuestApuLast']+reg]or m.ram[s['GuestNativeDirty']+reg]:flush.append((0x4000+reg,value))
  m.log=[];m.bank[1]=29;m.ram[s['CurrentBank']]=0x9d
  call(m,s['GuestAudioFinish'])
  hw=[(p,v)for p,v in m.log if 0x4000<=p<=0x4017]
  assert hw==flush,('actualMixerHardware',tick,hw,flush)
  m.bank[1]=96;m.ram[s['CurrentBank']]=0xe0
  lifecycle.append(dict(tick=tick,resume=resume,actual_hardware_stores=len(hw)))
 # Actual current IRQ at every unique owned PC in cold init, one request, and
 # first source tick. It preserves live borrowed foreground ZP and all SMC.
 irqs=[]
 for name,event in [('DpAudioInit',0),('DpAudioRequestEvent',0x30),('DpAudioTick',0)]:
  baseline=Memory()
  if name!='DpAudioInit':call(baseline,s['DpAudioInit'])
  end=call(baseline,s[name],a=event)
  for pc in sorted(p for p in end.visited if 0xa980<=p<0xc000):
   q=Memory()
   if name!='DpAudioInit':call(q,s['DpAudioInit'])
   c=call(q,s[name],a=event,inject=pc)
   assert c.irq_receipt and actual(q)==actual(baseline)
   assert q.ram[s['GuestNativeApu']:s['GuestNativeApu']+16]==baseline.ram[s['GuestNativeApu']:s['GuestNativeApu']+16]
   assert q.ram[s['GuestNativeDirty']:s['GuestNativeDirty']+16]==baseline.ram[s['GuestNativeDirty']:s['GuestNativeDirty']+16]
   assert (c.a,c.x,c.y,c.p&0xcf,c.sp)==(end.a,end.x,end.y,end.p&0xcf,end.sp)
   irqs.append(dict(callback=name,**c.irq_receipt))
 proof=dict(status='PASS_FINITE_ORIGINAL_AUDIO_AND_COMPILED_HOST_CALLBACKS_CPU_ONLY',
  core=A.D.binding(A.OUT/'component.bin'),source=A.D.binding(A.D.ROM),parent=A.D.binding(H.B.HOST.with_suffix('.nes')),
  native_state_bytes=137,borrowed_ZP5_restored=True,campaigns=campaigns,public_ticks=public_exact,
  state_address=f'{s["DpAudioState"]:04X}',state_owner='RgAudioRam first137B; RgAudioZp untouched by port, unconditional parentSilent CV3 aliases harmless',
  raw_driver_AXYP_SP_ticks=raw_exact,raw_request_AXYP_SP_cases=raw_requests,foreign_calls=foreign,explicit_invalid_events=invalid,
  actual_mixer_and_mute_resume=lifecycle,actual_parent_IRQ_injections=irqs,
  exact_state_and_ordered_source_APU_image_sha256=digest.hexdigest(),
  original_cycles=[min(x[0]for x in costs),max(x[0]for x in costs)],callback_cycles=[min(x[1]for x in costs),max(x[1]for x in costs)],
  added_cycles=[min(x[1]-x[0]for x in costs),max(x[1]-x[0]for x in costs)],
  limits=['CPU/mapper model, no native/NMI scheduling/PPU/cadence or waveform proof',
   'Raw source APU store requests match at real callback entry; complete image stream includes both original helper4015 enable writes; actual native mixer composed hardware independently checked24ticks',
   'No scheduler/live foreground cue consumption; ROOT must establish atomic caller/consumer and ownership lifecycle',
   'Original unusedFFFF descriptors are explicitly refused, not treated as valid music'])
 p=A.OUT/'source-callback-controls.json';p.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(proof=A.D.binding(p),ticks=public_exact,raw_AXYP=raw_exact,cycles=proof['callback_cycles'],added=proof['added_cycles']),indent=2))
if __name__=='__main__':main()
