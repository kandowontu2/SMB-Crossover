"""Prepare one SimonHard lost-first-pickup controller escape; never launch."""
from pathlib import Path
from types import SimpleNamespace
import difflib,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from current_roster_compact_11_v1 import prepare
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
EXPECTED='6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
LOCAL='local simonFirstPickupSeen=false\n'
INSERT=""" -- SimonHard: abandon only the observed, subsequently lost first pickup.
 -- Retrying its head bump while standing on the row cannot reveal it again.
 if ROSTER_CONFIG.name=='simon'and ROSTER_CONFIG.mode_value==1
    and c.char==5 and c.variant==0 and c.world==0 and c.level==0
    and c.areaType==1 and not firstPowerDone then
  local observable=false
  for slot=0,5 do
   if c.r('Enemy_Flag',slot)>0 and c.r('Enemy_ID',slot)==0x2e then observable=true end
  end
  simonFirstPickupSeen=simonFirstPickupSeen or observable
  if simonFirstPickupSeen and not observable and c.camera>=307
     and c.grounded and c.yHigh==1 and c.y==112 and c.x>=c.camera and c.x<416 then
   firstPowerDone=true;holdA=0;cooldown=0
  end
 end
"""

def models():
 base=dict(name='simon',mode=1,char=5,variant=0,world=0,level=0,areaType=1,done=False,seen=True,camera=307,grounded=True,yHigh=1,y=112,x=330,actors=[])
 def evaluate(s):
  scoped=s['name']=='simon'and s['mode']==1 and s['char']==5 and s['variant']==0 and s['world']==0 and s['level']==0 and s['areaType']==1 and not s['done']
  observable=any(flag>0 and ident==0x2e for flag,ident in s['actors'])if scoped else False
  seen=s['seen']or observable if scoped else s['seen']
  escape=scoped and seen and not observable and s['camera']>=307 and s['grounded']and s['yHigh']==1 and s['y']==112 and s['x']>=s['camera']and s['x']<416
  return dict(escape=escape,seen=seen,observable=observable)
 cases=[]
 def case(label,changes,want):
  s={**base,**changes};got=evaluate(s);assert got['escape']==want,(label,s,got,want);cases.append(dict(name=label,changes=changes,expected_escape=want,observed_literal_model=got))
 case('Actual grounded lost-pickup retry',{},True)
 case('Never observed a pickup',dict(seen=False),False)
 for slot in range(6):
  actors=[(0,0)]*6;actors[slot]=(1,0x2e);case('Observable pickup slot'+str(slot),dict(actors=actors),False)
 for key,value in [('name','link'),('mode',0),('char',4),('variant',1),('world',1),('level',1),('areaType',2),('done',True),('camera',306),('grounded',False),('yHigh',0),('y',111),('y',113),('y',176),('x',306),('x',416)]:case('Reject '+key+'='+str(value),{key:value},False)
 case('Last admitted x',dict(x=415),True)
 case('Camera beyond player',dict(camera=331),False)
 case('Unrelated live enemy is not pickup',dict(actors=[(1,6)]),True)
 case('Erased stale pickup ID is not observable',dict(actors=[(0,0x2e)]),True)
 # Whole ownership progression: visible actor first arms this Lua latch but
 # cannot escape; loss in air cannot escape; grounded row state escapes.
 s={**base,'seen':False,'actors':[(1,0x2e)]};a=evaluate(s);assert a['seen']and not a['escape']
 s.update(seen=a['seen'],actors=[],grounded=False);b=evaluate(s);assert not b['escape']
 s.update(grounded=True);c=evaluate(s);assert c['escape']
 return cases,dict(visible=a,lost_in_air=b,then_grounded_row=c)

