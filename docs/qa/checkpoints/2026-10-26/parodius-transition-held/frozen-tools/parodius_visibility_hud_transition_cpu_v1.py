"""Actual linked transition owners plus host-only lifecycle admission checks."""
from pathlib import Path
import argparse,hashlib,json,sys
from parodius_visibility_menu_hint_observer_cpu_v3 import ObservedArena
from parodius_visibility_hud_static_startup_v1 import MOCK
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'


EXPOSE="""
function TRANSITION_TEST_STATE()return{loaded=loadedArea,initial=initialAreaKey,loads=areaLoads,pipes=pipeRequests,vertical=verticalPipeFrames,changes=areaChanges,resets=areaResets,updates=newAreaUpdates,fresh=freshGameUpdates,deaths=deaths,lifestarts=lifeStarts,generation=PARODIUS_LIFECYCLE_GENERATION()}end
"""


def runtime(LuaRuntime,script):
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+"\nL={}\nMOCK_LOGS={};io.open=function(path,mode)if mode=='rb'then return nil end;MOCK_LOGS[path]=MOCK_LOGS[path]or'';return{write=function(self,x)MOCK_LOGS[path]=MOCK_LOGS[path]..x;return self end,flush=function()end,close=function()end}end")
 for line in script.with_name('candidate.lbl').read_text().splitlines():
  f=line.split()
  if len(f)>=3 and f[0]=='al':rt.globals().L[f[2].lstrip('.')]=int(f[1],16)
 # Same chunk: temporary source-only inspection can see lexical locals.
 rt.execute(script.read_text()+EXPOSE)
 rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
 return rt


