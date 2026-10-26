"""One finite same-input current3b timing companion; prepare or explicitly granted run."""
from pathlib import Path
import argparse,copy,csv,json,shutil,subprocess,sys,traceback
from smb3_host_current3b_cpu_v1 import D,R,sha,put
from smb3_host_current3b_freeze_v1 import dependencies
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
from mario_powerups_current3cee_static_v2 import symbols,runtime
from final_item_abilities_current731_prepare_v1 import protocol

PILOT=D/'smb3-host-current3b-native-ready-v1'
BASE=D/'root-current-roster-composition-v1'
def hook(b,name,size=8,delta=0):
 at=location(b,name)+delta;pc=address(b,name)+delta;bank=(at-16)//8192
 return dict(pc=pc,bank=bank,banks=[bank],resident=bank==127,bytes=list(b['raw'][at:at+size]))
AUDIO='''
local C=BASELINE_AUDIO_CONFIG
local function bank(a)local q=emu.convertAddress(a);return q and q.address//8192 or -1 end
local f=assert(io.open(ROSTER_CONFIG.out..'baseline-whole-audio.jsonl','w'))
local pending=nil
emu.addMemoryCallback(function()
 assert(bank(C.pc)==127,'Actual baseline resident AudioUpdate bank127')
 for i,v in ipairs(C.bytes)do assert(emu.read(C.pc+i-1,emu.memType.nesDebug)==v,'Actual baseline AudioUpdate bytes')end
 assert(not pending,'No nested baselineAudioUpdate')
 local s=emu.getState();local sp=s['cpu.sp'];local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 pending={pc=pc,sp=(sp+2)%256,bank=bank(pc),cycle=s['cpu.cycleCount'],frame=s['ppu.frameCount']}
end,emu.callbackType.exec,C.pc)
BASELINE_INSTALL_AUDIO_RETURN=function()
 emu.addMemoryCallback(function(pc)
  if not pending then return end;local s=emu.getState();local q=pending
  if pc~=q.pc or s['cpu.sp']~=q.sp or bank(pc)~=q.bank then return end
  pending=nil;f:write(string.format('{"frame":%d,"cycles":%d,"returnBank":%d}\\n',q.frame,s['cpu.cycleCount']-q.cycle,q.bank));f:flush()
 end,emu.callbackType.exec,0,65535)
end
local stop=emu.stop;emu.stop=function(code)f:close();stop(code)end
'''

