"""Current Mac mixed request/restart/retirement and DMC supplement.

Earlier bound proposal sources/receipts remain immutable. Reexecute their
playback test with additional bus assertions, then qualify actual ingress.
"""
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
import hashlib,json
import audit_prince_pool_1102_v1 as A
import check_hogan_current_bounded_v1 as M
R,O=A.R,A.O
ROM=R/'build/excitebike-pose-1101-v3/current4.nes'
SHA='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def main():
 assert A.sha(ROM)==SHA;b=A.scoped_load(ROM);seed=M.fresh(b)
 decl=json.loads((O/'resident-padding-proposal.json').read_text())
 at=A.location(b,'LmNativeBankStart')
 assert hashlib.sha256(b['raw'][at:at+8192]).hexdigest()==decl['whole_source_bank_exact']['sha256']
 ranges=[tuple(v['CPU_half_open'])for v in decl['declared_pads']]
 buscounts=Counter();maps=set();closed={}
 class CheckedBus(M.Bus):
  def __getitem__(self,i):
   if isinstance(i,int)and getattr(self,'monitor',False)and 0x8000<=i<=65535:
    bank=self.rawtags[(i-0x8000)//8192]&127
    if bank==123:
     physical=0xa000+(i&8191)
     assert not any(lo<=physical<hi for lo,hi in ranges),('Source code/data consumes pad',hex(i),hex(physical))
   return super().__getitem__(i)
  def __setitem__(self,i,v):
   if isinstance(i,int)and getattr(self,'monitor',False):
    if i in [0x4012,0x4013]:raise AssertionError(('Mac source attempted DMC address/length store',hex(i),v))
    if i==0x4015:
     assert not v&16,('Mac source started source DMC',v)
     buscounts['hardware_status_stores_no_DMC']+=1
    if i in [0x5116,0x5117]:
     assert (v&127)!=123,('Source audio maps123 into DMC-visibleC/E',hex(i),v)
     maps.add((i,v));buscounts['C_E_mapper_stores_no123']+=1
   return super().__setitem__(i,v)
 # The exact old source recipe runs in memory with only added observation,
 # bounded-log clearing and a distinct output filename. No old result changes.
 p=R/'tools/audit/check_prince_mac_padding_consumers_1102_v1.py';source=p.read_text()
 changes={
  'class Reads(M.Bus):':'class Reads(CheckedBus):',
  "assert decl['passed']and decl['ROM_SHA256']==A.SHA":"assert decl['passed'];assert hashlib.sha256(b['raw'][A.location(b,'LmNativeBankStart'):A.location(b,'LmNativeBankStart')+8192]).hexdigest()==decl['whole_source_bank_exact']['sha256']",
  "r=M.invoke(m,'LmNativeMusicPlay');cycles+=r['CPU'];minimum=min(minimum,r['minimum_SP'])":"m.writes.clear();m.ram_writes.clear();r=M.invoke(m,'LmNativeMusicPlay');assert all(m[zp+i]==0 for i in [0,1,3,5,7]);cycles+=r['CPU'];minimum=min(minimum,r['minimum_SP'])",
  "rows.append(dict(song=song":"CLOSED[song]=M.fork(m)\n  rows.append(dict(song=song",
  "(O/'resident-pad-consumers.json')":"(O/'resident-pad-consumers-v2.json')",
 }
 for old,new in changes.items():assert old in source,old;source=source.replace(old,new)
 proxy=SimpleNamespace(**{n:getattr(A,n)for n in ['R','O','sha','scoped_load','address','location']},ROM=ROM,SHA=SHA)
 env=dict(__file__=str(p),__name__='mac_pad_ingress_supplement',CheckedBus=CheckedBus,CLOSED=closed)
 # Replace only the import binding in the executed copy; source A stays frozen.
 source=source.replace('import audit_prince_pool_1102_v1 as A','A=PROXY');env['PROXY']=proxy
 exec(compile(source,str(p),'exec'),env)
 # Reconstruct exact already-qualified repeat boundaries at loop_start,
 # rather than rerunning tune23's124160-update period on every ingress edit.
 # The complete observed playback proof runs again after ingress checks pass.
 previous=json.loads((O/'resident-pad-consumers.json').read_text())
 assert previous['passed']and previous['ROM_SHA256']==A.SHA
 ram=A.address(b,'LmNativeRam');zp=A.address(b,'LmNativeZp')
 for row in previous['rows']:
  m=M.fork(seed);m.__class__=CheckedBus;m.monitor=True
  m[ram:ram+288]=bytes(288);m[zp:zp+16]=bytes(16);m[248]=m[249]=0
  M.put(m,SelectedCharacter=15,OperMode=1);M.invoke(m,'LmNativeSourceInit',a=row['song']-1)
  for _ in range(row['loop_start']):m.writes.clear();m.ram_writes.clear();M.invoke(m,'LmNativeMusicPlay')
  closed[row['song']]=m
 ram=A.address(b,'LmNativeRam');zp=A.address(b,'LmNativeZp')
 def fresh():
  m=M.fork(seed);m.__class__=CheckedBus;m.monitor=True
  return m
 def invoke(m,name):
  m.writes.clear();m.ram_writes.clear();return M.invoke(m,name)
 def state(m):return bytes(m[ram:ram+48])+bytes(m[zp:zp+16])
 def prepare(m,**kw):
  M.put(m,SelectedCharacter=15,OperMode=1,XgAudioCharacter=0,GamePauseStatus=0,AreaMusicQueue=0,EventMusicQueue=0,**kw)
 areas=[20,22,1,23,2,1,23];events=[7,9,6,4,9,6,23]
 def request(a,e):
  vals=e&127
  if vals:return events[(vals&-vals).bit_length()-1]
  vals=a&127
  return areas[(vals&-vals).bit_length()-1]if vals else 20
 masks=0
 for mode in [0,1]:
  for paused in [0,1]:
   for a,e in [(v,0)for v in range(256)]+[(1,v)for v in range(256)]:
    m=fresh();prepare(m);M.put(m,OperMode=mode,GamePauseStatus=paused,AreaMusicQueue=a,EventMusicQueue=e)
    before=state(m);invoke(m,'LmNativeMusicGate')
    assert M.get(m,'AreaMusicQueue')==M.get(m,'EventMusicQueue')==0
    silence=bool(((a|e)&128)and not((a|e)&127))
    muted=mode==0 or paused or silence
    if muted:assert state(m)==before,('Muted source changes',mode,paused,a,e,[(i,v,w)for i,(v,w)in enumerate(zip(before,state(m)))if v!=w])
    if mode==0:
     M.put(m,OperMode=1,GamePauseStatus=0);invoke(m,'LmNativeMusicGate');expected=20
    elif silence:
     M.put(m,GamePauseStatus=0,AreaMusicQueue=1);invoke(m,'LmNativeMusicGate');expected=20
    elif paused:
     M.put(m,GamePauseStatus=0);invoke(m,'LmNativeMusicGate');expected=request(a,e)
    else:expected=request(a,e)
    assert M.get(m,'RgAudioSong')==expected,(mode,paused,a,e,expected,M.get(m,'RgAudioSong'))
    assert m[zp+2]!=0 and m[zp+6]==0
    masks+=1
 # Every legal request pair, with real prior source control states, must reach
 # the same constructor image regardless of earlier song/pointer history.
 targets=[(1<<i,0)for i in range(7)]+[(0,1<<i)for i in range(7)]
 restarts=0
 for song,old in closed.items():
  for a,e in targets:
   pair=[]
   for m in [M.fork(old),fresh()]:
    m.__class__=CheckedBus;m.monitor=True
    M.put(m,SelectedCharacter=15,OperMode=1,GamePauseStatus=0,XgAudioCharacter=252,LmNativePending=0,RgAudioSilenced=0,AreaMusicQueue=a,EventMusicQueue=e)
    fg=bytes(m[248:250]);invoke(m,'LmNativeMusicGate');assert bytes(m[248:250])==fg
    pair.append((state(m),M.get(m,'RgAudioSong')))
   assert pair[0]==pair[1],('Actual restart source state differs',song,a,e)
   restarts+=1
 endings=0
 for song,old in closed.items():
  if old[zp+2]or old[zp+6]:continue
  for event in [0,1]:
   m=M.fork(old);m.__class__=CheckedBus;m.monitor=True
   M.put(m,SelectedCharacter=15,OperMode=1,GamePauseStatus=0,XgAudioCharacter=252,LmNativePending=0,RgAudioSilenced=0,AreaMusicQueue=0,EventMusicQueue=0,RgAudioSong=song,XgAudioEvent=event)
   before=state(m);clock=M.get(m,'XgAudioSong');invoke(m,'LmNativeMusicGate')
   if event:
    assert M.get(m,'XgAudioEvent')==2 and state(m)==before and M.get(m,'GuestNativeEnable')==0
   else:assert M.get(m,'XgAudioSong')==(clock+1)&255 and m[zp+2]!=0 and m[zp+6]==0
   endings+=1
 # Real character-change retirement, including an active foreign DMC receipt,
 # executes its existing stop/reset path before Mac is admitted again.
 retirement=0
 for raw in range(38):
  if raw==15:continue
  m=M.fork(closed[20]);m.__class__=CheckedBus;m.monitor=True
  M.put(m,SelectedCharacter=raw,GuestAudioCharacter=15,BassDmcActive=3,Cv3DmcPriority=5,GuestCombinedEnable=31)
  invoke(m,'GuestAudioBegin')
  assert M.get(m,'GuestAudioCharacter')==raw
  assert all(M.get(m,n)==0 for n in ['BassDmcActive','GuestNativeEnable','GuestCombinedEnable','GuestMixMask'])
  M.put(m,SelectedCharacter=15);invoke(m,'GuestAudioBegin')
  assert M.get(m,'GuestAudioCharacter')==15
  M.put(m,OperMode=1,GamePauseStatus=0,AreaMusicQueue=1,EventMusicQueue=0)
  invoke(m,'LmNativeMusicGate');assert M.get(m,'RgAudioSong')==20
  retirement+=1
 # Actual gate instructions establish the only physical123 entry. Foreign
 # legacy playback is outside this pad owner; do not replace it with a stub.
 gate=A.address(b,'LmNativeMusicGate');legacy=A.address(b,'LmNativeMusicLegacy')
 for raw in range(256):
  m=fresh();M.put(m,SelectedCharacter=raw)
  c=M.NesMPU(memory=m,pc=gate)
  for _ in range(3):c.step()
  assert c.pc==(gate+7 if raw==15 else legacy),(raw,hex(c.pc))
  if raw!=15:assert bytes(m[c.pc:c.pc+3])==bytes([0x4c,*A.address(b,'ExpandedAudioTick').to_bytes(2,'little')])
 env['main']()
 playback=json.loads((O/'resident-pad-consumers-v2.json').read_text())
 assert playback['rows']==previous['rows'],'Actual current source full-cycle state/cost/read trace changed across rebase'
 q=dict(passed=True,ROM_SHA256=SHA,source_CPU_only=True,resource_granted=False,all256area_and_event_mask_selection_cases=masks,mixed_all9prior_tracks_all14request_restarts=restarts,genuine_source_end_event_stop_and_whole_tune_restart_cases=endings,actual37foreign_owner_retirement_and_Mac_reentry_cases=retirement,actual_all256_gate_identity_cases=256,all_nine_source_track_playback_and_DMC_checked_again=True,no_source_DMC_address_length_or_start=True,no_actual_source_C_E_mapping_to123=True,actual_C_E_mapper_pairs=sorted(maps),bus_counts=dict(buscounts),scope='Original current Mac source, actual native owning gate, all queue masks in title/pause/gameplay, original song restart/end states and actual GuestAudioBegin/Cv3DmcResetOwner retirement. All source SFX request flags remain zero during every closed music track. No source DMC starts or address/length stores; source123 is never mapped into C000/E000 by these actual paths. DMC hardware fetch begins atC000, so A000-only123 is outside this source playback DMA domain. No new resident writes or gameplay/audio waveform claim.',bindings={str(p.relative_to(R)):A.sha(p)for p in[Path(__file__),ROM,R/'src/mac_native_music.s',R/'src/guest_audio.s',R/'src/collision.s',R/'src/cv3_dmc_owner.inc',O/'resident-pad-consumers-v2.json']})
 q['bindings'][str(p.relative_to(R))]=A.sha(p)
 q['bindings'][str((O/'resident-pad-consumers.json').relative_to(R))]=A.sha(O/'resident-pad-consumers.json')
 (O/'resident-pad-ingress-v2.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
