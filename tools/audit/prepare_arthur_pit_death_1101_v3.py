"""Controller-earned first-pit death and native life-restart observation."""
from pathlib import Path
import prepare_arthur_camera_1101_v3 as P
from prepare_selected_native_packet_v1 import prepare,sha


def controller():
 ref=P.P.R/'tools/reference/arthur_full11_native_1101_v3.lua';text=ref.read_text()
 text=text.replace('local jumps=0','''local jumps=0
local deathStart=nil
local restarted=nil
local restartX=nil
local maximumDeathAge=0
local deathCalls={}
local function bindDeath(name)
 local pc=assert(L[name],name);local bank=assert(B[name],name)|128
 emu.addMemoryCallback(function()
  local mapped=pc>=0xe000 and 255 or r(pc>=0xc000 and 'CurrentBankC' or 'CurrentBank')
  if phase=='play' and mapped==bank then deathCalls[name]=(deathCalls[name]or 0)+1 end
 end,emu.callbackType.exec,pc)
end
''')
 # bindDeath closes over r, declared later, so move that helper below r.
 a=text.index('local function bindDeath(name)');z=text.index('\nend\n',a)+5
 helper=text[a:z];text=text[:a]+text[z:]
 marker="local function wx()";a=text.index(marker);text=text[:a]+helper+'\n'+text[a:]
 marker="local function finish(passed,reason)\n"
 extra=''' local d=assert(io.open(OUTPUT..'death.json','w'));local parts={}
 for name,n in pairs(deathCalls)do parts[#parts+1]=string.format('"%s":%d',name,n)end
 d:write(string.format('{"death_start_age":%d,"observation_frames":%d,"maximum_MmDeathAge":%d,"TimerControl":%d,"Player_Y_HighPos":%d,"Player_Y_Position":%d,"Player_Y_Speed":%d,"ArDead":%d,"MmDeathPit":%d,"DeathMusicLoaded":%d,"EventMusicQueue":%d,"EventMusicBuffer":%d,"restart_x":%d,"calls":{%s}}',deathStart or -1,deathStart and age-deathStart or 0,maximumDeathAge,r('TimerControl'),r('Player_Y_HighPos'),r('Player_Y_Position'),r('Player_Y_Speed'),r('ArDead'),r('MmDeathPit'),r('DeathMusicLoaded'),r('EventMusicQueue'),r('EventMusicBuffer'),restartX or -1,table.concat(parts,',')));d:close()
'''
 assert text.count(marker)==1;text=text.replace(marker,marker+extra)
 marker=" if r('GameEngineSubroutine')~=8 then jumpStart=nil;return b end"
 assert text.count(marker)==1;text=text.replace(marker," if x>=1000 then return b end\n"+marker)
 marker="emu.addMemoryCallback(function()\n if phase=='play' then mainCalls=mainCalls+1 end"
 hook="for _,name in ipairs({'HuDeath','ArHostNativeDeath','NativePlayerDeath','MegaManDeathUpdate','MegaManCheckPit','PlayerCtrlRoutine'})do bindDeath(name)end\n"
 assert text.count(marker)==1;text=text.replace(marker,hook+marker)
 old="if r('NumberofLives')~=startLives then finish(false,'Life lost');return end"
 new='''maximumDeathAge=math.max(maximumDeathAge,r('MmDeathAge'))
  if r('GameEngineSubroutine')==11 and not deathStart then deathStart=age;shot('pit-death-start')end
  if r('NumberofLives')<startLives and r('GameEngineSubroutine')==8 and r('OperMode_Task')==3 then
   if not restarted then restarted=age;restartX=x end
   if age-restarted>=60 then finish(x>restartX and r('ArDead')==0 and r('ArHostReady')==167,'Controller-earned pit death and next-life control');return end
  end
  if deathStart and age-deathStart>=600 and not restarted then finish(false,'Pit death did not reach next-life gameplay within 600 physical frames');return end'''
 assert text.count(old)==1;text=text.replace(old,new)
 text=text.replace("trace:write('frame,age,x,y,camera,engine,player_state,source_mode,jump_count,source_steps,reason,lives\\n')", "trace:write('frame,age,x,y,camera,engine,player_state,source_mode,jump_count,source_steps,reason,lives,timer,y_high,death_age,death_pit,event_queue,event_buffer\\n')")
 old="sourceSteps,jumpReason,r('NumberofLives')))"
 new="sourceSteps,jumpReason,r('NumberofLives'),r('TimerControl'),r('Player_Y_HighPos'),r('MmDeathAge'),r('MmDeathPit'),r('EventMusicQueue'),r('EventMusicBuffer')))"
 assert text.count(old)==1;text=text.replace(old,new)
 text=text.replace('%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s,%d\\n','%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s,%d,%d,%d,%d,%d,%d,%d\\n')
 return text,ref


def main():
 text,ref=controller()
 prepare(P.O/'pit-death',P.O/'candidate.nes',text,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=180,scope='Actual menu/controller-earned firstpit fall afterfourpipes; readonly native death call counts,TimerControl/highY/audio/MmDeathAge observation; requireone life loss and60physicalframes next-life rightwardcontrol with ArDead reset. No state/outcome/helper writes.600physicalframe deathbound,4PNGs,12-frameCSV. Originalfull11negativepreserved.')


if __name__=='__main__':main()
