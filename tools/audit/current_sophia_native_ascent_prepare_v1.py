"""Prepare one SophiaEasy native-ascent hold at the tall1-1 pipe."""
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
OLD=' elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<34 end\n'
NEW=""" elseif not c.grounded and jumpAge>=0 then
  if ROSTER_CONFIG.name=='sophia'and ROSTER_CONFIG.mode_value==0
     and c.char==11 and c.world==0 and c.level==0 and c.areaType==1
     and c.yHigh==1 and c.x>=832 and c.x<960 then
   -- Physical polls are not logic updates. Retain A through native ascent.
   b.a=c.r('XgRise')~=0 or c.vy>=128
  else b.a=jumpAge<34 end
 end
"""

def boundary_models():
 base=dict(name='sophia',mode=0,char=11,world=0,level=0,areaType=1,yHigh=1,x=894,grounded=False,jumpAge=35,rise=0,vy=254)
 def scope(s):return s['name']=='sophia'and s['mode']==0 and s['char']==11 and s['world']==0 and s['level']==0 and s['areaType']==1 and s['yHigh']==1 and 832<=s['x']<960 and not s['grounded']and s['jumpAge']>=0
 rows=[]
 def case(name,changes,want_scope,wantA):
  s={**base,**changes};actual_scope=scope(s);A=(s['rise']!=0 or s['vy']>=128)if actual_scope else s['jumpAge']<34
  assert actual_scope==want_scope and A==wantA;rows.append(dict(name=name,changes=changes,expected_scope=want_scope,expected_A=wantA,literal_scope=actual_scope,literal_A=A))
 case('Native upward motion beyond34polls',{},True,True)
 case('Native initial rise',dict(rise=1,vy=0),True,True)
 case('Native apex releases',dict(vy=0),True,False)
 case('Native falling releases',dict(vy=2),True,False)
 for k,v in [('name','pit'),('mode',1),('char',7),('world',1),('level',1),('areaType',2),('yHigh',0),('x',831),('x',960),('grounded',True)]:case('Foreign/boundary '+k+'='+str(v),{k:v},False,False)
 case('First X',dict(x=832),True,True);case('Last X',dict(x=959),True,True)
 case('Prior air34 rule unchanged outside scope',dict(x=1000,jumpAge=33),False,True)
 return rows

def source_motion_controls(b):
 results=[]
 for mode in ['release_after22_logic','hold34_logic','native_ascent']:
  q=Arena(b,11);q.invoke('InventoryInit')
  q.put(CrossoverBehaviorVersion=0,PlayerStatus=0,Player_X_Position=126,Player_PageLoc=3,MmOldX=126,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,ScreenLeft_X_Pos=15,ScreenLeft_PageLoc=3,ScreenRight_X_Pos=14,ScreenRight_PageLoc=4)
  previous=0;ys=[];release=None;held=0
  for tick in range(75):
   A=tick<(22 if mode=='release_after22_logic'else 34)if mode!='native_ascent'else tick==0 or q.get('XgRise')!=0 or q.get('Player_Y_Speed')>=128
   if A:held+=1
   elif release is None:release=tick+1
   bits=1+(128 if A else 0);q.put(SavedJoypadBits=bits,A_B_Buttons=128 if A else 0,PreviousA_B_Buttons=previous)
   q.invoke('ExpandedMovement');q.invoke('ExpandedWeapons');previous=128 if A else 0
   ys.append(q.get('Player_Y_Position'))
   if q.get('Player_Y_Position')>=200:break
  minimum=min(ys);assert minimum==(112 if mode=='release_after22_logic'else 104)
  results.append(dict(input_rule=mode,actual_assembled_calls='ExpandedMovement then ExpandedWeapons, including real input-history publication',held_logic_updates=held,first_release_logic_update=release,minY=minimum,minimum_update=ys.index(minimum)+1,clearance_for_actual_pipe_top144=minimum+32<144,limits='Isolated source movement/input caller pair; no terrain/enemy/NMI/PPU or exact failed-world replay. Native old span2358..2391 contains22completed loops.'))
 return results

