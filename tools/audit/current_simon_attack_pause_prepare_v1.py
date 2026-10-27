"""Prepare SimonHard's scoped intentional-whip-pause watchdog correction."""
from pathlib import Path
from types import SimpleNamespace
import difflib,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from current_roster_compact_11_v1 import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
EXPECTED='6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
INSERT=""" -- A real grounded whip intentionally stops Simon; it is not a wall stall.
 -- Keep the recovery jump from firing into this low brick ceiling afterward.
 if ROSTER_CONFIG.name=='simon'and ROSTER_CONFIG.mode_value==1
    and c.char==5 and c.variant==0 and c.world==0 and c.level==0
    and c.areaType==1 and c.yHigh==1 and c.x>=2688 and c.x<2784
    and c.grounded and c.y==176 and c.r('RgAttack')~=0
    and solid(c.x+8,c.y-24)then still=0 end
"""

def gate_models():
 base=dict(name='simon',mode=1,char=5,variant=0,world=0,level=0,areaType=1,yHigh=1,x=2714,grounded=True,y=176,attack=7,roof=True)
 def gate(s):return s['name']=='simon'and s['mode']==1 and s['char']==5 and s['variant']==0 and s['world']==0 and s['level']==0 and s['areaType']==1 and s['yHigh']==1 and 2688<=s['x']<2784 and s['grounded']and s['y']==176 and s['attack']!=0 and s['roof']
 rows=[]
 def case(name,changes,want):
  s={**base,**changes};got=gate(s);assert got==want;rows.append(dict(name=name,changes=changes,expected=want,actual_literal_model=got))
 case('Actual scoped whip pause',{},True)
 for k,v in [('name','grant'),('mode',0),('char',4),('variant',1),('world',1),('level',1),('areaType',2),('yHigh',0),('x',2687),('x',2784),('grounded',False),('y',175),('y',177),('attack',0),('roof',False)]:case('Foreign or boundary '+k+'='+str(v),{k:v},False)
 for x in [2688,2783]:case('Inclusive X edge'+str(x),dict(x=x),True)
 return rows

def whole_counter_source(b):
 rows=[]
 for fixed in [False,True]:
  q=Arena(b,5);q.put(Player_X_Position=154,Player_PageLoc=10,MmOldX=154,Player_Y_Position=176,Player_State=0,Player_Y_Speed=0,PlayerStatus=0,RgAttack=7,RgAttackAge=14,RgShootPose=0,RgDoubleJump=1,ScreenLeft_PageLoc=10,ScreenLeft_X_Pos=42,ScreenRight_PageLoc=11,ScreenRight_X_Pos=41)
  still,cooldown,lastX,lastA=42,4,154,False;path=[]
  for tick in range(12):
   x=q.get('Player_X_Position');ground=q.get('Player_State')==0
   still=still+1 if x==lastX else 0;lastX=x
   if fixed and ground and q.get('Player_Y_Position')==176 and q.get('RgAttack')!=0:still=0
   A=ground and not lastA and still>20
   if cooldown>0:A=False;cooldown-=1
   q.put(SavedJoypadBits=1+(128 if A else 0),A_B_Buttons=128 if A else 0,PreviousA_B_Buttons=128 if lastA else 0)
   q.invoke('RosterMovement');q.invoke('RosterWeapons')
   path.append(dict(tick=tick+1,still=still,A=A,x=q.get('Player_X_Position'),y=q.get('Player_Y_Position'),state=q.get('Player_State'),attack=q.get('RgAttack')));lastA=A
  if fixed:assert not any(s['A']for s in path)and path[-1]['x']>154 and all(s['state']==0 and s['y']==176 for s in path)
  else:assert any(s['A']for s in path)and any(s['state']!=0 for s in path)
  rows.append(dict(corrected_watchdog=fixed,path=path,limits='Actual assembled RosterMovement+RosterWeapons with source-only Lua-counter model, remaining attack7, no NMI/PPU/terrain/enemy replay. Original no-input cooldown4 retained.'))
 return rows