def main():
 old=ROOT/'build/verification/compact-next-simon-6be-hard-v1';out=ROOT/'build/verification/compact-next-simon-6be-hard-v2'
 origin=ROOT/'tools/playthroughs/link_simon_ryu_policy.lua';policy=ROOT/'tools/playthroughs/current_roster_simon_lost_power_v2.lua'
 assert not out.exists()and not policy.exists()
 prior=json.loads((old/'ready.json').read_text());negative=json.loads((old/'result.json').read_text())
 assert prior['ROM_sha256']==negative['ROM_sha256']==EXPECTED and negative['passed']is False and negative['frames']==8000 and negative['reason']=='finite frame bound'and negative['zero_deaths']
 assert sha(origin)==prior['bindings'][str(origin)]
 raw=origin.read_bytes();text=raw.decode();nl='\r\n'if b'\r\n'in raw else'\n'
 local=LOCAL.replace('\n',nl);insert=INSERT.replace('\n',nl)
 local_anchor="local firstPowerDone,powerStage,powerAge,powerMount=false,'approach',0,nil"+nl
 anchor=' if c.world==0 and c.level==0 and not firstPowerDone then'+nl
 assert text.count(local_anchor)==text.count(anchor)==1
 corrected=text.replace(local_anchor,local_anchor+local,1).replace(anchor,insert+anchor,1)
 assert corrected.replace(insert,'',1).replace(local,'',1).encode()==raw
 assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset|setInput)\s*\(',corrected)and 'io.open'not in corrected
 assert 'firstPowerDone=true;holdA=0;cooldown=0'in INSERT and 'powerStage='not in INSERT and 'powerMount='not in INSERT
 cases,progression=models();policy.write_bytes(corrected.encode())
 rom=ROOT/'build/samus_fixed_hud_current4a.nes';assert sha(rom)==EXPECTED
 prepare(SimpleNamespace(rom=rom,expected_sha256=EXPECTED,output=out,identity='simon',mode='hard',frames=8000,policy=policy,replay=None))
 patch=''.join(difflib.unified_diff(text.splitlines(True),corrected.splitlines(True),fromfile='link_simon_ryu_policy.lua (unchanged shared)',tofile=policy.name))
 (out/'controller.patch').write_text(patch,newline='\n')
 review=dict(PREPARED_DO_NOT_RUN=True,native_run=False,ROM_sha256=EXPECTED,policy=str(policy),shared_policy_sha256=sha(origin),generated_policy_sha256=sha(policy),exact_reverse_removal=True,all_original_navigation_chase_attack_backflip_and_double_jump_branches_byte_unchanged=True,no_emulated_writes=True,old_negative=dict(path=str(old/'result.json'),reason=negative['reason'],frames=8000,preserved=True),actual_trace='MaxX406 at814/camera307; last horizontal change1008; X330 through8000, power0. Zero B polls after1000. Repeated A/neutral jumps start on rowY112. ROOT reviewed first-mushroom actor visible at early markers, gone from the selected final view.',cause='Optional first-power fallback returns to bump whenever no pickup is observed and status0; it has no escape from bumping above the already used row. No native whip-freeze or product defect demonstrated.',gate='Only Simon native variant0 Hard world1-1/outdoor, after real pickup observation in this attempt, then no observable pickup in any of the same six actual enemy slots, camera>=307, groundedY112/Yhigh1 and camera<=X<416. Marks only Lua firstPowerDone and clears only owned input latches; original navigation resumes.',source_controls=cases,whole_latch_progression=progression,control_limits='Finite literal gate/ownership models, not execution of the Lua controller or native route. No new source physics or feature change.',scope='One fresh bounded route attempt; first mushroom can be missed, so no whole-powerup acquisition claim. Original8000frame/fullDMA-E3/NMI/IRQ/CHR/5SMC/stack/zero-death/capture guards unchanged.')
 put(out/'controller-review.json',review)
 ready=out/'ready.json';z=json.loads(ready.read_text());z['PREPARED_DO_NOT_RUN']=True;z['controller_revision']=dict(policy_only=True,review=str(out/'controller-review.json'),old_negative_not_replaced=True,first_power_acquisition_claim=False)
 for f in[Path(__file__).resolve(),origin,out/'controller.patch',out/'controller-review.json',old/'ready.json',old/'result.json',old/'trace.csv',old/'inputs.csv',ROOT/'src/roster.s']:
  z['bindings'][str(f)]=sha(f)
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease=True,argv=z['command']));z['bindings'][str(out/'command.json')]=sha(out/'command.json')
 for f,h in z['bindings'].items():assert sha(f)==h,f
 put(ready,z);assert origin.read_bytes()==raw
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),source_model_cases=len(cases),policy_sha256=sha(policy),command=str(out/'command.json'))))
if __name__=='__main__':main()