def main():
 old=ROOT/'build/verification/compact-next-sophia-6be-easy-v1';out=ROOT/'build/verification/compact-next-sophia-6be-easy-v2'
 origin=ROOT/'tools/playthroughs/pit_rygar_sophia_dry_policy.lua';policy=ROOT/'tools/playthroughs/current_roster_sophia_native_ascent_v2.lua';receipt=ROOT/'docs/qa/sophia-easy-v1-native-failure-2026-10-27.json'
 assert not out.exists()and not policy.exists()and not receipt.exists()
 prior=json.loads((old/'ready.json').read_text());failed=json.loads((old/'result.json').read_text())
 assert failed['ROM_sha256']==prior['ROM_sha256']==EXPECTED and failed['actual_mode']==0 and not failed['passed']and failed['frames']==2982 and failed['reason']=='Zero-death 1-1 route'
 assert sha(old/'review.json')=='b702639e5ba4ef88fbc36528c9c23a0b38bd2204bc1cb1930ab739c7cd7c4497'and sha(old/'selected-whole-frames.png')=='65f6c78917b9141698afc5aea0bf22309ede52672c6b589e113919a26a7c989f'
 assert sha(origin)==prior['bindings'][str(origin)]
 raw=origin.read_bytes();text=raw.decode();nl='\r\n'if b'\r\n'in raw else'\n';needle=OLD.replace('\n',nl);replacement=NEW.replace('\n',nl)
 assert text.count(needle)==1;corrected=text.replace(needle,replacement,1);assert corrected.replace(replacement,needle,1).encode()==raw
 assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset|setInput)\s*\(',corrected)and 'io.open'not in corrected
 rom=ROOT/'build/samus_fixed_hud_current4a.nes';assert sha(rom)==EXPECTED;b=scoped_load(rom)
 cases=boundary_models();motion=source_motion_controls(b)
 evidence=[old/n for n in ['ready.json','result.json','review.json','trace.csv','inputs.csv','selected-whole-frames.png']]
 negative=dict(status='NATIVE_FALSE',ROM_sha256=EXPECTED,identity='sophia',mode='Easy',actual_numeric_mode=0,frame=2982,reason=failed['reason'],route_clear=False,zero_death=False,whole_PPU_frames_valid=2738,completed_GameLoops=2038,actual256_DMAs=1187,selected_frames_ROOT_viewed=5,actual_trace='Repeated34physical-poll A spans contain20..22 completed loops. Example2358..2391 loops1623->1645. Multiple native apicesY112 atX894; final death2982/X894/Y166 engine11. Exact final contact actor/PC not recorded.',source_result='Actual compiled ExpandedMovement+ExpandedWeapons reproduce minimum112 for22held logic updates; full/native-held ascent reaches104. XgRise41px is followed by ballistic ascent; falling-edge release selects much stronger upward friction.',geometry_correction='Existing selected sheet512x720 final panel startsY480; fourth pipe top is at rawY624/local144. Source flat Sophia bottom=PY+32; PY104 clears144, short-hold112 reaches boundary. This is not a canonical95 claim.',ledger_entry=dict(identity='sophia',mode=0,ROM_sha256=EXPECTED,component='controller-only1-1',outcome='FALSE',frame=2982,x=894,y=166,failure='Zero-death guard after tall-pipe retries',remaining='Fresh v2 actual-input clear/replay and inventory coverage; no source physics defect established.'),external_evidence=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)for p in evidence],payload_exclusions='No ROM/audio/settings/containers/raw-frame or source trees copied.')
 put(receipt,negative);policy.write_bytes(corrected.encode());prepare(SimpleNamespace(rom=rom,expected_sha256=EXPECTED,output=out,identity='sophia',mode='easy',frames=8000,policy=policy,replay=None))
 (out/'controller.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),corrected.splitlines(True),fromfile=origin.name+' (unchanged shared)',tofile=policy.name)),newline='\n')
 review=dict(PREPARED_DO_NOT_RUN=True,native_run=False,ROM_sha256=EXPECTED,reverse_substitution_exact=True,boundary_and_foreign_models=cases,source_movement_controls=motion,scope='SophiaEasy outdoors1-1/X832..<960/Yhigh1 only; existing launched air branch. Hold real A while XgRise or exported upward velocity is active; release at native apex. No physical-poll duration assumption.',all_other_policy_bytes_unchanged=True,no_actor_motion_resource_or_outcome_writes=True,shared_harness_and_8000frame_cap_unchanged=True,remaining_limits='Not a full native scene replay; exact release/clear/landing/final enemy ownership require ROOT native run. Native controls and source cannot be retagged as route PASS.',draft_preflight='Two preparer parse attempts rejected missing whitespace before34/104. No code executed/output directory/native launch. Both corrected before this prepared packet.',public_failure_receipt=str(receipt))
 put(out/'controller-review.json',review);put(out/'negative-ledger-entry.json',negative['ledger_entry'])
 ready=out/'ready.json';z=json.loads(ready.read_text());z['PREPARED_DO_NOT_RUN']=True;z['controller_revision']=dict(policy_only=True,review=str(out/'controller-review.json'),old_negative_not_replaced=True)
 for p in [Path(__file__).resolve(),origin,receipt,out/'controller.patch',out/'controller-review.json',out/'negative-ledger-entry.json',ROOT/'src/expanded.s',ROOT/'src/source_motion.s',ROOT/'src/sophia_source_body.s',ROOT/'src/sophia_source_terrain.s']+evidence:
  z['bindings'][str(p)]=sha(p)
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease=True,argv=z['command']));z['bindings'][str(out/'command.json')]=sha(out/'command.json')
 for p,h in z['bindings'].items():assert sha(p)==h,p
 put(ready,z);assert origin.read_bytes()==raw
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),scope_models=len(cases),source_movement_cases=len(motion),public_failure_receipt=str(receipt),receipt_sha256=sha(receipt))))
if __name__=='__main__':main()
