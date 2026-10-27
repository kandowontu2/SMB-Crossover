"""Prepare one LanceHard descent escape; no emulator or game-source edits."""
from pathlib import Path
from types import SimpleNamespace
import csv,difflib,hashlib,json,re,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from current_roster_compact_11_v1 import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from luigi_mario_profile731_cpu_v1 import full,tick
from mario_luigi731_coefficients_v1 import seed_vx,coord
SHA='9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

HELPER="""local function lanceRetreatLane(c,e)
 local first,last=c.x-32,e.x+14
 if last<first or last-first>144 then return false end
 local function clear(x)
  for y=112,200,8 do if c.block(x,y)~=0 then return false end end
  local t=c.block(x,216)
  return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
 end
 for x=first,last,8 do if not clear(x)then return false end end
 if not clear(last)then return false end
 for i=0,5 do
  local f,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  if f>0 and f<128 and id<0x15 and st<0x20 and not(id==6 and st>=2)
   and c.r('Enemy_Y_HighPos',i)==1 and c.r('Enemy_Y_Position',i)>=160 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if x>=c.x-48 and x<=c.x then return false end
  end
 end
 return true
end
"""
BRANCH=""" -- LanceHard cannot stomp. Leave the descending contact lane before
 -- reaching the short enemy; neutral air input would retain source VX.
 if ROSTER_CONFIG.name=='lance'and ROSTER_CONFIG.mode_value==1
    and c.char==3 and c.variant==1 and c.world==0 and c.level==0
    and c.areaType==1 and c.yHigh==1 and not c.grounded and c.vy>0 and c.vy<128
    and e and e.id==6 and e.state<2 and e.y==184 and e.dx>20 and e.dx<96
    and c.y>=88 and c.y+32<198 then
  local i=e.slot
  if i and i%1==0 and i>=0 and i<6 and c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128
     and c.r('Enemy_ID',i)==6 and c.r('Enemy_State',i)<2
     and c.r('Enemy_Y_HighPos',i)==1 and c.r('Enemy_Y_Position',i)==184
     and c.r('Enemy_BoundBoxCtrl',i)==9
     and c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)==e.x
     and e.x-c.x==e.dx and lanceRetreatLane(c,e)then
   holdA=0;cooldown=0
   return {left=true,a=false,b=false}
  end
 end
"""

def movement_controls(b):
 rows=[]
 for gap in [25,33]:
  for fraction in [0,65535]:
   pair=[]
   for retreat in [False,True]:
    q=full(b,1,1)
    q.put(SelectedCharacter=3,BillVariant=1,MarioVariant=0,Player_X_Position=232,Player_PageLoc=6,
          Player_Y_Position=126,Player_Y_HighPos=1,Player_State=1,Player_Y_Speed=2,PlayerSize=0,
          RgDoubleJump=128,ScreenLeft_PageLoc=6,ScreenLeft_X_Pos=120,ScreenRight_PageLoc=7,
          ScreenRight_X_Pos=119,Player_Rel_XPos=112,Player_Pos_ForScroll=112)
    q.array('MmVY',[0,0,2]);seed_vx(q,0,1.25);q.array('MmXFraction',[fraction&255,fraction>>8])
    q.invoke('InitGoomba');ex=1768+gap
    q.put(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_Y_HighPos=1,Enemy_Y_Position=184,
          Enemy_X_Position=ex&255,Enemy_PageLoc=ex>>8,ObjectOffset=0)
    path=[];retreats=0
    for age in range(45):
     x=coord(q,'X');y=q.get('Player_Y_Position');ex=q.get('Enemy_X_Position')+256*q.get('Enemy_PageLoc');dx=ex-x
     active=retreat and q.get('Player_State')!=0 and 0<q.get('Player_Y_Speed')<128 and 20<dx<96 and 88<=y and y+32<198
     bits=2 if active else 5
     retreats+=int(active);tick(q,bits);q.set('ObjectOffset',0);q.invoke('MoveNormalEnemy')
     box=[q.get('BoundingBox_UL_Corner',i)for i in range(4)]
     ex=q.get('Enemy_X_Position')+256*q.get('Enemy_PageLoc');camera=q.get('ScreenLeft_PageLoc')*256+q.get('ScreenLeft_X_Pos')
     enemy=[ex-camera+3,198,ex-camera+13,204]
     overlap=box[0]<=enemy[2]and box[2]>=enemy[0]and box[1]<=enemy[3]and box[3]>=enemy[1]
     s=dict(update=age+1,input=bits,x=coord(q,'X'),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vy=q.get('Player_Y_Speed'),enemy_x=ex,actual_player_box=box,Goomba_proxy_box=enemy,overlap=overlap)
     path.append(s)
     if overlap or s['state']==0:break
    assert path
    if retreat:assert not path[-1]['overlap']and path[-1]['state']==0 and path[-1]['enemy_x']-path[-1]['x']>=24 and retreats>0
    else:assert path[-1]['overlap']
    pair.append(dict(retreat=retreat,active_retreat_updates=retreats,updates=len(path),final=path[-1]))
   rows.append(dict(initial_gap=gap,horizontal_fraction=fraction,paired=pair))
 return dict(passed=True,cases=rows,
             model='Actual full PlayerCtrl/Bill source body/movement/background caller and native InitGoomba/MoveNormalEnemy in four paired legal flat-floor arenas. Player1768/126/+1.25/+2 and groundGoomba gaps25/33, both Xfraction endpoints. No source tick/event changes.',
             limits='Literal input-branch translation, not executed Lua or exact full failed RAM. Goomba proxy is its linked bbox9 with current source position; actual native enemy damage, projectiles/cadence/contact, NMI/IRQ/PPU and full route are not simulated. Baseline can reach an overlapping descending body; retreat reaches floor with >=24px world gap.' )