def prepare(out):
 out.mkdir(parents=True,exist_ok=False);old=json.loads((PILOT/'readiness.json').read_text());assert sha(BASE/'candidate.nes')=='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
 for f,h in old['bindings'].items():assert sha(f)==h,f
 b=scoped_load(BASE/'candidate.nes');cfgs=json.loads((PILOT/'configuration.json').read_text());folder=out/'native';folder.mkdir();(folder/'frames').mkdir()
 cfg=copy.deepcopy(cfgs['roster']);cfg.update(out=folder.as_posix()+'/',policy=(folder/'policy.lua').as_posix(),audit=(folder/'audit.lua').as_posix(),replay=(PILOT/'native/inputs.csv').as_posix())
 # Input is an actual cold natural-controller recording, not synthetic state
 # or a different-phase old playthrough. Poll AND physical-frame equality stay
 # literal in the unchanged harness. Any mismatch is a retained failure.
 for n in ['harness.lua','audit.lua','native-guard.lua']:shutil.copyfile(PILOT/'native'/n,folder/n)
 policy=(PILOT/'native/policy.lua').read_text();body=policy.split('\n',1)[1];(folder/'policy.lua').write_text('dofile('+lua((folder/'native-guard.lua').as_posix())+')\n'+body,encoding='utf-8',newline='\n')
 render=copy.deepcopy(cfgs['render']);render['ROM_sha256']=sha(BASE/'candidate.nes')
 for n,h in render['hooks'].items():
  source={'NmiEntry':'NonMaskableInterrupt','NmiReturn':'NonMaskableInterrupt','IrqEntry':'IrqScrollSplit','IrqReturn':'IrqScrollSplit','GameLoop':'GameLoop','GameLoopReturn':'GameLoop','DrawAll':'DrawAllMetasprites'}[n]
  offset=int(b['syms'][source]['size'],0)-1 if n.endswith('Return')else 0;render['hooks'][n]=hook(b,source,len(h['bytes']),offset)
  render['hooks'][n]['banks']=[render['hooks'][n]['bank']]
 render['dma_protocol']=protocol(b)
 # Same generated common hardware observer.3b has no SMB3 resident70/97
 # clones, so permit ONLY its genuine127. Never add fake aliases to baseline.
 shutil.copyfile(PILOT/'render-observer.lua',out/'render-observer.lua')
 audio=hook(b,'AudioUpdate');audio={k:audio[k]for k in ['pc','bytes']};put(out/'configuration.json',dict(roster=cfg,render=render,audio=audio))
 script='ROSTER_CONFIG='+lua(cfg)+'\nSMB3_RENDER_OBSERVER='+lua(render)+'\nSMB3_RENDER_OBSERVER.residentAlias=function(b)return b==127 end\nBASELINE_AUDIO_CONFIG='+lua(audio)+'\ndofile('+lua((out/'render-observer.lua').as_posix())+')\n'+AUDIO+'\ndofile('+lua((folder/'harness.lua').as_posix())+')\nassert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\nBASELINE_INSTALL_AUDIO_RETURN()\n';(out/'run.lua').write_text(script,encoding='utf-8',newline='\n')
 env=old['environment']
 for n in ['emulator','core','worker_settings','user_settings']:assert sha(env[n])==env[n+'_sha256'],n
 put(out/'environment.json',env)
 sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
 labels,banks=symbols(b,BASE/'candidate.nes');rt=runtime(LuaRuntime,labels,banks);rt.execute("state['cpu.ps']=32;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end")
 # Mock io.lines supplies the first four genuine saved entries; no native
 # replay or source-source comparison is inferred from this startup example.
 rt.execute("io.lines=function(path)local lines={'poll,frame,mask','1,1,0','2,2,0','3,3,0','4,4,0'};local i=0;return function()i=i+1;return lines[i]end end")
 rt.execute(script);count=rt.eval('#callbacks');rt.execute("emu.addMemoryCallback=function()error('Runtime registration')end;emu.removeMemoryCallback=function()error('Runtime removal')end")
 for frame in range(1,5):rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.endFrame);runevents(emu.eventType.inputPolled)")
 assert rt.eval('#callbacks')==count and rt.eval('inputCalls')==4
 put(out/'static-controls.json',dict(passed=True,native_run=False,generated_startup_loaded=True,mocked_recorded_input_entries=4,runtime_registration=0,callbacks=count,common_render_observer_byteexact_to_pilot=True,common_harness_audit_guard_byteexact=True,original_policy_body_exact=True,new_music_hooks_omitted=True,actual_replay_input_sha256=sha(PILOT/'native/inputs.csv'),literal_poll_frame_checks_retained=True))
 cmd=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),'--emulator',env['emulator'],str(out/'run.lua'),str(BASE/'candidate.nes'),'--timeout','180']+['--option='+v for v in env['actual_command_overrides']]
 manifest=json.loads((BASE/'source-manifest.json').read_text());files={BASE/'source'/n for n in manifest}|{BASE/'candidate.nes',BASE/'candidate.dbg',BASE/'candidate.lbl',BASE/'source-manifest.json',PILOT/'readiness.json',PILOT/'native-final-freeze-v1/proof.json',PILOT/'native-post-v2/proof.json',PILOT/'native/inputs.csv',PILOT/'native/trace.csv',PILOT/'native/actual-ppu-index.csv',PILOT/'native/route-observation.jsonl'}
 files|={PILOT/'native'/n for n in ['harness.lua','policy.lua','audit.lua','native-guard.lua']}|{PILOT/'render-observer.lua'}|set(dependencies([Path(__file__),R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py']))|{Path(env[n])for n in ['emulator','core','worker_settings','user_settings']}|{f for f in out.rglob('*')if f.is_file()}
 for n,h in manifest.items():assert sha(BASE/'source'/n)==h,n
 bindings={str(f.resolve()):sha(f)for f in sorted(files,key=str)}
 put(out/'readiness.json',dict(passed=True,status='PREPARE_DO_NOT_RUN',native_run=False,native_granted=False,baseline_ROM_sha256=sha(BASE/'candidate.nes'),candidate_ROM_sha256=old['ROM_sha256'],native_command=cmd,bindings=bindings,environment=env,maximum_launches=1,native_workers=1,timeout_seconds=180,maximum_PPU_frames=1200,automatic_retries=0,stop_first_failure=True,mechanics='One exact actual1199-poll/1200PPU input stream from the genuine7469 natural-menu/M3MarioEasy opening. Byte-identical controller body is still loaded; replay supplies literal sameinput and existing poll/frame assertions. Common render/harness/audit/motion preserved, real127hooks rebound; source-only new music requirements omitted.',comparison='After real baseline success compare literal perPPU masks and actual cumulative updates/draws/commits/costs. Candidate deficiencies remain explicit; baseline component success alone cannot promote music.'))
 command=[sys.executable,'-B',str(Path(__file__).resolve()),'--run',str(out),'--expected-readiness-sha256',sha(out/'readiness.json'),'--native-grant'];put(out/'command.json',dict(command=command,not_executed=True,explicit_ROOT_grant_required=True));print(json.dumps(dict(passed=True,native_run=False,bindings=len(bindings),readiness_sha256=sha(out/'readiness.json'),command_sha256=sha(out/'command.json'))))

def run(packet,expected,granted):
 assert granted and sha(packet/'readiness.json')==expected;ready=json.loads((packet/'readiness.json').read_text())
 for f,h in ready['bindings'].items():assert sha(f)==h,f
 g=json.loads((packet/'ROOT-grant.json').read_text());assert g['readiness_sha256']==expected and g['maximum_launches']==1
 marker=packet/'ONE-SHOT-USED.json';assert not marker.exists();put(marker,dict(consumed=True,readiness_sha256=expected,retry=False))
 try:
  r=subprocess.run(ready['native_command'],cwd=R,capture_output=True,text=True,timeout=210);put(packet/'launch-result.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,'Native firstfailure retained'
  f=packet/'native';result=json.loads((f/'result.json').read_text());render=json.loads((f/'render-observation-result.json').read_text());body=json.loads((f/'chr-commit.json').read_text());motion=json.loads((f/'completed-loop-motion.json').read_text());assert result['component_complete']and result['frames']==1200 and result['deaths']==0 and render['passed']and body['passed']and motion['passed']
  assert(f/'inputs.csv').read_bytes()==(PILOT/'native/inputs.csv').read_bytes(),'Actual same perPPU/poll input required'
  candidate=list(csv.DictReader((PILOT/'native/actual-ppu-index.csv').open()));baseline=list(csv.DictReader((f/'actual-ppu-index.csv').open()));assert len(candidate)==len(baseline)==1200
  delta=[]
  for x,y in zip(candidate,baseline):
   assert x['ordinal']==y['ordinal']and x['ppuFrame']==y['ppuFrame'];delta.append(dict(ordinal=int(x['ordinal']),ppuFrame=int(x['ppuFrame']),candidate_minus_baseline_updates=int(x['updates'])-int(y['updates']),candidate_minus_baseline_draws=int(x['draws'])-int(y['draws']),candidate_minus_baseline_commits=int(x['commits'])-int(y['commits'])))
  proof=dict(passed=True,native_run=True,baseline_ROM_sha256=ready['baseline_ROM_sha256'],candidate_ROM_sha256=ready['candidate_ROM_sha256'],same_input_stream_byteexact=True,render=render,result=result,body=body,motion=motion,per_PPU_differences=delta,draw_deficit_prefixes=[q for q in delta if q['candidate_minus_baseline_draws']<0],final_difference=delta[-1],music_cadence_accepted=False,limits='Baseline component pass, not music adoption. Candidate draw/update differences remain literal, not relabeled by aggregate. Native cost/physicalPPU raw evidence retained.')
  put(packet/'proof.json',proof);print(json.dumps(dict(passed=True,draw_deficit_prefixes=len(proof['draw_deficit_prefixes']),final=delta[-1])))
 except Exception as e:put(packet/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),retry=False));raise
def main():
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--run',type=Path);p.add_argument('--expected-readiness-sha256');p.add_argument('--native-grant',action='store_true');a=p.parse_args();prepare(a.output.resolve())if a.output else run(a.run.resolve(),a.expected_readiness_sha256,a.native_grant)
if __name__=='__main__':main()
