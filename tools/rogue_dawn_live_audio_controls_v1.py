"""Finite actual live-cue/06C4 callers and IRQs. No scheduler/native claim."""
from pathlib import Path
import itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
import rogue_dawn_audio_driver_controls_v4 as audio
import rogue_dawn_live_cue_semantics_v1 as cuts
import rogue_dawn_host_ui_controls_v1 as ui
from prepare_rogue_dawn_audio_driver_v4 import labels
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from sunny_integrated_controls_v1 import registers,app,smc_at
O=R/'build/rogue-dawn-live-audio-v1';w=ui.w
get,put=w.get,w.put

def audio_labels():
 s=labels(O/'candidate.lbl')
 s.update({n:int(a,16)for n,a in re.findall(r'^(\w+)=\$([0-9a-f]+)$',(O/'live-driver-imports.inc').read_text(),re.M)})
 return s

def main():
 assert not(O/'controls.json').exists(),'Frozen finite result'
 build=json.loads((O/'build.json').read_text())
 for q in build['bindings']:assert ref.binding(q['path'])==q,q['path']
 raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
 b=scoped_load(O/'candidate.nes');parent=scoped_load(ui.O/'candidate.nes')
 s=audio_labels();checks={};minimum=255
 proof=dict(passed=False,source_CPU_only=True,native_run=False,checks=checks)
 try:
  # Every actual original driver reference; Q2 has only one clear, no read or
  # producer. Genuine original raw data bytes are NOT operand-remapped.
  graph=json.loads((R/'docs/qa/rogue-dawn-audio-source-closure-2026-10-28.json').read_text())['graph']
  sites=[]
  for q in build['source_cue_sites']:
   pc=int(q['source_PC'],16);off=16+97*8192+(pc+0x2000&8191)
   oldbytes=bytes.fromhex(next(x['bytes']for x in graph['instructions']if x['pc']==pc))
   actual=b['raw'][off:off+3];target=int.from_bytes(actual[1:],'little')
   want=s['RdaState']+0x82 if int(q['source_operand'],16)==0x682 else 0x5c20+int(q['source_operand'],16)-0x680
   assert actual[0]==oldbytes[0] and target==want,(q,actual.hex(),want)
   sites.append(dict(**q,actual_PC=hex(pc+0x2000),compiled_bytes=actual.hex()))
  assert sum(x['source_operand']=='0x682'for x in sites)==1
  # All consumed original/source projection references are recorded. The only
  # variable queue-index helper has three literal incoming paths X=4/3/3.
  producers=[('RdScrewRequest',0,0x40),('RdJumpRequest',1,2),('RdWalkRequest',0,8),
   ('MissileRequest',0,0x20),('BombRequest',3,1),('BombExplodeRequest',0,0x10),
   ('WaveRequest',1,1),('IceRequest',1,0x10),('RdControlHurtSound',4,4),
   ('RdControlDeathSound',3,0x80),('RdControlMorphSound',3,2)]
  producer_rows=[]
  for name,idx,bit in producers:
   m=w.life.make(b);m[0x5c20:0x5c27]=bytes([0x20,0x40,0xa7,8,0x10,0x80,1])
   before=bytes(m[0x5c20:0x5c27]);c,l,tr=w.call(m,name,sp=224);minimum=min(minimum,l)
   expected=bytearray(before);expected[idx]|=bit
   assert bytes(m[0x5c20:0x5c27])==expected,(name,before.hex(),bytes(m[0x5c20:0x5c27]).hex())
   pair=[(pc,bank)for pc,bank in tr if bytes(m[pc:pc+3])in [bytes.fromhex('1d205c'),bytes.fromhex('9d205c')]]
   assert len(pair)==2 and c.x==idx,(name,pair,c.x)
   producer_rows.append(dict(name=name,real_index=idx,bit=bit,actual_OR_STA_PC=[hex(p)for p,k in pair],bank=pair[0][1],Q2_unchanged=True))
  consumed=[Path(q['path'])for q in build['bindings']if Path(q['path']).suffix in ['.s','.inc']]
  refs=[]
  for path in dict.fromkeys(consumed):
   if 'rogue_dawn'not in str(path) and path.name not in ['services-include.s','control-include.s','weapon-source.s','lifecycle-source.s','body-source.s','live-deferred.s']:continue
   for line,text in enumerate(path.read_text().splitlines(),1):
    code=text.split(';',1)[0]
    if re.search(r'\bRdSfx\b|\$5[cC]22\b',code):refs.append(dict(file=str(path),line=line,code=code.strip()))
  # Only new explicit source counter and the API Q2 reject may mention+2.
  assert not any('RdSfx+2'in q['code']and 'RdLowHpCounter='not in q['code']for q in refs),refs
  checks['compiled_queue_projection_and_old_Q2_closure']=dict(driver_sites=sites,indexed_source_producers=producer_rows,consumed_Rogue_reference_inventory=refs,
   direct_queue_producers='Spring direct queue3; scene theme queue4; authored defeat/contact queue1; all explicit source operands exclude2.',
   generic_initializers='Actual RdHsEnterScene zeroes all128 overlay bytes; RdaAudioInit explicitly zeroes six live slots once. These genuine lifecycle resets intentionally zero source06C4.',
   scope='Actual consumed source plus compiled driver graph and complete known indexed-producer entry controls; not a disassembly theorem for arbitrary corrupted RAM/indirect execution.')

  # Execute actual source B189 and health B199 prefix with original game3
  # bytes. Stop at B1AE: following source-room B133 is deliberately not SMB.
  original_image=ref.cpu_image(raw,a_bank=3,lower_bank=2)
  def source_callback(service,counter,health,image):
   m=bytearray(original_image);m[0x6c4]=counter;m[0x106],m[0x107]=health;m[0x683]=image;m[0x30a]=0x5a
   pc=0xb189 if service==8 else 0xb11c
   c=NesMPU(memory=m,pc=pc);c.sp=224;c.a=0;c.x=13;c.y=87;c.p=0x71;c.stPushWord(0x5aff)
   for _ in range(100):
    if c.pc==0x5b00 or service==7 and c.pc==0xb1ae:break
    c.step()
   else:raise AssertionError(('source callback nonreturn',hex(c.pc)))
   return m[0x6c4],m[0x683],m[0x30a]
  rows=[]
  for service,counter,health in itertools.product([7,8],range(256),[(0x00,0),(0x69,1),(0x70,1),(0x99,1),(0x00,2)]):
   expected=source_callback(service,counter,health,0x12)
   m=w.life.make(b);put(m,RdHostService=service,RdHealthLo=health[0],RdHealthHi=health[1],RdHit=0x5a)
   m[0x5c22]=counter;m[0x5c23]=0x12
   c,l,tr=w.call(m,'RdHostDispatch',a=0,x=13,y=87,p=0x71,sp=224);minimum=min(minimum,l)
   assert (m[0x5c22],m[0x5c23],get(m,'RdHit'))==expected,(service,counter,health,expected,list(m[0x5c22:0x5c24]),get(m,'RdHit'))
   assert (c.a,c.x,c.y,c.p&0xcf)==(0,13,87,(0x71&0xcf)&(~1 if service==8 else 255))
   assert m.banks[1]==95 and get(m,'CurrentBank')==223
   if counter in[0,1,59,60,63,64,255]:rows.append(dict(service=service,counter=counter,health=list(health),after_counter=m[0x5c22],queue3=m[0x5c23],CPU=c.processorCycles,minimum_SP=l))
  checks['all256_source_B189_B199_counter_and_thresholds']=dict(cases=2*256*5,selected=rows,original_room_tail_not_fabricated=True)

  # Exact original queue request order in representative phase0 normal/pause
  # contexts, with two separate queue2 canaries: live counter and privateQ2.
  apu={}
  for q in graph['instructions']:
   z=bytes.fromhex(q['bytes'])
   if len(z)==3 and 0x4000<=int.from_bytes(z[1:],'little')<=0x4017:
    apu[q['pc']+0x2000]=(q['instruction'].split()[0],int.from_bytes(z[1:],'little'),q['mode'])
  def observe(m,c):
   if c.pc>=0x8000 and m.banks[(c.pc-0x8000)//8192]==97:
    if c.pc in apu:
     op,at,mode=apu[c.pc];v=c.y if op=='STY'else c.x if op=='STX'else c.a
     m.requests.append([at+(c.y if mode=='aby'else 0),v])
    elif c.pc==0xd386:m.requests.append([m[0xe0]+256*m[0xe1]+c.y,c.a])
  def acall(m,name,**kw):return cuts.call(m,s[name],observe=lambda c:observe(m,c),**kw)
  cases=[]
  for mode,image,counter in itertools.product([3,5],[[0]*6,[0,2,0,0,0,0],[0,0,0,2,0,0],[0x42,0x12,0xa5,2,0x40,0x10],[1,0x12,0xa5,2,0x40,0x10]],[0,60,255]):
   src=cuts.source(raw,mode);host=audio.Host(b['raw'],s);src[0x680]=1
   acall(host,'RdaAudioInit');acall(host,'RdaAudioSetMode',a=mode)
   req,_=cuts.source_tick(src);host.requests=[];acall(host,'RdaAudioTick');assert req==host.requests
   src[0x680:0x686]=image
   for i,v in enumerate(image):
    if i==2:host[s['RdaState']+0x82]=v
    else:host[0x5c20+i]=v
   host[0x5c22]=counter;host.requests=[]
   req,_=cuts.source_tick(src);c=acall(host,'RdaAudioTick');assert req==host.requests
   actual=[host[s['RdaState']+0x82]if i==2 else host[0x5c20+i]for i in range(6)]
   assert actual==list(src[0x680:0x686]) and host[0x5c22]==counter
   assert (c.a,c.x,c.y,c.p&0xcf)==(0x36,0x57,0x98,0x61&0xcf)
   cases.append(dict(mode=mode,input=image,live06C4=counter,actual_after=actual,CPU=c.processorCycles))
  # The old setter cannot treat counter as a cue. Init owns its explicit reset.
  h=audio.Host(b['raw'],s);acall(h,'RdaAudioInit');h[0x5c22]=0x3c
  acall(h,'RdaAudioSetQueue',a=0xa5,x=2);assert h[0x5c22]==0x3c and h[s['RdaState']+0x82]==0
  checks['phase0_actual_source_requests_pause_init_and_counter_isolation']=dict(cases=cases,SetQueue2_rejected=True,sourceRawData_unchanged=True)

  # Actual complete IdleLoop->Main->sourceControl->C94 callback->A95->A62.
  # Native audio hook intentionally remains old; this proves foreground calls,
  # not authentic integrated NMI cadence or future scheduler behavior.
  mainrows=[]
  for mode,keys,health in itertools.product([0,1],[0,1,128],[(0x69,1),(0x70,1)]):
   m=w.life.make(b,mode);put(m,DisableScreenFlag=0,RdHealthLo=health[0],RdHealthHi=health[1]);m[0x5c22]=0
   before=0;low_calls=0;health_calls=0
   for tick in range(48):
    if tick:w.life.wake(m)
    put(m,SavedJoypadBits=keys)
    # Instrument genuine executed callback entry, not mutable endFrame state.
    oldclass=m.__class__;entries=[]
    class Watch(oldclass):
     def __getitem__(self,k):
      if isinstance(k,int)and k==address(b,'RdaLowHealth')and self.banks[1]==62:entries.append((self[0x5c79],self[0x5c22],self[0x5c2e]))
      return super().__getitem__(k)
    m.__class__=Watch
    c,row=w.life.mainstep(m,first=True);m.__class__=oldclass;minimum=min(minimum,row['minimum_SP'])
    # Multiple instruction fetches may touch entry; de-duplicate identical
    # callback tuples here, while actual counter writes prove true calls.
    counter_writes=[v for at,v in m.writes if at==0x5c22]
    if health[0]==0x69:
     for service,value,clock in dict.fromkeys(entries):
      if service==8:assert clock&15==0;low_calls+=1
      elif service==7:health_calls+=1
     before=(before-len(counter_writes))&255
     assert m[0x5c22]==before,(mode,keys,tick,counter_writes,m[0x5c22],before)
    else:assert m[0x5c22]==0
   if health[0]==0x69:assert low_calls>=2 and health_calls>=40
   mainrows.append(dict(mode=mode,pad=keys,source_health=list(health),Mains=48,actual_low_callbacks=low_calls,actual_health_callbacks=health_calls,final_counter=m[0x5c22],minimum_SP=minimum))
  checks['complete_Main_actual_source_callbacks']=mainrows

  # Genuine mapper IRQ and lagNMI at new callback paths. Other-owner dispatch
  # must still reject BEFORE any overlay read/write, including new counter.
  seamrows=[]
  for service in[7,8]:
   for name,bank in[('RdCueHealthGate',95),('RdaLowHealth',62)]:
    for kind in['IRQ','lagNMI']:
     m=w.life.make(b);put(m,RdHostService=service,RdHealthLo=0x69,RdHealthHi=1);m[0x5c22]=60
     c,l,tr=w.call(m,'RdHostDispatch',a=0,x=13,y=87,p=0x71,seam=(address(b,name),bank,kind));minimum=min(minimum,l)
     assert m[0x5c22]==(59 if service==8 else 60)
     seamrows.append(dict(service=service,PC=hex(address(b,name)),bank=bank,interrupt=kind,minimum_SP=l))
  foreign=[]
  owned=set(range(0x5c00,0x5c80))|set(range(0x5fb0,0x5fb8))
  for char,var in itertools.product([0,1,2,3,20,21,23,24,25,255],[0,1,2,255]):
   if(char,var)==(2,1):continue
   m=w.life.make(b);put(m,SelectedCharacter=char,RdVariant=var);m.reads.clear();m.writes.clear()
   c,l,tr=w.call(m,'RdHostDispatch',a=0x5a,x=4,y=0xe0,p=0x71)
   assert not m.reads&owned and not any(at in owned for at,v in m.writes),(char,var)
   foreign.append([char,var])
  checks['actual_IRQ_lagNMI_and_foreign_owner']=dict(seams=seamrows,foreign_dispatch_cases=len(foreign),foreign_no_overlay_access=True)
  proof.update(passed=True,minimum_SP=minimum,bindings=[ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',ref.ROM,R/'tools/rogue_dawn_live_cue_semantics_v1.py',R/'tools/rogue_dawn_audio_driver_controls_v4.py',R/'tools/rogue_dawn_host_ui_controls_v1.py']],limitations=build['open'])
 except Exception as e:
  proof['error']=repr(e);proof['traceback']=traceback.format_exc()
  target=O/'first-controls-negative.json'
  if target.exists():target=O/'next-controls-negative.json'
  target.write_text(json.dumps(proof,indent=2)+'\n')
  raise
 (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,ROM=build['ROM']['sha256'],minimum_SP=minimum,source_callback_cases=2560,actual_Main_calls=576,actual_audio_ticks=120,ISR_seams=len(seamrows))))

if __name__=='__main__':main()
