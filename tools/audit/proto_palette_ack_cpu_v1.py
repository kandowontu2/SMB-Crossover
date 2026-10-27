"""Finite actual-source CPU controls for sparse Proto palette cache acknowledgement."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P=R/'build/bass_corner_current.nes';N=R/'build/proto_palette_ack.nes'
def palette(writes):
 a=0;high=True;step=1;pixels={};bus=[]
 for at,v in writes:
  if at==0x2000:step=32 if v&4 else 1
  elif at==0x2006:
   if high:a=v<<8
   else:a=(a&0xff00)|v
   high=not high
  elif at==0x2007:
   bus.append((a,v));key=a&0x3fff
   if key>=0x3f00:
    key=0x3f00+(key&31)
    if key in [0x3f10,0x3f14,0x3f18,0x3f1c]:key-=16
   pixels[key]=v;a=(a+step)&0x3fff
 return pixels,bus
def prefix(q,n):
 q.set('VRAM_Buffer1_Offset',n)
 for i in range(256):q.set('VRAM_Buffer1',0,i)
 at=0
 while n-at>=4:
  size=min(63,n-at-3);q.array('VRAM_Buffer1',[0x20,at,size]+[0x15]*size)if at==0 else None
  for j,v in enumerate([0x20,at,size]+[0x15]*size):q.set('VRAM_Buffer1',v,at+j)
  at+=3+size
 return at==n
def arena(b,state):
 q=Arena(b,state.get('SelectedCharacter',1),proto=state.get('ProtoVariant',1));q.put(OperMode_Task=3,PlayerStatus=0,AreaType=1,GameEngineSubroutine=0,CurrentPlayer=0,SsLastPalette=0,MmLastPalette=0)
 q.put(**{k:v for k,v in state.items()if k!='offset'});prefix(q,state.get('offset',0));return q
def view(q):return tuple(q.m[:0x8000])
def main():
 old,new=scoped_load(P),scoped_load(N);rows=[]
 assert sha(P)=='8487c439ded9bc6274e1dc8f8e051494fa96ee518553d9c2f382eccf2e71d0e6'
 assert sha(N)=='2082c19a7364920f828e97f70040d37f1f7059bde1ea136b5c2c4532324abf36'
 oldlbl={w[2]:w[1]for l in P.with_suffix('.lbl').read_text().splitlines()if len(w:=l.split())==3};newlbl={w[2]:w[1]for l in N.with_suffix('.lbl').read_text().splitlines()if len(w:=l.split())==3};assert all(newlbl.get(k)==v for k,v in oldlbl.items()),'All old public labels preserved'
 tests=[dict(offset=o,PlayerStatus=p,SsLastPalette=cache)for o,p,cache in itertools.product([0,20,64,65,83,238,250,255],[0,1],[0,1,5])]
 for k,v in [('StarInvincibleTimer',1),('GuestPowerupActive',1),('MmChargeFrames',1),('MmChargeFrames',33),('MmChargeFrames',87),('InvSelected',1),('PlayerStatus',2),('ProtoVariant',0)]:
  for o in [0,20,64]:
   state=dict(offset=o);state[k]=v;tests.append(state)
 # InvSelected is a12+-element array, source guard specifically owner1.
 for state in tests:
  qs=[];cs=[]
  for b in [old,new]:
   q=arena(b,{k:v for k,v in state.items()if k!='InvSelected'})
   if'InvSelected'in state:q.set('InvSelected',state['InvSelected'],1)
   c,_=q.invoke('X5GetPlayerColors',a=0x67,x=0x89,y=0xab);qs.append(q);cs.append(c)
  a,b=qs;ca,cb=cs;assert(ca.a,ca.x,ca.y,ca.p,ca.sp,a.m.banks)==(cb.a,cb.x,cb.y,cb.p,cb.sp,b.m.banks),('Caller ABI',state)
  delta=[i for i,(x,y)in enumerate(zip(view(a),view(b)))if x!=y and not 0x100<=i<0x200]
  assert set(delta)<= {address(old,'SsLastPalette')},('Unexpected full caller RAM delta',state,delta)
  eligible=not state.get('StarInvincibleTimer',0)and not state.get('GuestPowerupActive',0)and not state.get('MmChargeFrames',0)and not state.get('InvSelected',0)and state.get('PlayerStatus',0)<2 and state.get('ProtoVariant',1)!=0 and state.get('offset',0)<=64
  assert b.get('SsLastPalette')==(1 if eligible else a.get('SsLastPalette')),('Ack condition',state)
  rows.append(dict(state=state,ack=eligible,old_cycles=ca.processorCycles,new_cycles=cb.processorCycles))
 # Foreign route bytes are identical and these finite actual calls also retain
 # every RAM/register/flag/mapper result, not just final palette colors.
 foreign=[]
 for ch,proto in [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(9,0),(12,0)]:
  qs=[];cs=[]
  for b in [old,new]:
   q=arena(b,dict(SelectedCharacter=ch,ProtoVariant=proto));c,_=q.invoke('X5GetPlayerColors');qs.append(q);cs.append(c)
  assert view(qs[0])==view(qs[1]) and qs[0].m.banks==qs[1].m.banks and(cs[0].a,cs[0].x,cs[0].y,cs[0].p,cs[0].sp,cs[0].processorCycles)==(cs[1].a,cs[1].x,cs[1].y,cs[1].p,cs[1].sp,cs[1].processorCycles)
  foreign.append([ch,proto,cs[0].processorCycles])
 # Reconstruct source entrance->graphics->firstactive palette calls and the
 # exact recorded timer command. No native timing/adoption claim.
 routes=[]
 for bundle in [old,new]:
  q=arena(bundle,{});q.invoke('X5GetPlayerColors');q.invoke('MegaManPaletteState');q.invoke('ProtoFixQueuedPalette');entrance=q.get('VRAM_Buffer1_Offset')
  q.put(GameEngineSubroutine=8);q.invoke('SpecialPalette');q.invoke('MegaManPaletteState');q.invoke('ProtoFixQueuedPalette');end=q.get('VRAM_Buffer1_Offset')
  timer=bytes.fromhex('207a03040000');q.array('NmiR0',[address(bundle,'VRAM_Buffer1')&255,address(bundle,'VRAM_Buffer1')>>8])
  for i,v in enumerate(timer+b'\x00'):q.set('VRAM_Buffer1',v,end+i)
  q.set('VRAM_Buffer1_Offset',end+6);raw=bytes(q.get('VRAM_Buffer1',i)for i in range(end+7));q.m.page(2,(location(bundle,'FastNmiVramCopy')-16)//8192);c,_=q.invoke('UpdateScreen');pixels,bus=palette(q.m.writes)
  routes.append(dict(entrance_bytes=entrance,queued_bytes=end+6,queue_hex=raw.hex(),UpdateScreen_body_cycles=c.processorCycles-6,ppu_bus=bus,palette_image=pixels))
 assert routes[0]['queue_hex']=='3f1d030f37173f19031630273f1004220f16103f11030f16103f1d030f37173f19031630273f1004220f16103f11030f1610207a0304000000',routes[0]
 assert routes[0]['palette_image']==routes[1]['palette_image'] and routes[0]['UpdateScreen_body_cycles']-routes[1]['UpdateScreen_body_cycles']==624
 assert routes[0]['queued_bytes']==56 and routes[1]['queued_bytes']==31
 proof=dict(passed=True,source_CPU_only=True,native_run=False,baseline_sha256=sha(P),candidate_sha256=sha(N),all_old_public_labels=len(oldlbl),actual_GetColors_caller_cases=len(rows),caller_state_contract='FullAXYP/SP, mapper state and every nonstack RAM byte identical except intentional normal-palette SsLastPalette acknowledgement. Added helper leaves dead stack residue; no live stack or caller state claim is masked.',queue_capacity='VRAM_Buffer1 actualDBG sizeof84; sourceLegacyGetColors appends6+6+7=19. Safe final offset19..83 means originaloffset0..64; wrap cases cannot enter that range. Header/colors/terminator verified before acknowledgment.',cases=rows,foreign_actual_calls=foreign,actual_source_route=routes,recorded_native_attribution=dict(NMI_entry=8663764,render_enable=8666344,elapsed=2580,Gateway=1478,CHR=429,DMA_request_elapsed=2059,actual29writes=True,audio_after_enable=True),projected_recovery=dict(UpdateScreen_cycles_saved=624,PPUDATA_old=len(routes[0]['ppu_bus']),PPUDATA_new=len(routes[1]['ppu_bus']),native_remeasurement_required=True),limitations='Finite component/queue/caller controls, not a new fullNMI/IRQ hardware run. Star/transform/charge and foreign paths retained. No installed source/build writes. No all-level performance claim.')
 out=R/'build/proto_palette_ack_controls.json';out.write_text(json.dumps(proof,indent=2)+'\n',newline='\n');print(json.dumps({'passed':True,'output':str(out),'sha256':sha(out),'cases':len(rows),'foreign':len(foreign),'saved':624}))
if __name__=='__main__':main()