def trigger(q,name):
 pc=address(q.b,name);q.cpu=NesMPU(memory=q.m,pc=pc);q.sync()
 for fn in q.execs.get(pc,[]):fn(pc)
 q.cpu=None


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['packet','lua-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
 z=json.loads((a.packet/'proof.json').read_text());prep=json.loads((Path(z['profiles'][0]['packet'])/'preparation.json').read_text());script=Path(prep['script']);assert sha(script.with_name('candidate.nes'))==SHA;b=scoped_load(script.with_name('candidate.nes'));rows=[]
 def setup(mode):
  rt=runtime(LuaRuntime,script);q=ObservedArena(b,rt)
  q.put(SelectedCharacter=18,VvVariant=1,CrossoverBehaviorVersion=mode,OperMode=1,OperMode_Task=1,GameEngineSubroutine=3,AreaPointer=0x25,WorldNumber=0,LevelNumber=0,NumberofLives=2,ScreenLeft_PageLoc=0,Player_PageLoc=0,Player_X_Position=96,Player_Y_Position=160,Player_Y_HighPos=1)
  return rt,q
 try:
  for mode in [0]:
   rt,q=setup(mode);q.invoke('GetAreaDataAddrs');t=rt.globals().TRANSITION_TEST_STATE();first=t['loaded']['key'];assert t['loads']==1 and t['loaded']['destination']==0x25 and t['loaded']['area_type']==1
   q.invoke('MoveAllSpritesOffscreen');q.put(OperMode_Task=3,GameEngineSubroutine=8)
   trigger(q,'GameLoop');assert rt.globals().TRANSITION_TEST_STATE()['initial']==first
   # Explicit isolated source setup: this is the value the real ParseRow0e
   # owner may write before entry. It is NOT a native fixture state write.
   q.put(AreaPointer=0xc2);trigger(q,'GameLoop');t=rt.globals().TRANSITION_TEST_STATE();assert t['changes']==0 and t['loaded']['key']==first and t['updates']==0
   rows.append(dict(mode=mode,case='parsed-destination-is-not-loaded-area',loaded_identity=first,raw_destination=0xc2,observed_changes=0,actual_GetAreaDataAddrs_CPU=True,host_GameLoop_callback_only=True))
   q.put(Up_Down_Buttons=4,SavedJoypadBits=4,R0=0x11,R1=0x10,WarpZoneControl=0)
   q.invoke('HandlePipeEntry');assert q.get('GameEngineSubroutine')==3 and q.get('ChangeAreaTimer')==48
   assert rt.globals().TRANSITION_TEST_STATE()['pipes']==1
   before=q.get('Player_Y_Position')
   for i in range(48):q.invoke('VerticalPipeEntry')
   t=rt.globals().TRANSITION_TEST_STATE();assert t['vertical']==48 and q.get('OperMode_Task')==0 and q.get('DisableScreenFlag')!=0 and q.get('Player_Y_Position')==(before+48)&255
   rows.append(dict(mode=mode,case='actual-pipe-request-and48-native-entry-updates',engine=q.get('GameEngineSubroutine'),task=q.get('OperMode_Task'),native_timer=q.get('ChangeAreaTimer'),native_vertical_updates=int(t['vertical']),native_AltEntranceControl=q.get('AltEntranceControl')))
   q.invoke('GetAreaDataAddrs');q.invoke('VvReset');q.invoke('MoveAllSpritesOffscreen');q.invoke('DrawAllMetasprites');q.put(OperMode_Task=3,GameEngineSubroutine=8)
   trigger(q,'GameLoop');t=rt.globals().TRANSITION_TEST_STATE();second=t['loaded']['key'];assert second!=first and t['loaded']['area_type']==2 and t['changes']==1 and t['resets']==1 and t['updates']==1 and t['generation']==1
   q.put(AreaPointer=0x25);trigger(q,'GameLoop');t=rt.globals().TRANSITION_TEST_STATE();assert t['changes']==1 and t['loaded']['key']==second and t['updates']==2
   rows.append(dict(mode=mode,case='real-reload-reset-current-generation-published-owner',before=first,after=second,observed_area_changes=int(t['changes']),native_resets=int(t['resets']),loaded_area_type=int(t['loaded']['area_type']),new_area_observed_updates=int(t['updates']),generation=int(t['generation']),raw_destination_rewrite_does_not_change_identity=True,limits='Actual compiled loader/reset/blank/draw; GameLoop observations are synthetic host callbacks, not real route/reachability. No Buffer2 overlap implied.'))
   rt,q=setup(mode);q.invoke('GetAreaDataAddrs');q.invoke('MoveAllSpritesOffscreen');q.put(OperMode_Task=3,GameEngineSubroutine=8,DisableScreenFlag=0,VvInitialized=0x76,VvLife=2,VvAlive=1,PnInitialized=0x50,InvHudActive=3,InvHudPhysical=140,X5HudChrUpper=0x85)
   trigger(q,'GameLoop');q.invoke('KillPlayer');t=rt.globals().TRANSITION_TEST_STATE()
   assert q.get('GameEngineSubroutine')==11 and q.get('VvAlive')==0 and q.get('VvLife')==255 and q.get('InvHudActive')==0 and q.get('X5HudChrUpper')==1 and t['deaths']==1
   for i in range(120):q.invoke('VvDeathUpdate')
   assert q.get('GameEngineSubroutine')==6 and q.get('TimerControl')==0 and q.get('VvDeathAge')==120
   q.invoke('PlayerLoseLife');assert q.get('NumberofLives')==1 and q.get('OperMode_Task')==0
   q.invoke('VvEnsure');assert q.get('VvLife')==1 and q.get('VvAlive')==1 and q.get('InvHudActive')==0 and q.get('X5HudChrUpper')==1
   q.invoke('PnEnsure');assert q.get('PnInitialized')==0x50 and q.get('PnBombCapturePending')==1 and q.get('PnBombPaletteReady')==0
   rows.append(dict(mode=mode,case='actual-KillPlayer-death120-loss-ensure',one_native_death=True,death_updates=120,native_lives_after=q.get('NumberofLives'),new_life_capture_pending=q.get('PnBombCapturePending'),new_life_palette_ready=q.get('PnBombPaletteReady'),HUD_inactive_until_real_publication=True,limits='Isolated legal CPU inputs; functions execute for real, native terrain/controller contact and fresh45 displayed updates remain unrun.'))
  rt,q=setup(1);q.invoke('GetAreaDataAddrs');q.invoke('MoveAllSpritesOffscreen');q.put(OperMode_Task=3,GameEngineSubroutine=8)
  try:trigger(q,'GameLoop')
  except Exception as ex:assert 'Lifecycle numeric mode readback'in str(ex)
  else:raise AssertionError('Wrong mode bypassed frozen numeric0 fixture')
  rows.append(dict(mode=1,case='wrong-mode-for-frozen-numeric0-fixture',rejected=True,unchanged_mode_guard=True))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),completed=rows),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');proof=dict(passed=True,native_run=False,ROM_sha256=SHA,cases=len(rows),cases_sha256=sha(a.output/'cases.json'),preparation_sha256=sha(a.packet/'proof.json'),tool_sha256=sha(Path(__file__)),limits='Synthetic isolated actual-CPU owners and host callbacks only. No Mesen, natural death/pipe reachability, actual PPU/IRQ/DMC timing or Buffer2 hold/catch-up verdict. Source-only mode0/1 values do not constitute native Easy/Hard coverage.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
