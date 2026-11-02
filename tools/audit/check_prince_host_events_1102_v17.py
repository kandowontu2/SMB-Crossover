"""Original audio continuations versus quiet host event leaves; no APU claim."""
from collections import Counter
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_host_lifecycle_model_1102_v12 as C
import check_prince_host_services_1102_v16 as S
P,O,W=C.P,C.O,C.W;N=W.N


class ActualAudio(C.World):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.lab.update(P.T.labels(O/'host-render-v11.lbl'))
 def callback(self,c,n,bank,pc):
  if n not in ['PpNativeSfx','PpNativeMusic']:return super().callback(c,n,bank,pc)
  self.calls[n]+=1;d=P.machine();d.memory.switch(bank if pc<0xc000 else self.s[0x6d1]);list.__setitem__(d.memory,slice(0,2048),self.s[:2048])
  result=P.call(d,pc,a=c.a,x=c.x,y=c.y,p=c.p,limit=100000)
  # Donor stack is discarded. The host source's dead OAM/stack span contains
  # executable code and never receives audio's original hardware-stack bytes.
  self.s[:256]=d.memory[:256];self.s[512:2048]=d.memory[512:2048]
  c.a,c.x,c.y,c.p=result[:4]


def quiet(b):
 h=C.World(b);h.lab.update(P.T.labels(O/'host-render-v11.lbl'));lab=P.T.labels(O/'host-services-v17.lbl');h.lab.update(lab);blob=(O/'host-services-v17.bin').read_bytes();h.s[0x1b9a:0x1b9a+len(blob)]=blob
 names={'PpNativeSfx':'PpNativeQuietSfx','PpNativeMusic':'PpNativeQuietMusic',**{n:'PpNativeUnpublishedMaterial'for n in ['PpNativeEndScene','PpSourceTrapContact','PpSourceHazardContact','PpSourceSwordPickup','PpSourcePotionContact']}}
 for at,v in h.recovery['instructions'].items():
  if v['mn']not in ['JSR','JMP']:continue
  bank,pc=at.split(':');dest=h.lab[f'PpN_{bank}_{pc}'];old=h.m[dest+1]|h.m[dest+2]<<8;name=h.callbacks.get(old,(None,))[0]
  if name in names:
   target=lab[names[name]];h.m[dest+1]=target&255;h.m[dest+2]=target>>8
 h.callbacks={a:v for a,v in h.callbacks.items()if v[0]not in names}
 return h


def equal(a,b,context):
 # Audio-only RAM has no legal actor reader. The private41 byte is a mapper
 # and interpreter save temporary: each of its two actor reads is preceded
 # by its own STY41 in the same original command (84BD->84D9,84DC->84F8).
 ignored={0,1,6,0x41,*range(0xad,0xb0),*range(0x780,0x800)}
 differences=[(hex(i),a.s[i],b.s[i])for i in range(0x800)if i not in ignored and a.s[i]!=b.s[i]]
 assert not differences,(context,differences[:16])


