"""Actual injury-status/ForceInjury source consumer and unchanged UI geometry."""
from pathlib import Path
import collections,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_current64_host_checks_v1 as A
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
H=A.H;T=A.T;N=A.N
P=R/'build/bowser-current64-v3/joint';J=R/'build/bowser-playable-jump-v1/joint'
O=R/'build/bowser-playable-contact-controls-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def call(m,name,**kw):
 names=['GuestInjuryStatus','RlInjuryStatusDispatch','BwStatus','RlInjuryDispatch','BwInjury','KillPlayer','BwDeathStart']
 points={(address(m.bundle,n),3 if n.startswith('Bw')else((location(m.bundle,n)-16)//8192)|128):n for n in names}
 events=[];c=H.start(m,name,**kw)
 def hook(mm,c,i):
  if c.pc>=0x8000:
   key=(c.pc,mm.rawtags[(c.pc-0x8000)//8192])
   if key in points:events.append(dict(step=i,name=points[key],A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,HP=mm.ram[3][0x1e29]))
 c,low=H.finish(m,c,hook);assert c.sp==224
 return dict(counts=dict(collections.Counter(e['name']for e in events)),events=events,minimum_SP=low,AXYP_SP=[c.a,c.x,c.y,c.p,c.sp])

def timer_frame(m):
 # Execute the actual unpaused GameLoop::DecTimers fragment to NoDecTimers.
 # The legal caller preconditions are explicit. No timer is assigned/zeroed.
 assert H.get(m,'TimerControl')==0 and not H.get(m,'GamePauseStatus')&1
 c=NesMPU(memory=m,pc=address(m.bundle,'DecTimers'));c.sp=224
 for i in range(1000):
  if c.pc==address(m.bundle,'NoDecTimers'):return
  c.step()
 raise AssertionError('literal native timer fragment bound')

def visible(m):return [list(m[i:i+4])for i in range(0x200,0x300,4)if m[i]<240]

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False,contacts=[],expiry=[],UI=[])
 try:
  old,new=load(P/'candidate.nes'),load(J/'candidate.nes');seeds={f:A.boot(new,f)for f in[0,8]}
  for form,flag in itertools.product([0,8],range(64)):
   m=T.fork(seeds[form]);H.put(m,InjuryTimer=0,ObjectOffset=0);hp=m.ram[3][0x1e29]
   r=call(m,'InjurePlayer',p=T.flags(flag))
   assert m.ram[3][0x1e29]==hp-1 and H.get(m,'InjuryTimer')==8
   assert r['counts'].get('BwStatus')==r['counts'].get('BwInjury')==1 and not r['counts'].get('KillPlayer')
   r2=call(m,'InjurePlayer',p=T.flags(flag));assert m.ram[3][0x1e29]==hp-1 and not r2['counts'].get('BwStatus')and not r2['counts'].get('BwInjury')
   q['contacts'].append(dict(form=form,flags=flag,HP_before=hp,HP_after=hp-1,first=r,protected=r2))
  for form in[0,8]:
   before=A.boot(old,form);r=call(before,'InjurePlayer');assert before.ram[3][0x1e29]==0 and r['counts'].get('KillPlayer')==1 and not r['counts'].get('BwInjury')
   m=T.fork(seeds[form]);hp=m.ram[3][0x1e29];rows=[]
   for hit in range(hp):
    assert H.get(m,'InjuryTimer')==0
    r=call(m,'InjurePlayer');assert m.ram[3][0x1e29]==hp-hit-1
    if hit<hp-1:
     assert not r['counts'].get('KillPlayer')and H.get(m,'GameEngineSubroutine')==8
     for age in range(2000):
      if not H.get(m,'InjuryTimer'):break
      prior=H.get(m,'InjuryTimer');phase=H.get(m,'IntervalTimerControl')
      timer_frame(m)
      assert H.get(m,'InjuryTimer')==prior-int(phase==0)
     else:raise AssertionError('native interval timer expiry bound')
     assert H.get(m,'InjuryTimer')==0
    else:assert r['counts'].get('KillPlayer')==1 and H.get(m,'GameEngineSubroutine')==11
    rows.append(dict(hit=hit+1,HP=m.ram[3][0x1e29],native_timer_frames=age if hit<hp-1 else 0,counts=r['counts']))
   q['expiry'].append(dict(form=form,hits=rows,old_first_contact=r if False else 'Old native ForceInjury skipped service5 and killed immediately; retained previous source trace.'))
  # Both real cold consumers: select positions remain exact; lives translate
  # every emitted body part down8 while restoring native PlayerY afterward.
  for form,mode in itertools.product([0,8],[0,1]):
   outcomes=[]
   for b in[old,new]:
    if mode==0:
     m=N.C.fresh(b,0);H.put(m,CrossoverMenuIndex=26,FmAlts=form,SelectedCharacter=0)
     for name in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:N.invoke(m,name)
    else:
     m=A.boot(b,form);H.put(m,OperMode=1,OperMode_Task=1,AltEntranceControl=0,DisableIntermediate=0,CurrentOAMOffset=0,VRAM_Buffer1_Offset=0)
     N.invoke(m,'DisplayIntermediate')
    outcomes.append(dict(OAM=visible(m),Y=H.get(m,'Player_Y_Position'),X=H.get(m,'Player_X_Position'),queue=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+H.get(m,'VRAM_Buffer1_Offset')+1]).hex()))
   x,y=outcomes;assert len(x['OAM'])==len(y['OAM'])==(7 if form else 11),(form,mode,outcomes)
   expected=[[a+(8 if mode else 0),t,p,xx]for a,t,p,xx in x['OAM']]
   assert y['OAM']==expected and(x['Y'],x['X'],x['queue'])==(y['Y'],y['X'],y['queue']),(form,mode,outcomes)
   q['UI'].append(dict(form=form,mode=mode,old=x,new=y))
  q.update(passed=True,native_status_flag_pairs=128,genuine_protected_recontacts=128,real_native_timer_expiry_frames=sum(h['native_timer_frames']for cohort in q['expiry']for h in cohort['hits']),
   native_timer_semantics='Normal native InjuryTimer8 intervals, approximately168 Main updates; the90-interval unit bug is fixed.',
   explicit_limits='Literal native unpaused timer fragment for repeated expiry; full natural contact/traversal is a separate wholeMain receipt. No native emulator/route clear claim.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),Path(N.__file__),P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['contacts','expiry','UI','bindings']}));assert q['passed']
if __name__=='__main__':main()
