"""Supplement RCR composed proof with explicitly active task3 full callers."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from river_city_pipe_contact_controls_v2 import fixture,position,tile,pipe,state
from sunny_integrated_controls_v1 import run,registers,app,cleanwrites
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def world(q):return q.get('Player_X_Position')+256*q.get('Player_PageLoc')
def main():
 rom=R/'build/roster-shared-rcr-adopted-v8.nes';assert sha(rom)=='4cbd019100ba4dfc51fd9f71c5d3cabd844828eb7d5d2a4aa39413e3579ab39a'
 old=R/'build/river-city-native-v2.nes';bundles=[scoped_load(p)for p in [old,rom]];rows=[];cost=[]
 for variant,mode,face,kind,action in itertools.product((0,1),(0,1),(1,2),('open','side','ceiling','floor'),(0,128,64,4)):
  pair=[]
  for b in bundles:
   q=fixture(b,variant,mode);pipe(q,736)
   if kind=='side':x,y,vy=(721 if face==1 else 769),142,4
   elif kind=='ceiling':x,y,vy=448,174,-7
   elif kind=='floor':x,y,vy=448,174,4
   else:x,y,vy=448,96,4
   if kind in ('ceiling','floor'):
    for xx in range(400,512,16):tile(q,xx,160 if kind=='ceiling'else 208,0xc4 if kind=='ceiling'else 0x61)
   position(q,x,y,vy,face)
   bits=face|action
   q.put(OperMode_Task=3,PlayerEntranceCtrl=2,GameTimerDisplay=4,RcHudDirty=0,
     SavedJoypadBits=bits,Left_Right_Buttons=face,A_B_Buttons=bits&192,
     Player_Rel_XPos=96,Player_Rel_YPos=y,ScreenRight_PageLoc=x//256,ScreenRight_X_Pos=255)
   c,w,_=run(q,'GameLoop',p=0x71)
   assert q.get('RcClock')==1,'Real owned movement tick must execute'
   pair.append(dict(regs=registers(c),RAM=app(q),banks=q.m.banks,cycles=c.processorCycles,state=state(q),X=world(q)))
  current=pair[1]
  assert abs(current['X']-x)<=5,(kind,face,x,current['X'])
  if kind=='floor':assert current['state']['Player_Y_Position']==176 and current['state']['Player_State']==0,current
  if kind=='ceiling':assert 0<=current['state']['Player_Y_Speed']<128,current
  if kind=='side':
   assert current['X']<=722 if face==1 else current['X']>=766,current
   assert current['state']['Player_State']!=0,current
  exact=all(pair[0][k]==pair[1][k]for k in ('regs','RAM','banks'))
  if kind in ('open','floor'):assert exact,(kind,variant,mode,face,action)
  cost.append(pair[1]['cycles']-pair[0]['cycles'])
  rows.append(dict(variant=variant,mode=mode,face=face,arena=kind,input=bits,owned_movement_ticks=1,
    original_X=pair[0]['X'],current_X=current['X'],current_state=current['state'],full_state_exact=exact,
    CPU_delta=cost[-1]))
 out=R/'build/river-city-active-callers-v9.json';assert not out.exists()
 out.write_text(json.dumps(dict(passed=True,native_run=False,ROM_sha256=sha(rom),rows=rows,CPU_delta=[min(cost),max(cost)],
  correction='Prior composedv8 owned256 GameLoop arenas used OperMode_Task0 InitializeArea; valid full calls but not active movement. The86foreign seed() calls were already actualtask3. Preserve old proof; supersede owned-active coverage with these128 explicittask3 calls and assertRcClock increments. Prior floor arena at448 lacked ground becausepipe() onlypainted608..864; actual208floor is now explicit.',
  limits=['Typed active source arenas, not native FPS/audio/all-actor encounters','Contact corrections may intentionally differ from retained legacyclampbug'],
  bindings=[dict(path=str(p),sha256=sha(p))for p in [Path(__file__),rom,rom.with_suffix('.dbg'),old,R/'tools/river_city_composed_controls_v8.py']]),indent=2)+'\n')
 print(json.dumps(dict(passed=True,active_GameLoops=len(rows),CPU=[min(cost),max(cost)])))
if __name__=='__main__':main()