def main():
 b=W.scoped_load(C.BASE);cases=0;events=Counter();source=json.loads((O/'contact-recovery.json').read_text())['instructions']
 assert[(k,v['mn'])for k,v in source.items()if v['mode']in ['abs','zpg']and v['value']==0x41 and v['mn']in ['LDA','LDY','LDX']]==[('5:84D9','LDY'),('5:84F8','LDY')]
 assert not any(v['mn']in ['STA','STX','STY','INC','DEC']and v['mode']=='abs'and v['value']==0x735 for v in source.values())
 music=0
 for value in range(256):
  h=quiet(b);d=P.machine();d.memory.switch(6);list.__setitem__(d.memory,slice(0,2048),h.s[:2048]);args=dict(a=value,x=17,y=91,p=0x61)
  old=P.call(d,0xaa19,**args,limit=100000)
  m=h.m;root=h.lab['PpNativeQuietMusic'];c=N.NesMPU(memory=m,pc=root);c.a,c.x,c.y,c.p=value,17,91,0x61;c.sp=224;c.stPushWord(0x5aff)
  for _ in range(1000):
   if c.pc==0x5b00:break
   c.step()
  else:raise AssertionError(('Quiet music bound',value))
  assert old[:3]==(c.a,c.x,c.y)and old[3]&0xcf==c.p&0xcf,(value,old,(c.a,c.x,c.y,c.p));music+=1
 for face in [0,255]:
  for action in range(1,94):
   real=ActualAudio(b);q=quiet(b)
   for h in [real,q]:
    h.s[0x615]=face;h.lab['TestSet']=0xdd20;at=h.lab['PpSetAction'];h.s[0x1d20:0x1d27]=bytes([0xa9,action,0xa0,0,0x4c,at&255,at>>8]);h.source('TestSet')
   equal(real,q,('set',face,action));seen=set()
   for tick in range(512):
    ptr=real.s[0x613]|real.s[0x614]<<8
    if ptr in seen:break
    seen.add(ptr)
    for h in [real,q]:h.source('PpAdvanceActor');h.source('PpHostProject')
    equal(real,q,('advance',face,action,tick));cases+=1
    if real.s[0x60e]==255:break
   else:raise AssertionError(('Action cycle bound',face,action))
   events.update(real.calls)
 # Actual world/phase continuations include the two terrain SFX callers.
 world=[]
 for height in [0,16,32,48,64]:
  real=ActualAudio(b);q=quiet(b)
  for h in [real,q]:h.terrain(lambda x,y:0x54 if y>=208 or(height and 192<=x<224 and y>=208-height)else 0)
  stage='approach';age=0
  for tick in range(560):
   pad=1
   if height:
    if stage=='approach'and real.x()>=152:stage='wait';age=0
    if stage=='wait':
     pad=0
     if real.s[0x617]==15 and real.s[0x618]==0:stage='launch';age=0
    if stage=='launch':
     pad=8 if age<64 or real.s[0x618]in [2,6]else 0xc9;age+=1
   if real.x()>232:pad=1
   for h in [real,q]:N.put(h.m,SavedJoypad1Bits=pad);h.source('PpHostUpdate')
   equal(real,q,('world',height,tick));cases+=1
   if real.x()>328:break
  events.update(real.calls);world.append(dict(pipe_height=height,updates=tick+1,X=real.x(),source_audio_calls=dict(real.calls)))
 # Every native transport sample retains speed sign, parser bound and facing.
 h=quiet(b);samples=0
 for delta in range(256):
  for face in [0,255]:
   N.put(h.m,Player_X_Scroll=delta);h.s[0x615]=face;oldx=bytes(h.s[0x60f:0x611]);h.source('PpNativeMotionExport');signed=delta if delta<128 else delta-256;want=max(-5,min(5,signed))&255
   assert N.get(h.m,'Player_X_Scroll')==want and N.get(h.m,'Player_X_Speed')==(want<<4)&255 and N.get(h.m,'PlayerFacingDir')==(1 if face else 2)
   assert bytes(h.s[0x60f:0x611])==oldx;samples+=1
 q=dict(passed=True,base_ROM_SHA256=C.PIN,original_donor_SHA256=P.SHA,source_CPU_only=True,native_emulator=False,host_ROM_created=False,quiet_audio_WIP=True,original_audio_compared_at_actual_callers=True,original_music_AXYP_cases=music,full_actor_live_state_continuations=cases,actions=93,facings=2,actual_donor_audio_calls=dict(events),world_continuations=world,bounded_motion_transport_cases=samples,source_X_and_motion_unchanged=True,unpublished_material_callbacks=dict(material_domain=[0,1,20],original_entry_materials=dict(trap=18,hazard=10,sword=22,potion=2),demo0735_initialized_zero=True,no_direct_source_demo_writer=True),ignored_audio_only_state=['00/01/06 audio pointer/scratch, no recovered actor reader','0780..07FF audio-only, HP indexed instruction requires genuine player/enemy HP index0/1','41 mapper/interpreter save temporary overwritten before both reads','C0AD..AF owned event records'],scope='Quiet event bookkeeping only: no original audio playback claim. All93 original action programs and controller-driven pipe continuations compare complete actor-live RAM against actual original ROM audio. Callback material guards and normal-player demo-zero invariant close the five unpublished source material/scene leaves. Native owner/loader/combat/Main/emulator qualification remain separate.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),R/'tools/reference/prince_host_events_1102_v17.s',O/'host-services-v17.bin',O/'host-services-layout-v17.json',O/'contact-recovery.json',O/'host-life-v12.bin',C.BASE]})
 (O/'host-events-CPU-v17.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','world_continuations']}))


if __name__=='__main__':main()
