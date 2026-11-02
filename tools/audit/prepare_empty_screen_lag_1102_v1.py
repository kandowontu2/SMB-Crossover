"""Prepare bounded controller-only empty-screen performance measurements."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/empty-screen-lag-1102-v1'
ROM = R / 'build/excitebike-pose-1101-v3/current4.nes'
PIN = 'cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
CONTROLLER = r'''
local NAME=CHARACTER_NAME
local SLOT,RAW=CHARACTER_SLOT,CHARACTER_RAW
local actions=MENU_ACTIONS
local frame,age,phase,done,step=0,0,'title',false,1
local lastEpoch,initialLives=nil,nil
local metrics={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function wx()return r('Player_PageLoc')*256+r('Player_X_Position')end
local function visible()
 local n,active=0,0
 local left=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
 for i=0,4 do
  if r('Enemy_Flag',i)~=0 then
   active=active+1
   local dx=r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i)-left
   if dx>=0 and dx<256 and r('Enemy_Y_HighPos',i)==1 and r('Enemy_Y_Position',i)<240 then n=n+1 end
  end
 end
 return n,active
end
local function finish(reason)
 if done then return end
 done=true
 local f=assert(io.open(OUTPUT..'empty-screen.png','wb'));f:write(emu.takeScreenshot());f:close()
 local rows={}
 for _,name in ipairs({'idle','walk'})do
  local q=metrics[name]
  if q then rows[#rows+1]=string.format('{"phase":%q,"physical_frames":%d,"main_updates":%d,"updates_per_frame":%.6f,"first_x":%d,"last_x":%d,"max_visible_enemies":%d,"max_active_slots":%d}',name,q.frames,q.updates,q.updates/q.frames,q.firstX,q.lastX,q.visible,q.active)end
 end
 local passed=reason=='measured' and #rows==2 and r('NumberofLives')==initialLives and r('SelectedCharacter')==RAW
 local out=assert(io.open(OUTPUT..'result.json','w'))
 out:write(string.format('{"passed":%s,"reason":%q,"character":%q,"controller_only":true,"frames":%d,"initial_lives":%d,"final_lives":%d,"selected":%d,"measurements":[%s],"full_stage":false}\n',tostring(passed),reason,NAME,frame,initialLives or -1,r('NumberofLives'),r('SelectedCharacter'),table.concat(rows,',')))
 out:close();emu.stop(passed and 0 or 1)
end
emu.addEventCallback(function()
 local pad={}
 if phase=='open' or phase=='start' then pad.start=age<4
 elseif phase=='select' and age<4 then pad[actions[step]]=true
 elseif phase=='walk' then pad.right=true end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end
 frame=frame+1;age=age+1
 if phase=='title' and frame>=100 then phase='open';age=0
 elseif phase=='open' and age>=50 then
  assert(r('CrossoverMenuState')==2,'menu did not open')
  phase=#actions>0 and 'select' or 'start';age=0
 elseif phase=='select' and age>=30 then
  step=step+1;age=0
  if step>#actions then assert(r('CrossoverMenuIndex')==SLOT and r('SelectedCharacter')==RAW,'wrong selected owner');phase='start' end
 elseif phase=='start' and age>=300 then
  assert(r('CrossoverMenuState')==0 and r('SelectedCharacter')==RAW and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8,'active1-1 ingress')
  initialLives=r('NumberofLives');phase='settle';age=0
 elseif phase=='settle' and age>=90 then phase='idle';age=0;lastEpoch=r('FrameCounter')
 elseif phase=='idle' or phase=='walk' then
  assert(r('SelectedCharacter')==RAW and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8,'lost active owner')
  local q=metrics[phase]
  if not q then q={frames=0,updates=0,firstX=wx(),lastX=wx(),visible=0,active=0};metrics[phase]=q end
  local epoch=r('FrameCounter');local delta=(epoch-lastEpoch)&255;lastEpoch=epoch
  assert(delta<=2,'unexpected gameplay frame-counter reset')
  local v,a=visible()
  q.frames=q.frames+1;q.updates=q.updates+delta;q.lastX=wx();q.visible=math.max(q.visible,v);q.active=math.max(q.active,a)
  if r('NumberofLives')~=initialLives then finish('lost-life')
  elseif phase=='idle' and age>=180 then phase='walk';age=0
  elseif phase=='walk' and age>=40 then finish('measured') end
 end
 if frame>1500 and not done then finish('global-bound')end
end,emu.eventType.endFrame)
'''


def main():
    O.mkdir(exist_ok=True)
    assert sha(ROM) == PIN
    inventory = R / 'build/playable-menu-1102-v5/inventory.json'
    rows = json.loads(inventory.read_text(encoding='utf-8'))['rows']
    names = ['MARIO', 'DONATELLO', 'HULK HOGAN', 'RASH', 'BURNS', 'PAPA',
             'EXCITEBIKE', 'ARTHUR', 'METAL STORM']
    packets = []
    for name in names:
        row = next(q for q in rows if q['name'].removeprefix('<3F>') == name)
        slot = row['slot']
        col, rr = slot % 8, slot // 8
        actions = (['right'] * col if col <= 4 else ['left'] * (8 - col))
        actions += (['up'] if rr == 3 else ['down'] * rr)
        actions += ['select'] * row['cycle']
        text = CONTROLLER.replace('CHARACTER_NAME', json.dumps(name)).replace('CHARACTER_SLOT', str(slot))
        text = text.replace('CHARACTER_RAW', str(row['raw']))
        text = text.replace('MENU_ACTIONS', '{' + ','.join(json.dumps(s) for s in actions) + '}')
        target = O / name.lower().replace(' ', '-')
        prepare(target, ROM, text, [Path(__file__), inventory], expected=PIN,
                timeout=90, allow_interactive=True,
                scope='Controller-only cold selection plus180 idle/40 walking physical frames at the opening. '
                      'Measure actual Main frame-counter cadence and visible enemies; one PNG, no writes, '
                      'no full-stage or all-character performance claim.')
        packets.append(dict(character=name, directory=str(target.relative_to(R)), slot=slot,
                            alternate=row['cycle'], raw=row['raw']))
    (O / 'packets.json').write_text(json.dumps(packets, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
