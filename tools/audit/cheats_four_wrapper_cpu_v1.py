"""Actual compiled wrapper/jump/wrap controls for private four-Cheats draft."""
from pathlib import Path
import sys,json,itertools,argparse,traceback,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();O=args.output;O.mkdir(exist_ok=False,parents=True)
def put(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n',newline='\n')
b=scoped_load(args.candidate);old=scoped_load(args.baseline)
variants={1:('ProtoVariant',2),3:('BillVariant',2),4:('Z2Variant',2),5:('Cv3Variant',4),9:('RlVariant',2),12:('DarkwingVariant',2),13:('KbVariant',2),14:('CdVariant',2),17:('M3Variant',2),18:('VvVariant',4),19:('TnVariant',4)}
def fresh(bundle,ch,mode,v):
 q=Arena(bundle,ch);q.put(OperMode_Task=3,CrossoverBehaviorVersion=mode,Player_State=0,SwimmingFlag=0,AreaType=1,PlayerStatus=1,PlayerSize=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_X_Position=96,Player_PageLoc=1,Player_CollisionBits=3,PlayerFacingDir=1,Player_MovingDir=1,Player_X_Speed=0,Player_XSpeedAbsolute=0,A_B_Buttons=0,PreviousA_B_Buttons=0,SavedJoypadBits=0,Left_Right_Buttons=0,Up_Down_Buttons=0,Player_Rel_XPos=96,Player_Pos_ForScroll=96,ScreenLeft_PageLoc=1,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=1,ScreenRight_X_Pos=255,ScrollLock=1,NmiDisable=255)
 for n,z in variants.values():q.set(n,0)
 if ch in variants:q.set(variants[ch][0],v)
 if ch in [0,8]:q.set('MarioSourceActive',1)
 for n in ['Block_Buffer_1','Block_Buffer_2']:
  for i in range(0xb0,0xd0):q.set(n,0x54,i)
 return q
def tick(q,bits=0,name='PlayerCtrlRoutine'):
 q.put(SavedJoypadBits=bits);c,e=q.invoke(name);q.set('PreviousA_B_Buttons',bits&192);q.set('FrameCounter',(q.get('FrameCounter')+1)&255)
 return c,e
def state(q):return dict(y=q.get('Player_Y_Position'),page=q.get('Player_Y_HighPos'),state=q.get('Player_State'),vy=q.get('Player_Y_Speed'),engine=q.get('GameEngineSubroutine'))
rows=[]
try:
 for ch in range(20):
  for mode,v in itertools.product([0,1],range(variants.get(ch,('',1))[1])):
   q=fresh(b,ch,mode,v)
   for i in range(12):tick(q)
   assert q.get('GameEngineSubroutine')==8,(ch,mode,v,state(q))
   q.put(Player_State=2,Player_Y_Position=160,Player_Y_HighPos=1,Player_Y_Speed=3,PreviousA_B_Buttons=0,SavedJoypadBits=128)
   q.invoke('CheatsAirJump');admit=q.get('Player_State');path=[]
   for i in range(4):tick(q,128);path.append(state(q))
   if ch!=18:
    assert admit==0,(ch,mode,v,admit)
    assert min(r['y']for r in path)<160,(ch,mode,v,path)
   else:assert admit==2
   rows.append(dict(char=ch,mode=mode,variant=v,admitted_state=admit,path=path))
 put('native-jump-admission.json',dict(passed=True,cases=rows,source_CPU_only=True,warm_native_wrapper_updates=12,actual_motion_wrapper='PlayerCtrlRoutine',limits='Finite legal dry empty arenas, four retained-A updates after new A; no physical controller/NMI/gameplay qualification.'))
 rows=[]
 for ch in range(20):
  for mode,v in itertools.product([0,1],range(variants.get(ch,('',1))[1])):
   for edge in ['bottom','top']:
    q=fresh(b,ch,mode,v)
    for i in range(12):tick(q)
    q.put(Player_State=2,Player_Y_Position=237 if edge=='bottom'else 16,Player_Y_HighPos=1,Player_Y_Speed=5 if edge=='bottom'else 251,SavedJoypadBits=4 if edge=='bottom'else 8)
    if ch==18:q.put(VvObjY=192 if edge=='bottom'else 16,PnY=192 if edge=='bottom'else 16)
    if ch==19 and edge=='top':q.set('Player_Y_Position',40)
    before=[q.get('Block_Buffer_1',i)for i in range(416)];q.invoke('CheatsWrapPlayer');wrapped=state(q)
    assert wrapped['page']==1 and 32<=wrapped['y']<=192,(ch,mode,v,edge,wrapped)
    expected=32 if edge=='bottom'else 176
    # Topsearch192 intersects floorrow208; the conservative32px volume chooses176.
    assert wrapped['y']==expected,(ch,mode,v,edge,wrapped)
    if ch==18:assert q.get('VvObjY')==expected-24 and q.get('PnY')==expected-24
    tick(q,q.get('SavedJoypadBits'));after=state(q)
    assert after['engine']==8 and after['page']==1 and 20<=after['y']<=220,(ch,mode,v,edge,wrapped,after)
    assert [q.get('Block_Buffer_1',i)for i in range(416)]==before
    rows.append(dict(char=ch,mode=mode,variant=v,edge=edge,wrapped=wrapped,after_real_wrapper=after))
 put('native-wrap-import-export.json',dict(passed=True,cases=rows,source_CPU_only=True,real_terrain_buffers=True,no_terrain_writes=True))
 # Both fullysolid buffers: no destination and no mutation/loop.
 rows=[]
 for edge in ['top','bottom']:
  q=fresh(b,0,0,0);q.put(Player_State=2,Player_Y_Position=16 if edge=='top'else 237,Player_Y_HighPos=1)
  for i in range(416):q.set('Block_Buffer_1',0x54,i)
  before=state(q);c,_=q.invoke('CheatsWrapPlayer');assert state(q)==before;rows.append(dict(edge=edge,cycles=c.processorCycles))
 put('wrap-no-destination.json',dict(passed=True,cases=rows))
 put('proof.json',dict(passed=True,ROM=hashlib.sha256(args.candidate.read_bytes()).hexdigest()))
 print(json.dumps({'passed':True}))
except Exception as e:
 put('failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),last_rows=rows[-3:]));raise