def main():
 old=ROOT/'build/verification/compact-next-simon-6be-hard-v3';out=ROOT/'build/verification/compact-next-simon-6be-hard-v4'
 origin=ROOT/'tools/playthroughs/current_roster_simon_air_threat_v3.lua';policy=ROOT/'tools/playthroughs/current_roster_simon_attack_pause_v4.lua'
 receipt=ROOT/'docs/qa/simon-hard-v3-native-failure-2026-10-27.json'
 assert not out.exists()and not policy.exists()and not receipt.exists()
 previous=json.loads((old/'ready.json').read_text());failed=json.loads((old/'result.json').read_text())
 assert failed['ROM_sha256']==previous['ROM_sha256']==EXPECTED and not failed['passed']and failed['frames']==3561 and failed['reason']=='Zero-death 1-1 route'
 assert sha(old/'review.json')=='26b6c418a782a0af2b227d97e2936a8cff7668edd427b7d0507b03b4943e2be0'
 assert sha(old/'selected-whole-frames.png')=='a4c00fcdf6069f25abbb727c492615f78e31a07e8d0d98821a90958e007e5227'
 assert sha(origin)==previous['bindings'][str(origin)]
 raw=origin.read_bytes();text=raw.decode();nl='\r\n'if b'\r\n'in raw else'\n';insert=INSERT.replace('\n',nl)
 needle=' if c.x==lastX then still=still+1 else still=0 end;lastX=c.x'+nl
 assert text.count(needle)==1;corrected=text.replace(needle,needle+insert,1)
 assert corrected.replace(insert,'',1).encode()==raw
 assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset|setInput)\s*\(',corrected)and 'io.open'not in corrected
 rom=ROOT/'build/samus_fixed_hud_current4a.nes';assert sha(rom)==EXPECTED;b=scoped_load(rom)
 cases=gate_models();counter=whole_counter_source(b)
 evidence=[old/n for n in ['ready.json','result.json','review.json','trace.csv','inputs.csv','selected-whole-frames.png']]
 negative=dict(status='NATIVE_FALSE',ROM_sha256=EXPECTED,identity='simon',variant=0,mode='Hard',actual_numeric_mode=1,native_frame=3561,native_reason=failed['reason'],route_clear=False,zero_death=False,whole_PPU_frames_valid=3272,completed_GameLoops=3283,actual256_DMAs=2760,selected_images_reviewed_by_ROOT=5,missing_collision_ownership='No final actual enemy slot/ID/contactPC was serialized; final selected PNG supports nearby Goomba contact, not an absolute owner attribution.',controller_observation='X2714/Y176 stationary3493..3534 during intentional crouch-whips. B edges3493/3520. Then generic still>20 requests jump after cooldown: A3538, native rise3540, head obstructionY152 at3545, death3561/X2739/Y174. No physics defect established.',old_negatives_preserved=True,proposed_successor='Scoped controller-only reset of its own still counter while source RgAttack intentionally stops grounded Simon under the actual brick roof. No mechanics/assertion/cap/source changes.',ledger_entry=dict(identity='simon',variant=0,mode=1,ROM_sha256=EXPECTED,component='controller-only1-1',outcome='FALSE',failure='Zero-death guard',frame=3561,x=2739,y=174,remaining='Fresh v4 controller attempt and fullclear/replay still required; no fullpowerup claim.'),external_evidence=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)for p in evidence],payload_exclusions='No ROM/NSF/audio/settings/containers/raw-frame trees copied. Source native artifacts remain in their original bounded directory.')
 put(receipt,negative)
 policy.write_bytes(corrected.encode());prepare(SimpleNamespace(rom=rom,expected_sha256=EXPECTED,output=out,identity='simon',mode='hard',frames=8000,policy=policy,replay=None))
 (out/'controller.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),corrected.splitlines(True),fromfile=origin.name+' (retained v3)',tofile=policy.name)),newline='\n')
 review=dict(PREPARED_DO_NOT_RUN=True,native_run=False,ROM_sha256=EXPECTED,all_v3_branches_reverse_exact=True,foreign_and_boundary_models=cases,whole_counter_and_source_controls=counter,owned_changes='Only controller still counter reset; every real actor/body/resource/source state remains read-only.',source_contract='roster.s BillMove explicitly stops grounded Simon when RgAttack!=0. Treating that known deliberate stop as obstacle stall causes the old still>20 jump. Native ordinary whip21updates/activeage14 means a successfully engaged enemy can leave a short remaining attack pause.',native_limits='Legal isolated source calls and literal counter model do not reproduce actual unlogged enemy/roof/RNG/NMI fields. Existing native FALSE remains; v4 has no clear or pickup claim.',unchanged='Lost-first-pickup escape, earlier native Goomba doublejump admission, all gap/backflip/navigation/combat rules, shared harness and8000frame cap.',negative_receipt=str(receipt))
 put(out/'controller-review.json',review);put(out/'negative-ledger-entry.json',negative['ledger_entry'])
 ready=out/'ready.json';z=json.loads(ready.read_text());z['PREPARED_DO_NOT_RUN']=True;z['controller_revision']=dict(policy_only=True,review=str(out/'controller-review.json'),old_negatives_not_replaced=True,first_power_acquisition_claim=False)
 for p in [Path(__file__).resolve(),origin,receipt,out/'controller.patch',out/'controller-review.json',out/'negative-ledger-entry.json',ROOT/'src/roster.s',ROOT/'src/roster_weapons.s']+evidence:
  z['bindings'][str(p)]=sha(p)
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease=True,argv=z['command']));z['bindings'][str(out/'command.json')]=sha(out/'command.json')
 for p,h in z['bindings'].items():assert sha(p)==h,p
 put(ready,z);assert origin.read_bytes()==raw
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),source_cases=len(cases),whole_counter_source_cases=len(counter),public_failure_receipt=str(receipt),receipt_sha256=sha(receipt))))
if __name__=='__main__':main()
