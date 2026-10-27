"""Prepare one controller-only LanceHard pipe-exit correction; never launch."""
from pathlib import Path
from types import SimpleNamespace
import difflib,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from current_roster_compact_11_v1 import prepare
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
EXPECTED='4a0394b0892e6c54940856791e44bcbe9fe4e469047aca3982c3f59112a61b8b'
INSERT=''' -- LanceHard only: the third pipe has continuous floor below its exit.
 -- Walk off rather than treating air8px below its top as a floor gap.
 -- Reset only this controller's own jump latch; never game motion/state.
 if ROSTER_CONFIG.name=='lance'and ROSTER_CONFIG.mode_value==1
    and c.char==3 and c.variant==1 and c.world==0 and c.level==0
    and c.x>=748 and c.x<820 and c.yHigh==1 and c.y<176 then
  holdA=0;cooldown=0
  return {right=true,b=c.poll%12<5,a=false}
 end
'''

def main():
 old=R/'build/verification/compact-next-lance-coalesce-hard-v1';out=R/'build/verification/compact-next-lance-coalesce-hard-v2'
 assert not out.exists();origin=R/'tools/playthroughs/roster_samus_contra.lua';policy=R/'tools/playthroughs/current_roster_lance_pipe_exit_v2.lua'
 assert not policy.exists()
 previous=json.loads((old/'ready.json').read_text());failed=json.loads((old/'result.json').read_text())
 assert previous['ROM_sha256']==failed['ROM_sha256']==EXPECTED and not failed['passed'] and failed['frames']==1859
 assert failed['reason']=='Zero-death 1-1 route' and sha(origin)==previous['bindings'][str(origin)]
 raw=origin.read_bytes();text=raw.decode();nl='\r\n'if b'\r\n'in raw else'\n';needle=' local e=c.enemy()'+nl;insert=INSERT.replace('\n',nl);assert text.count(needle)==1
 corrected=text.replace(needle,needle+insert)
 assert corrected.replace(insert,'',1)==text
 assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset|setInput)\s*\(',corrected)
 assert 'io.open'not in corrected and 'c.r('not in INSERT and 'emu.'not in INSERT
 # Exact literal gate checked by finite negative boundary models. This is a
 # source/controller-scope check, not an executed Lua/gameplay qualification.
 assert "c.char==3 and c.variant==1 and c.world==0 and c.level==0"in INSERT
 assert "c.x>=748 and c.x<820 and c.yHigh==1 and c.y<176"in INSERT
 def gate(s):return s['name']=='lance'and s['mode']==1 and s['char']==3 and s['variant']==1 and s['world']==0 and s['level']==0 and 748<=s['x']<820 and s['yHigh']==1 and s['y']<176
 base=dict(name='lance',mode=1,char=3,variant=1,world=0,level=0,x=754,yHigh=1,y=112)
 controls=[]
 for k,values in dict(name=['bill','samus','lance'],mode=[0,1],char=[2,3,5],variant=[0,1],world=[0,1],level=[0,1,2],x=[747,748,754,819,820],yHigh=[0,1,2],y=[38,112,175,176,177]).items():
  for v in values:
   s=dict(base);s[k]=v;want=(k=='name'and v=='lance')or(k=='mode'and v==1)or(k=='char'and v==3)or(k=='variant'and v==1)or(k=='world'and v==0)or(k=='level'and v==0)or(k=='x'and 748<=v<820)or(k=='yHigh'and v==1)or(k=='y'and v<176)
   assert gate(s)==want;controls.append(dict(change=k,value=v,admitted=gate(s)))
 # Own latches must clear BEFORE return, so the old finish() cannot secretly
 # hold/restart A. The original finish and nav bytes are otherwise untouched.
 assert INSERT.index('holdA=0;cooldown=0')<INSERT.index('return {right=true')
 policy.write_bytes(corrected.encode())
 rom=R/'build/smb-crossover-mmc5-expanded.nes';assert sha(rom)==EXPECTED
 prepare(SimpleNamespace(rom=rom,expected_sha256=EXPECTED,output=out,identity='lance',mode='hard',frames=8000,policy=policy,replay=None))
 patch=''.join(difflib.unified_diff(text.splitlines(True),corrected.splitlines(True),fromfile='roster_samus_contra.lua (unchanged shared)',tofile=policy.name))
 (out/'controller.patch').write_text(patch,newline='\n')
 first=next(i+1 for i,s in enumerate(corrected.splitlines())if s==' -- LanceHard only: the third pipe has continuous floor below its exit.')
 review=dict(PREPARED_DO_NOT_RUN=True,native_run=False,ROM_sha256=EXPECTED,policy=str(policy),policy_sha256=sha(policy),changed_policy_lines=[first,first+len(INSERT.splitlines())-1],inserted_lines=len(INSERT.splitlines()),reverse_removal_byte_exact=True,all_original_branches_finish_nav_unchanged=True,scope_controls=controls,control_scope='Literal gate/ownership/negative-boundary model only; no Lua runtime or native controller outcome claimed.',old_failure=dict(directory=str(old),frame=1859,reason=failed['reason'],preserved=True),actual_observation='Third-pipe landing at1741 x753/y112, newA+Right+B1742; continued airborneRight+Down into two visibleGoombas, contact death1859 x849/y166. Exact enemy slot/contactPC unrecorded. Counterfactual walkoff drop is prediction only.',motion_source='roster.s ImmediateInput keeps airborne neutralVX, so the correction walksRight off the pipe instead of pretending neutral can stop inair. Bill/Lance release does not clamp the jump (Release clamp is Link-only). Grounded crouch/fire policy takes over whenY176 is reached.',resource_or_motion_writes=False,cheats=False,guards='Original shared current_roster_compact_11_v1.lua unchanged: real menu/variant/mode/physicalmushroom/zero-death/full256DMA-E3/CHR/NMI/IRQ/5SMC/SP/render deadline. 8000physicalframes,512MiBcapture,2GB/64-file central cap,8offlineimages maximum.',remaining='One new finite controller attempt requires ROOT native lease. No existing Bill2082 or Lancev1/native image results transfer.')
 put(out/'controller-review.json',review)
 ready=out/'ready.json';z=json.loads(ready.read_text());z['PREPARED_DO_NOT_RUN']=True;z['controller_revision']=dict(review=str(out/'controller-review.json'),sha256=sha(out/'controller-review.json'),policy_only=True,old_negative_not_replaced=True)
 for f in[Path(__file__).resolve(),origin,out/'controller.patch',out/'controller-review.json',old/'ready.json',old/'result.json',old/'trace.csv',old/'inputs.csv',old/'captures-index.jsonl',old/'captures.nesppuv1',R/'src/roster.s',R/'src/guest_body_contact.s']:
  z['bindings'][str(f)]=sha(f)
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease=True,argv=z['command']));z['bindings'][str(out/'command.json')]=sha(out/'command.json')
 for f,h in z['bindings'].items():assert sha(f)==h,f
 put(ready,z);assert origin.read_bytes()==raw
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),policy=str(policy),policy_sha256=sha(policy),changed_lines=review['changed_policy_lines'],negative_scope_cases=len(controls),command=str(out/'command.json'))))
if __name__=='__main__':main()
