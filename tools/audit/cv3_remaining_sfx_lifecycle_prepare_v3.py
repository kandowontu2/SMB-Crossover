"""Ten focused preseed-only lifecycle fixtures; fixed startup observer, NO launch."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PROFILES=[('mixed-easy','mixed',0,1,2,0x15,'sub',[2]),('mixed-hard','mixed',1,1,2,0x15,'sub',[2]),('priority-hard','priority',1,2,2,0x21,'sub',[4,5]),('pause-hard','pause',1,2,2,0x21,'sub',[4]),('death-easy','death',0,3,0,0x2f,'bat',[7]),('death-hard','death',1,3,0,0x2f,'bat',[7]),('scene-hard','scene',1,3,0,0x2f,'bat',[7]),('pressure-fireball-easy','pressure',0,3,0,0x1f,'fireball',[6]),('pressure-fireball-hard','pressure',1,3,0,0x1f,'fireball',[6]),('pressure-idle-hard','pressure',1,3,0,0,'idle',[])]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def section(s,lo,hi,new):
 assert s.count(lo)==s.count(hi)==1,(lo,hi);i=s.index(lo);j=s.index(hi,i);return s[:i]+new+s[j:]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
 common=Path(__file__).with_name('cv3_remaining_sfx_lifecycle_common_v2.lua').read_text();newqueue=Path(__file__).with_name('cv3_remaining_sfx_lifecycle_queue_v1.lua').read_text();oldqueue=Path(__file__).with_name('cv3_remaining_sfx_steady_native_v1.lua').read_text()
 for version in['baseline','candidate']:
  parent=D/('cv3-remaining-static-observer-v1/replay-packet-v1/baseline50b'if version=='baseline'else'cv3-remaining-steady-native-v2/hard-ice');rom=D/('cv3-remaining-current50b-v1/baseline.nes'if version=='baseline'else'cv3-remaining-steady-v3/candidate.nes');b=load(rom);labels=qualified(rom)
  assert sha(rom)==('50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'if version=='baseline'else'eaa36e56c09e87f58a85db312894f14bfd7fb5838be139fc508ae6121c9e0732')
  def hook(n):
   if'::'in n:
    proc,leaf=n.split('::');pc=labels[(proc,leaf)];off=location(b,proc)+pc-address(b,proc)
   else:pc=address(b,n);off=location(b,n)
   return dict(address=pc,physical_bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]),genuine_source_symbol=n)
  original=(parent/'run.lua').read_text().split('\n',1)[1]
  for name,profile,mode,variant,sub,event,kind,cues in PROFILES:
   cfg=json.loads((parent/'configuration.json').read_text());cfg.update(mode=mode,variant=variant,lifecycle=1,expected_cue=cues[0]if cues else 0,allowed_cues={str(v):1 for v in cues},cases=[dict(name=name,profile=profile,mode=mode,sub=sub,event=event,kind=kind,updates=240 if profile=='pressure'else 140)])
   for n in['Cv3CollectPickupGate','NativeRareHandlePipeEntryCore','GuestAudioNativeFlush','GuestAudioFinish::MixedChannels']:cfg['hooks'][n]=hook(n)
   if version=='candidate':
    for n in['Cv3FxMusicInit','Cv3FxTick','Cv3FxMuteGate']:cfg['hooks'][n]=hook(n)
   for n in['RgAudioSilenced','Enemy_BoundBoxCtrl','PowerUpType','InvPickup','InvPickupOwner','Cv3PickupVariant','InvRisePhase','AreaPointer','AreaType','WarpZoneControl','ChangeAreaTimer','GuestMixMask','GuestMixChanged','GuestNativeApu','GuestApuLast','GuestNativeDirty','GuestFxApu','GuestFxDirty']:cfg['ram'][n]=address(b,n)
   text=original
   if version=='candidate':assert text.count(oldqueue)==1;text=text.replace(oldqueue,newqueue,1)
   old="local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end";new="local lifeStaging=false\nlocal w=function(n,v,i)assert(lifeStaging,'No postseed fixture outcome/RAM writes');emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end";assert text.count(old)==1;text=text.replace(old,new,1)
   # Replace the old controlled-sentinel scene observation. Its immediate
   # ID-clear expectation belongs to a different (rejected) protocol.
   lo="emu.addMemoryCallback(function()\n if not entered or done or not valid('Cv3NoiseSceneReset')or";hi="emu.addMemoryCallback(function()\n if not entered or done or not valid('Cv3SpawnAudioType')then";text=section(text,lo,hi,'')
   assert text.count('local timing=assert')==1;text=text.replace('local timing=assert',common+'\nlocal timing=assert',1)
   assert text.count('local function seed(q)\n')==1;text=text.replace('local function seed(q)\n','local function seed(q)\n lifeStaging=true\n',1)
   if version=='candidate':needle='\n queueStartCase()\n';assert text.count(needle)==1;text=text.replace(needle,'\n lifeStage(q)\n queueStartCase()\n lifeStaging=false\n',1)
   else:needle=" print('CV3_AUDIO_SEED '";assert text.count(needle)==1;text=text.replace(needle," lifeStage(q)\n lifeStaging=false\n"+needle,1)
   finish='''local function finishCase()
 lifeFinish()
'''+(' queueFinishCase()\n'if version=='candidate'else'')+''' local f=assert(io.open(OUTPUT..'last-case.json','w'));f:write(json(current));f:close();capture('case-end')
 assert(current.modeReadback==C.mode,'Actual cold numeric mode retained')
 current.durationUpdates=age;results[#results+1]=current
end
'''
   text=section(text,'local function finishCase()\n',"emu.addMemoryCallback(function()\n if done or not valid('PauseSkip')",finish)
   # No periodic respawn, health rewrite, subweapon rewrite or LastArea flip.
   text=section(text," if current.q.profile=='pressure'and age%24==0 then",' if age>=C.cases[index].updates then','')
   lo="  if current.firstActionWall and wall>=current.firstActionWall+6 and current.q.profile=='scene'";hi='  current.frames=current.frames+1';text=section(text,lo,hi,'')
   lo=' local b={}\n if not done then\n  local q=current.q;local pressed=';hi=' emu.setInput(b,0)';text=section(text,lo,hi,' local b={}\n if not done then b=lifeInput()end\n')
   assert text.count('dmaBus:close()')==1;text=text.replace('dmaBus:close()','dmaBus:close();lifeLog:close()',1)
   assert "w('Cv3LastArea',r("not in text and "age==32 then w('Cv3Subweapon'"not in text and 'age%24==0 then for i=0,5 do w('not in text
   assert text.endswith('installStaticReturns()\n')and text.count('emu.removeMemoryCallback')==0
   dest=a.output/version/name;dest.mkdir(parents=True);script=dest/'run.lua';script.write_text('CV3_REMAINING_NATIVE_CONFIG='+lua(cfg)+'\n'+text,encoding='utf-8',newline='\n');(dest/'configuration.json').write_text(json.dumps(cfg,indent=2)+'\n');shutil.copyfile(rom.with_suffix('.lbl'),dest/'candidate.lbl')
   record=dict(prepared=True,native_executed=False,version=version,name=name,ROM=str(rom),ROM_sha256=sha(rom),script=str(script),script_sha256=sha(script),configuration_sha256=sha(dest/'configuration.json'),parent_script_sha256=sha(parent/'run.lua'),parent_configuration_sha256=sha(parent/'configuration.json'),literal_original_static_DMACHR_IRQ_SMC_bank_stack_APU_DMC_guards_retained=True,all_game_RAM_writes_guarded_by_initial_seed=True,no_postseed_health_weapon_scene_enemy_respawn_writes=True,controller_profile=cfg['cases'][0],source_oracle_expected_cues=cues,source_original_ids={str(c):{2:0x15,4:0x21,5:0x1e,6:0x1f,7:0x2f}[c]for c in cues},scene_scope='Isolated original10/11 pipe topology and authentic1-1 destinationC2 beforeseed, real Down+A/pipe/loader thereafter; not traversing1-1 to its pipe.',scope='SOURCE PREPARATION ONLY. Need full Lua static/actual source-owner replay, original oracle qualification, input/environment freeze and explicit native grant. No outcome/cadence/adoption claim.',tool_sha256=sha(__file__));(dest/'preparation.json').write_text(json.dumps(record,indent=2)+'\n');rows.append(record)
 (a.output/'prepared.json').write_text(json.dumps(dict(prepared=True,native_executed=False,profiles=10,fixtures=20,rows=rows,tools={str(p0):sha(p0)for p0 in[Path(__file__),Path(__file__).with_name('cv3_remaining_sfx_lifecycle_common_v2.lua'),Path(__file__).with_name('cv3_remaining_sfx_lifecycle_queue_v1.lua')]}),indent=2)+'\n');print(json.dumps(dict(prepared=True,native_executed=False,profiles=10,fixtures=20),indent=2))
if __name__=='__main__':main()
