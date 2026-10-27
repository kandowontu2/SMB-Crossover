"""Prepare one controller-only source-doublejump over a real Goomba threat."""
from pathlib import Path
from types import SimpleNamespace
import difflib,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from current_roster_compact_11_v1 import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
EXPECTED='6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
INSERT=""" -- SimonHard's descending second-pipe arc meets a real ground Goomba.
 -- The whip needs fourteen logic updates; use the unused native air jump.
 if ROSTER_CONFIG.name=='simon'and ROSTER_CONFIG.mode_value==1
    and c.char==5 and c.variant==0 and c.world==0 and c.level==0
    and c.areaType==1 and c.yHigh==1 and c.x>=640 and c.x<736
    and not c.grounded and c.vy<128 and not c.lastA and c.r('RgDoubleJump')~=0 then
  for slot=0,5 do
   local flag=c.r('Enemy_Flag',slot)
   if flag>0 and flag<128 and c.r('Enemy_ID',slot)==6
      and c.r('Enemy_State',slot)<2 and c.r('Enemy_Y_HighPos',slot)==1
      and c.r('Enemy_BoundBoxCtrl',slot)==9 then
    local left=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)+3
    local above=c.r('Enemy_Y_Position',slot)+14-(c.y+32)
    if left>=c.x-8 and left<c.x+64 and above>=8 and above<=64 then
     holdA=0;cooldown=0
     return{right=true,a=true,b=false}
    end
   end
  end
 end
"""

def models():
 base=dict(name='simon',mode=1,char=5,variant=0,world=0,level=0,areaType=1,yHigh=1,x=674,y=104,grounded=False,vy=2,lastA=False,double=1,flag=1,id=6,state=0,enemyHigh=1,bbox=9,enemyX=704,enemyY=184)
 def admitted(s):
  return s['name']=='simon'and s['mode']==1 and s['char']==5 and s['variant']==0 and s['world']==0 and s['level']==0 and s['areaType']==1 and s['yHigh']==1 and 640<=s['x']<736 and not s['grounded']and s['vy']<128 and not s['lastA']and s['double']!=0 and 0<s['flag']<128 and s['id']==6 and s['state']<2 and s['enemyHigh']==1 and s['bbox']==9 and s['x']-8<=s['enemyX']+3<s['x']+64 and 8<=s['enemyY']+14-(s['y']+32)<=64
 rows=[]
 def case(name,changes,want):
  s={**base,**changes};got=admitted(s);assert got==want,(name,s,got);rows.append(dict(name=name,changes=changes,expected_admission=want,actual_literal_model=got))
 case('Legal descending threat',{},True)
 for k,v in [('name','grant'),('mode',0),('char',4),('variant',1),('world',1),('level',1),('areaType',2),('yHigh',0),('x',639),('x',736),('grounded',True),('vy',128),('lastA',True),('double',0),('flag',0),('flag',128),('id',0),('state',2),('enemyHigh',2),('bbox',3),('enemyX',662),('enemyX',735),('enemyY',126),('enemyY',184+3)]:case('Reject '+k+'='+str(v),{k:v},False)
 case('First X boundary with matching target',dict(x=640,enemyX=670),True)
 case('Last X boundary with matching target',dict(x=735,enemyX=765),True)
 case('Vertical minimum clearance8',dict(enemyY=130),True)
 case('Vertical maximum clearance64',dict(enemyY=186),True)
 case('Left threat boundary',dict(enemyX=663),True)
 case('Right threat boundary',dict(enemyX=734),True)
 return rows

def launch_controls(b):
 rows=[]
 for fresh,available in [(True,True),(False,True),(True,False)]:
  q=Arena(b,5);q.put(Player_X_Position=162,Player_PageLoc=2,MmOldX=162,Player_Y_Position=104,Player_State=1,Player_Y_Speed=2,RgDoubleJump=int(available),A_B_Buttons=128,PreviousA_B_Buttons=0 if fresh else 128,SavedJoypadBits=129,RgAttack=20,RgAttackAge=6,RgShootPose=12)
  q.set('MmVY',2,2);q.invoke('RosterMovement')
  launched=fresh and available
  assert(q.get('Player_Y_Speed')>=128)==launched and(q.get('Player_Y_Position')<104)==launched
  assert q.get('RgDoubleJump')==(0 if launched else int(available))
  assert q.get('RgAttack')==(0 if launched else 20)
  rows.append(dict(fresh_A=fresh,unused_doublejump=available,native_launched=launched,after_y=q.get('Player_Y_Position'),after_vy=q.get('Player_Y_Speed'),after_doublejump=q.get('RgDoubleJump'),after_attack=q.get('RgAttack'),limits='Actual assembled isolated RosterMovement only; not a replay of the unlogged enemy/NMI state.'))
 return rows

