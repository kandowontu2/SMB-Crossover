"""Retain a finite ordinary-input traversal witness on frozen9529; no ROM edits."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_current64_host_checks_v1 as A
from check_tmnt_render_oa import load,address
H=A.H;N=A.N;J=R/'build/bowser-playable-jump-v1/joint';O=R/'build/bowser-playable-route-analysis-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 O.mkdir(exist_ok=False);q=dict(source_CPU=True,native=False,ROM_edited=False,route_clear=False,rows=[],pipes=[])
 try:
  b=load(J/'candidate.nes');m=A.boot(b,8);lastx=-1;still=0;hold=0;lastA=False;seen=set()
  def get(n):return H.get(m,n)
  def block(wx,y):
   if y<32 or y>=240:return 0
   return m[address(b,'Block_Buffer_1')+(wx//256%2)*208+((y-32)//16)*16+(wx%256)//16]
  for age in range(5000):
   x=get('Player_X_Position')+256*get('Player_PageLoc');y=get('Player_Y_Position');ground=get('Player_State')==0
   still=still+1 if x==lastx else 0;lastx=x
   camera=get('ScreenLeft_X_Pos')+256*get('ScreenLeft_PageLoc')
   pipe=None
   for wx in range((x//16)*16,min(camera+256,x+112),16):
    tops=[yy for yy in range(32,208,16)if block(wx,yy)in[16,17,18,19,20,21]]
    if tops:
     top=min(tops)
     if wx>=x+8 and pipe is None:pipe=[wx,top,208-top]
     if(wx,top)not in seen:
      seen.add((wx,top));q['pipes'].append(dict(age=age,x=wx,top=top,height=208-top,tile=block(wx,top)))
   # Ordinary held A survives a real source edge; no velocity/position writes.
   if hold>0:hold-=1;pressed=True
   else:
    pressed=False
    if ground and not lastA and pipe and pipe[0]-x<52:hold=7;pressed=True
    if ground and not lastA and still>15:hold=7;pressed=True
    ahead=block(x+24,min(232,y+40))
    if ground and not lastA and ahead in[0,35,38,194,195]:hold=7;pressed=True
    for slot in range(6):
     if m[address(b,'Enemy_Flag')+slot]==1 and m[address(b,'Enemy_ID')+slot]<21 and m[address(b,'Enemy_State')+slot]<32:
      ex=m[address(b,'Enemy_X_Position')+slot]+256*m[address(b,'Enemy_PageLoc')+slot]
      if ground and not lastA and 0<ex-x<72:hold=7;pressed=True
   keys=1|(128 if pressed else 0)|(64 if age%32==0 else 0);lastA=pressed
   H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=1,Up_Down_Buttons=0,NmiDisable=255)
   r=N.invoke(m,'GameLoop');normal=N.C.A.consume(m)
   q['rows'].append(dict(age=age,input=keys,x=x,y=y,state=get('Player_State'),vx=get('Player_X_Speed'),vy=get('Player_Y_Speed'),camera=camera,HP=m.ram[3][0x1e29],injury_timer=get('InjuryTimer'),engine=get('GameEngineSubroutine'),near_pipe=pipe,Main_CPU=r['CPU']))
   if get('MmDeathFlag')or get('GameEngineSubroutine')in[6,11]:q['endpoint']='native death';break
   if still>=240:q['endpoint']='240 consecutive Main at same X';break
   if get('WorldNumber')!=0 or get('LevelNumber')!=0:q.update(endpoint='real next area',route_clear=True);break
  else:q['endpoint']='5000 Main finite bound'
  q['completed_Main']=len(q['rows']);q['max_X']=max(r['x']for r in q['rows']);q['min_Y']=min(r['y']for r in q['rows'])
  q['analysis_complete']=True
 except Exception as e:q.update(analysis_complete=False,error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),Path(N.__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin']}
 (O/'analysis.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','pipes','bindings']}));assert q['analysis_complete']
if __name__=='__main__':main()