def scope_controls():
 s=dict(name='lance',mode=1,char=3,variant=1,world=0,level=0,area=1,yhigh=1,ground=False,vy=2,id=6,state=0,ey=184,dx=33,y=126,owner=True,lane=True,behind=False)
 def yes(q):return q['name']=='lance'and q['mode']==1 and q['char']==3 and q['variant']==1 and q['world']==q['level']==0 and q['area']==q['yhigh']==1 and not q['ground']and 0<q['vy']<128 and q['id']==6 and q['state']<2 and q['ey']==184 and 20<q['dx']<96 and q['y']>=88 and q['y']+32<198 and q['owner']and q['lane']and not q['behind']
 assert yes(s);rows=[dict(changes={},admitted=True)]
 for k,v in [('name','bill'),('mode',0),('variant',0),('ground',True),('vy',252),('id',13),('dx',20),('dx',96),('owner',False),('lane',False),('behind',True)]:
  assert not yes({**s,k:v});rows.append(dict(changes={k:v},admitted=False))
 return dict(scope='Literal boundary/foreign controller model, not Lua execution',cases=rows)

def main():
 old=ROOT/'build/verification/compact-next-lance-9ea-hard-v1'
 out=ROOT/'build/verification/compact-next-lance-9ea-hard-v2'
 receipt=ROOT/'docs/qa/lance-hard-9ea-v1-native-failure-2026-10-27.json'
 origin=ROOT/'tools/playthroughs/current_roster_lance_pipe_exit_v2.lua'
 policy=ROOT/'tools/playthroughs/current_roster_lance_air_retreat_v3.lua'
 rom=ROOT/'build/bill_early_cache.nes'
 assert not out.exists()and not policy.exists()and not receipt.exists()and sha(rom)==SHA
 prior=json.loads((old/'ready.json').read_text());failed=json.loads((old/'result.json').read_text())
 assert failed['ROM_sha256']==prior['ROM_sha256']==SHA and not failed['passed']and failed['actual_mode']==1 and failed['frames']==3371
 assert failed['reason']=='Zero-death 1-1 route'and sha(origin)==prior['bindings'][str(origin)]
 assert sha(old/'review.json')=='3742e0be934795bc4a91c158fffc960bffe58debd7ddffb15449cf66e7d9e9b9'
 assert sha(old/'selected-whole-frames.png')=='b9d5bfa1495db983047e61fb9d9f9a5288a2833e82eb2e51811794f18c628895'
 trace=list(csv.DictReader((old/'trace.csv').open(newline='')))
 final=trace[-1];assert all(int(final[k])==v for k,v in dict(frame=3371,x=1783,y=167,vy=252,power=0,engine=11).items())
 assert trace[-2]['vy']=='4'and trace[-2]['power']=='1'
 masks=[int(q['mask'])for q in csv.DictReader((old/'inputs.csv').open(newline=''))][-46:]
 assert set(masks)=={5,69}
 raw=origin.read_bytes();text=raw.decode();nl='\r\n'if b'\r\n'in raw else'\n'
 anchor='local holdA,cooldown=0,0'+nl;marker=' -- Land at the near edge of 1-3\'s high platform before firing at its Goombas.'+nl
 helper=HELPER.replace('\n',nl);branch=BRANCH.replace('\n',nl)
 assert text.count(anchor)==text.count(marker)==1
 new=text.replace(anchor,anchor+helper,1).replace(marker,branch+marker,1)
 assert new.replace(helper,'',1).replace(branch,'',1)==text
 assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset|setInput)\s*\(',new)and'io.open'not in new
 b=scoped_load(rom);cpu=movement_controls(b);scopes=scope_controls()
 evidence=[old/n for n in ['ready.json','result.json','review.json','trace.csv','inputs.csv','selected-whole-frames.png']]
 ledger=dict(identity='lance',mode=1,ROM_sha256=SHA,component='controller-only1-1',outcome='FALSE',frame=3371,x=1783,y=167,
             failure='Zero-death guard on descent directly above ROOT-viewed ground Goomba',remaining='Fresh source-qualified air-retreat controller route/replay. Exact injury slot/shot allocation/contact branch not recorded; no product bug demonstrated.')
 put(receipt,dict(status='NATIVE_FALSE',ROM_sha256=SHA,actual_numeric_mode=1,frame=3371,route_clear=False,zero_death=False,whole_PPU_frames_valid=3061,
                 completed_GameLoops=failed['completed_loops'],complete256_DMAs=failed['completed_DMAS'],selected_frames_ROOT_viewed=6,
                 final_trace=final,actual_controller='Final46 masks are only5/69: Right+Down with ordinary12physical-poll B pulses. Descent continues fromY102/vy0 toY163/vy4, then death atY167; this is not absent B input.',
                 source='Hard Bill/Lance cannot ordinary-stomp. BillMove invokes ImmediateInput in air: Left immediately sets negative1.25; neutral retains current airborne VX. Existing ground controller can turn then stop/prone-fire; its muzzle/branch is preserved. Exact hostile slot and all shot states/hits are unlogged, so no absolute collision-owner, gun-cadence malfunction or hitbox bug is inferred.',
                 ledger_entry=ledger,external_evidence=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)for p in evidence]))
 policy.write_bytes(new.encode());prepare(SimpleNamespace(rom=rom,expected_sha256=SHA,output=out,identity='lance',mode='hard',frames=8000,policy=policy,replay=None))
 (out/'controller.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),new.splitlines(True),fromfile=origin.name,tofile=policy.name)),newline='\n')
 put(out/'source-controller-controls.json',dict(movement=cpu,scope=scopes))
 put(out/'negative-ledger-entry.json',ledger)
 review=dict(PREPARED_DO_NOT_RUN=True,native_run=False,ROM_sha256=SHA,controller_only=True,reverse_two_insertions_exact=True,
             scope='LanceHard outdoor1-1 only. Real bounded canonical groundGoomba owner/bbox9,20<dx<96, positive downward speed and feet still above enemyTop198. Probe full body/head lane every8px from32px behind through enemy+14; require support216 and reject another live ordinary enemy in48px retreat lane.',
             response='Clear ONLY own holdA/cooldown; ordinary Left with A/B released while safely above threat. Existing grounded prone-fire, original first-mushroom pursuit, original third-pipe exit release and every unrelated branch remain exact. No game state/input API writes, resources, cheats or limit changes.',
             source_controls=str(out/'source-controller-controls.json'),
             discarded_model='A movement-only arena was not sufficient to call standalone RosterWeapons: an exploratory call had early input-history publication, and a second rejected an unexpected ROM write atF040. Neither is native gameplay or a source bug. Final qualification is limited to valid fullPlayerCtrl/nativeGoomba motion; no shot/hit proof is claimed.',
             limits='No native run; actual dynamic lane admission/ground firing/contact/clear/replay remain required. No no-lag, universal hazard or all-powerup claim.',public_failure_receipt=str(receipt))
 put(out/'controller-review.json',review)
 ready=out/'ready.json';z=json.loads(ready.read_text());z['PREPARED_DO_NOT_RUN']=True;z['controller_revision']=review
 for p in [Path(__file__).resolve(),origin,receipt,out/'controller.patch',out/'controller-review.json',out/'source-controller-controls.json',out/'negative-ledger-entry.json',ROOT/'src/roster.s',ROOT/'src/roster_weapons.s',ROOT/'src/bill_source_body.s',ROOT/'tools/audit/luigi_mario_profile731_cpu_v1.py',ROOT/'tools/audit/mario_luigi731_coefficients_v1.py']+evidence:z['bindings'][str(p)]=sha(p)
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease=True,argv=z['command']));z['bindings'][str(out/'command.json')]=sha(out/'command.json')
 for p,h in z['bindings'].items():assert sha(p)==h,p
 put(ready,z);assert origin.read_bytes()==raw
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),receipt=str(receipt),receipt_sha256=sha(receipt))))

if __name__=='__main__':main()
