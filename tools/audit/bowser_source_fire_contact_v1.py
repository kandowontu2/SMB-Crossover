"""Controller-earned source breath reaches genuine native fire collision targets."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_actual_host_checks_v1 as A
import bowser_gameplay_component_controls_v2 as C
T=A.T;H=A.H;J=A.J;O=R/'build/bowser-source-fire-contact-v1'
from check_tmnt_render_oa import load,address

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,source_CPU=True,rows=[])
 try:
  b=load(J/'candidate.nes');seeds={f:A.boot(b,f)for f in[0,8]}
  for form,slot,kind in itertools.product([0,8],range(6),[2,6,45]):
   m=T.fork(seeds[form]);H.put(m,Player_X_Position=40,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,ObjectOffset=(slot+1)%6,BowserHitPoints=2,EnemyFrenzyBuffer=0)
   C.rc(m,'BwConstruct')
   for i in range(6):m[address(b,'Enemy_Flag')+i]=0
   for n,v in [('Enemy_Flag',1),('Enemy_ID',kind),('Enemy_State',0),('Enemy_X_Position',70),('Enemy_PageLoc',0),('Enemy_Y_Position',176),('Enemy_Y_HighPos',1)]:m[address(b,n)+slot]=v
   events=[];entry=address(b,'HandleEnemyFBallCol');emit=address(b,'BwSpawnFire')
   for tick in range(80):
    H.put(m,SavedJoypadBits=64 if tick==0 else 0,FrameCounter=tick)
    C.rc(m,'BwMovement');T.call(m,'PlayerBGCollision')
    c=H.start(m,'BwWeaponTail');c.a=3
    def watch(mem,c,i):
     if c.pc==entry and mem.rawtags[0]==254:events.append([tick,'native_hit',c.x,H.get(mem,'ObjectOffset')])
     if c.pc==emit and mem.rawtags[1]==3:events.append([tick,'source_emit'])
    H.finish(m,c,watch)
    if any(e[1]=='native_hit'for e in events):break
   assert [e[1]for e in events]==['source_emit','native_hit'],(form,slot,kind,events)
   assert H.get(m,'ObjectOffset')==(slot+1)%6
   if kind==2:assert m[address(b,'Enemy_State')+slot]==0 and H.get(m,'BowserHitPoints')==2
   elif kind==6:
    assert m[address(b,'Enemy_State')+slot]&32 and m[address(b,'FloateyNum_Control')+slot]==1
    assert H.get(m,'Square1SoundQueue')>0
   else:assert H.get(m,'BowserHitPoints')==1
   q['rows'].append(dict(form=form,slot=slot,kind=kind,events=events,state=m[address(b,'Enemy_State')+slot],native_boss_HP=H.get(m,'BowserHitPoints')))
  q.update(passed=True,limits='Legal stationary native actor fixture and actual source movement/native terrain/weapon-tail sequence; no native campaign combat claim')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest()for p in[Path(__file__),Path(A.__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),traceback=q.get('traceback'))));assert q['passed']
if __name__=='__main__':main()
