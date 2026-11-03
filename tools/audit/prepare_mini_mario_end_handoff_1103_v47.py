"""Read-only native end-seam evidence over exact delivered8daf/frozen43 controls."""
from pathlib import Path
import argparse,json,sys
import prepare_mini_mario_native_smoke_1103_v25 as S
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua
O=R/'build/mini-mario-end-handoff-1103-v47'
SOURCE=R/'build/mini-mario-native-packets-1103-v43/full43/controller.lua'
PIN='8daf59cc958e2a3a645882ea53c6bd75e9a7c641793054f8ce534358f369a7d7'

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,default=R/'build/mini-mario-candidate-root-1103-v44/mini-private.nes');a=p.parse_args();O.mkdir(exist_ok=True)
    ready=json.loads(SOURCE.with_name('ready.json').read_text());assert ready['ROM_sha256']==PIN and sha(SOURCE)==ready['bindings'][str(SOURCE)] and sha(a.rom)==PIN
    text=SOURCE.read_text();G=S.labels(S.GLOBALS)
    fields=['OperMode','OperMode_Task','GameEngineSubroutine','SelectedCharacter','MarioVariant',
        'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State',
        'Player_X_Speed','Player_Y_Speed','Player_Y_MoveForce','Player_CollisionBits','NumberofLives',
        'WorldNumber','LevelNumber','ScreenLeft_X_Pos','ScreenLeft_PageLoc','ScrollLock',
        'FlagpoleCollisionYPos','FlagpoleFNum_Y_Pos','FlagpoleFNum_YMFDummy','FlagpoleScore',
        'FlagpoleMusicFlag','FlagpoleSoundQueue','StarFlagTaskControl','TimerControl',
        'GameTimerCtrlTimer','GameTimerExpiredFlag','GameTimerSetting','EventMusicBuffer',
        'EventMusicQueue','AreaMusicBuffer','AreaMusicQueue','CurrentBank','CurrentBankC','FrameCounter']
    aliases={n:G[n]for n in fields+['GameTimerDisplay']}
    anchor='-- Controller inputs only.';assert text.count(anchor)==1
    text=text.replace(anchor,'for k,v in pairs('+lua(aliases)+')do L[k]=v end\nC.max_frames=9500\n'+anchor)
    old='local done,lastEpoch,pending,last=nil,nil,nil,nil';assert text.count(old)==1
    text=text.replace(old,old+"\nlocal native_snapshot=nil\nlocal end_native={started=false,samples={}}")
    old='script_RAM_writes=false,controller_only=true';assert text.count(old)==1
    text=text.replace(old,"native_end_handoff=end_native,terminal_native=native_snapshot and native_snapshot()or nil,"+old)
    old='if not ok then result(false,tostring(e))';assert text.count(old)==1
    text=text.replace(old,"if not ok then if native_snapshot then end_native.terminal=native_snapshot()end;if shots<2 then local f=io.open(OUTPUT..'mini-end-terminal.png','wb');if f then f:write(emu.takeScreenshot());f:close();shots=shots+1 end end;result(false,tostring(e))")
    # The source CSV and every original movement/hardware/landing assertion are
    # unchanged. Only the previously unobserved native end phase is added.
    field_list=lua(fields)
    observer="""
local native_fields=FIELD_LIST
local end_csv=assert(io.open(OUTPUT..'native-end.csv','w'))
end_csv:write('frame,source,Main,worldX,Ready,sourceX16,sourceY16,sourceCurrent,sourceQueued,gameTimer,'..table.concat(native_fields,',')..'\\n')
native_snapshot=function()
 local q={frame=frame,source_updates=updates,completed_Main=mains}
 for _,n in ipairs(native_fields)do q[n]=r(n)end
 q.worldX=q.Player_X_Position+256*q.Player_PageLoc
 q.Ready=ram(0xc300);q.sourceX16=word(0xc250);q.sourceY16=word(0xc252)
 q.sourceCurrent=ram(0xc240);q.sourceQueued=ram(0xc228)
 q.gameTimer={read(L.GameTimerDisplay),read(L.GameTimerDisplay+1),read(L.GameTimerDisplay+2)}
 return q
end
local last_end_log,last_end_signature,last_end_change,last_major=-1000,nil,0,nil
local function native_end_sample(q,why)
 if #end_native.samples>=48 then return end
 q.reason=why;end_native.samples[#end_native.samples+1]=q
 local values={q.frame,q.source_updates,q.completed_Main,q.worldX,q.Ready,q.sourceX16,q.sourceY16,q.sourceCurrent,q.sourceQueued,table.concat(q.gameTimer,'')}
 for _,n in ipairs(native_fields)do values[#values+1]=q[n]end
 end_csv:write(table.concat(values,',')..'\\n');end_csv:flush();last_end_log=frame
end
emu.addEventCallback(guard(function()
 local q=native_snapshot()
 -- Same controller phases and inputs. Start only at the measured flag/castle
 -- approach after the source path has actually reached worldX>3000.
 local nearend=(q.worldX>3000 or(q.sourceX16>3000*16))
 local changed=q.GameEngineSubroutine~=8 or q.OperMode~=1 or q.OperMode_Task~=3
  or q.SelectedCharacter~=41 or q.WorldNumber~=0 or q.LevelNumber~=0
 if not end_native.started and phase=='fullstage'and nearend and changed then
  end_native.started=true;end_native.first_frame=frame;end_native.first=q
  native_end_sample(q,'first-native-end-transition')
 end
 if not end_native.started then return end
 local sig={};for _,n in ipairs(native_fields)do
  if n~='CurrentBank'and n~='CurrentBankC'and n~='FrameCounter'then sig[#sig+1]=q[n]end
 end
 for _,v in ipairs(q.gameTimer)do sig[#sig+1]=v end
 local signature=table.concat(sig,':')
 if signature~=last_end_signature then last_end_signature=signature;last_end_change=frame end
 end_native.stable_native_frames=frame-last_end_change
 end_native.elapsed_frames=frame-end_native.first_frame
 local major=table.concat({q.OperMode,q.OperMode_Task,q.GameEngineSubroutine,q.SelectedCharacter,q.MarioVariant,q.WorldNumber,q.LevelNumber,q.StarFlagTaskControl},':')
 if major~=last_major or frame-last_end_log>=60 then native_end_sample(q,major~=last_major and'native-phase-change'or'sixty-frame-native-state');last_major=major end
 end_native.terminal=q
 if end_native.elapsed_frames>=1200 then
  native_end_sample(q,'bounded-native-end-seam')
  error('End-handoff diagnostic stopped1200physicalframes after actual native end transition; inspect recorded native state before classifying cause')
 end
end),emu.eventType.endFrame)
""".replace('FIELD_LIST',field_list)
    text+='\n'+observer
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    deps=[Path(x)for x in ready['bindings']if Path(x)not in [SOURCE,SOURCE.with_name('run.py')]]
    prepare(O/'native',a.rom,text,[*deps,Path(__file__),SOURCE,R/'docs/qa/continuation-current.json'],expected=PIN,timeout=240,allow_interactive=True,
        scope='Read-only end-handoff diagnostic on delivered8daf/exactfrozen43controls. All movement/CHR/OAM/bbox/no-life-loss/7crossing assertions unchanged. After true native end transition nearflagpole, record authoritative mode/task/engine/identity/nativeXY/Ready/level/flagpole/collision/timers/music every60frames +phasechanges, stop1200physicalframes later(global9500). Menu+terminal≤2PNGs; one boundednativeCSV +aggregateJSON, no video/RAM/ability/statewrites.43negative preserved; no cause/fullclear inferred from sourceX alone.')

if __name__=='__main__':main()
