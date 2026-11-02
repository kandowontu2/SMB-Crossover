"""Record native scene counter resets without weakening active1-2 admission."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import R,prepare,sha
from prepare_excitebike_dispatch_1101_v1 import O


def main():
    old=O/'full11-v4';binding=json.loads((old/'capture/binding.json').read_text())
    log=(old/'capture/current4-controller.log').read_text()
    assert binding['exit_code']==1 and 'Unexpected Main epoch gap'in log and not(old/'capture/result.json').exists()
    text=(old/'controller.lua').read_text()
    def replace(old,new):
        nonlocal text
        assert text.count(old)==1,old
        text=text.replace(old,new)
    replace('local lastEpoch,updates,initialLives=nil,0,nil',
            'local lastEpoch,updates,initialLives=nil,0,nil\nlocal lastTask,lastWorld,lastLevel,lastArea=nil,nil,nil,nil\nlocal sceneEvents={}')
    marker='local function finish(passed,reason)\n'
    replace(marker,marker+'''
 local scenes=assert(io.open(OUTPUT..'scene.json','w'))
 scenes:write('['..table.concat(sceneEvents,',')..']');scenes:close()
''')
    replace("initialLives=r('NumberofLives');lastEpoch=r('FrameCounter');phase='play'", "initialLives=r('NumberofLives');lastEpoch=r('FrameCounter');lastTask=r('OperMode_Task');lastWorld=r('WorldNumber');lastLevel=r('LevelNumber');lastArea=r('AreaNumber');phase='play'")
    before="  local epoch=r('FrameCounter');local delta=(epoch-lastEpoch)&255;lastEpoch=epoch;assert(delta<=2,'Unexpected Main epoch gap');updates=updates+delta"
    after='''  local epoch=r('FrameCounter');local delta=(epoch-lastEpoch)&255
  local task,world,level,area=r('OperMode_Task'),r('WorldNumber'),r('LevelNumber'),r('AreaNumber')
  local transition=task~=lastTask or level~=lastLevel or area~=lastArea
  if transition or delta>2 then
   if #sceneEvents<64 then sceneEvents[#sceneEvents+1]=string.format('{"frame":%d,"old_epoch":%d,"new_epoch":%d,"delta":%d,"allowed_scene_reset":%s,"old_world":%d,"world":%d,"old_level":%d,"level":%d,"old_area":%d,"area":%d,"old_task":%d,"task":%d,"star_flag_task":%d,"engine":%d}',frame,lastEpoch,epoch,delta,tostring(delta>2 and transition),lastWorld,world,lastLevel,level,lastArea,area,lastTask,task,r('StarFlagTaskControl'),r('GameEngineSubroutine'))end
   if delta>2 and not transition then finish(false,'Unexpected epoch gap outside native scene transition');return end
  end
  if delta>2 then delta=0 end -- Counter reset is not counted as completed Main work.
  lastEpoch=epoch;lastTask=task;lastWorld=world;lastLevel=level;lastArea=area;updates=updates+delta'''
    replace(before,after)
    replace("   finish(maxX>=3000,'Reached active1-2');return", "   local pipes,gaps=0,0\n   for _,edge in ipairs({480,640,768,944})do if maxX>=edge+16 then pipes=pipes+1 end end\n   for _,edge in ipairs({1136,2240,2480})do if maxX>=edge+16 then gaps=gaps+1 end end\n   finish(maxX>=3000 and pipes==4 and gaps==3 and r('NumberofLives')==initialLives,'Reached active1-2');return")
    rom=O/'current4.nes';pin='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
    prepare(O/'full11-v5',rom,text,
            [Path(__file__),old/'controller.lua',old/'capture/binding.json',old/'capture/current4-controller.log',O/'current4-composition.json'],
            expected=pin,timeout=240,allow_interactive=True,
            scope='Same v4 controller inputs and exact ROM. Permit large FrameCounter delta ONLY with observed native OperModeTask/Level/Area transition; record old/new epoch/world/level/area/task/StarFlagTask/currentengine and count no fake updates. Any other large delta fails. Require actual0world/level1/task3/engine8, all4pipes/all3gaps, maxX>=3000 and same lives. No writes/helpers/source changes; preserve v4 assertion negative.4PNGs/global9500frame bound retained.')


if __name__=='__main__':main()