def main():
 old=ROOT/'build/verification/compact-next-simon-6be-hard-v2';out=ROOT/'build/verification/compact-next-simon-6be-hard-v3'
 origin=ROOT/'tools/playthroughs/current_roster_simon_lost_power_v2.lua';policy=ROOT/'tools/playthroughs/current_roster_simon_air_threat_v3.lua'
 assert not out.exists()and not policy.exists()
 previous=json.loads((old/'ready.json').read_text());failed=json.loads((old/'result.json').read_text())
 assert failed['ROM_sha256']==previous['ROM_sha256']==EXPECTED and not failed['passed']and failed['frames']==1315 and failed['reason']=='Zero-death 1-1 route'
 assert sha(origin)==previous['bindings'][str(origin)]
 raw=origin.read_bytes();text=raw.decode();nl='\r\n'if b'\r\n'in raw else'\n';insert=INSERT.replace('\n',nl)
 needle=' local e'+nl;assert text.count(needle)==1;corrected=text.replace(needle,insert+needle,1)
 assert corrected.replace(insert,'',1).encode()==raw
 assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset|setInput)\s*\(',corrected)and 'io.open'not in corrected
 rom=ROOT/'build/samus_fixed_hud_current4a.nes';assert sha(rom)==EXPECTED;b=scoped_load(rom)
 box=location(b,'BoundBoxCtrlData')+9*4;assert list(b['raw'][box:box+4])==[3,14,13,20]
 rows=models();source=launch_controls(b);policy.write_bytes(corrected.encode())
 prepare(SimpleNamespace(rom=rom,expected_sha256=EXPECTED,output=out,identity='simon',mode='hard',frames=8000,policy=policy,replay=None))
 (out/'controller.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),corrected.splitlines(True),fromfile=origin.name+' (retained v2)',tofile=policy.name)),newline='\n')
 review=dict(PREPARED_DO_NOT_RUN=True,native_run=False,ROM_sha256=EXPECTED,old_negative_preserved=True,all_v2_lost_pickup_chase_and_other_branches_byte_unchanged=True,no_emulated_writes=True,finite_scope_controls=rows,actual_assembled_doublejump_controls=source,observed_failure='V2 first jump clears second-pipe edge at1262. First aerial B occurs1309/X688/Y147; completed loops1274 then1277 at death1315/X693/Y170. Existing source ordinary whip starts age0 and hits only age>=14: this is too late. Final ROOT-reviewed image has Goomba directly below; exact collision slot/ID unlogged.',correction='Only Hard Simon variant0 outdoor1-1 X640..<736, fresh A available while descending, native unused RgDoubleJump, live native Goomba/box9. Source bbox left=EX+3/top=EY+14; ahead64px and player-feet clearance8..64. One genuine Right+A, Bfalse; original source consumes doublejump and cancels pending whip. No stomp reliance.',geometry_binding=dict(symbol='BoundBoxCtrlData',index=9,bytes=[3,14,13,20]),counterfactual_limits='Actual v2 enemy-slot positions, bounding control and RgDoubleJump were not serialized. New gate will read them natively; its exact original activation frame is not claimed. Isolated legal source arena proves fresh-A consumption/cancellation, not full route clearance.',guards='Same original8000frame/capture/zero-death/fullDMA-E3/CHR/NMI/IRQ/5SMC/SP/deadline guards. No cap increase or physics edits.')
 put(out/'controller-review.json',review)
 ready=out/'ready.json';z=json.loads(ready.read_text());z['PREPARED_DO_NOT_RUN']=True;z['controller_revision']=dict(policy_only=True,review=str(out/'controller-review.json'),old_negatives_not_replaced=True,first_power_acquisition_claim=False)
 for p in [Path(__file__).resolve(),origin,out/'controller.patch',out/'controller-review.json',old/'ready.json',old/'result.json',old/'trace.csv',old/'inputs.csv',ROOT/'src/roster.s',ROOT/'src/roster_weapons.s',ROOT/'src/collision.s']:
  z['bindings'][str(p)]=sha(p)
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease=True,argv=z['command']));z['bindings'][str(out/'command.json')]=sha(out/'command.json')
 for p,h in z['bindings'].items():assert sha(p)==h,p
 put(ready,z);assert origin.read_bytes()==raw
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),policy_sha256=sha(policy),scope_cases=len(rows),source_launch_cases=len(source))))
if __name__=='__main__':main()
