"""Controller-only enemy/pit deaths must return to real active play."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha
from prepare_hogan_full11_1102_v2 import CONTROLLER as ROUTE

O = R / 'build/wwf-death-1102-v2'
ROM = O / 'candidate.nes'
CONTACT = r'''
local VARIANT=VARIANT_VALUE
local frame,age,phase,step=0,0,'title',1
local actions={'right','right','right','right','up'}
for i=1,VARIANT do actions[#actions+1]='select'end
local done,deathSeen=false,false
local initialLives,deathFrame,maxDeathAge=nil,nil,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function finish(reason)
 if done then return end;done=true
 local passed=reason=='contact-death-recovered' and deathSeen and r('NumberofLives')==initialLives-1 and active()
 local f=assert(io.open(OUTPUT..'endpoint.png','wb'));f:write(emu.takeScreenshot());f:close()
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(string.format('{"passed":%s,"reason":%q,"controller_only":true,"WWF_variant":%d,"frames":%d,"death_frame":%d,"death_seen":%s,"maximum_death_age":%d,"initial_lives":%d,"final_lives":%d,"world":%d,"level":%d,"engine":%d,"mode":%d,"task":%d}',tostring(passed),reason,VARIANT,frame,deathFrame or -1,tostring(deathSeen),maxDeathAge,initialLives or -1,r('NumberofLives'),r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),r('OperMode'),r('OperMode_Task')))
 f:close();emu.stop(passed and 0 or 1)
end
emu.addEventCallback(function()
 local pad={}
 if phase=='open' or phase=='start' then pad.start=age<4
 elseif phase=='select' and age<4 then pad[actions[step]]=true
 elseif phase=='play' and not deathSeen then pad.right=true end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title' and frame>=100 then phase='open';age=0
 elseif phase=='open' and age>=50 then assert(r('CrossoverMenuState')==2);phase='select';age=0
 elseif phase=='select' and age>=30 then
  step=step+1;age=0
  if step>#actions then assert(r('SelectedCharacter')==29 and r('FmGroups')&7==VARIANT);phase='start' end
 elseif phase=='start' and age>=300 then assert(active());initialLives=r('NumberofLives');phase='play';age=0
 elseif phase=='play' then
  if r('GameEngineSubroutine')==11 then
   if not deathSeen then deathSeen=true;deathFrame=frame;assert(r('MmDeathPit')==0,'Expected contact death, not pit')end
   maxDeathAge=math.max(maxDeathAge,r('MmDeathAge'))
  end
  if deathSeen and r('NumberofLives')==initialLives-1 and active() then
   assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('SelectedCharacter')==29 and r('FmGroups')&7==VARIANT)
   assert(maxDeathAge>=168,'Original native normal death duration must finish')
   finish('contact-death-recovered');return
  end
  if r('NumberofLives')<initialLives-1 then finish('extra-life-lost');return end
  if age>=2400 then finish('death-recovery-bound');return end
 end
 if frame>=3600 then finish('global-bound')end
end,emu.eventType.endFrame)
'''


def main():
    digest = sha(ROM)
    refs = [Path(__file__), R / 'tools/audit/prepare_hogan_full11_1102_v2.py', O / 'assembly.json', O / 'CPU.json']
    for variant in range(6):
        prepare(O / f'contact-{variant}', ROM, CONTACT.replace('VARIANT_VALUE', str(variant)), refs,
                expected=digest, timeout=90, allow_interactive=True,
                scope=f'WWF identity{variant}: genuine cold selection and ordinary enemy contact death, '
                      'native death age/life loss, real active1-1 respawn and retained identity. No writes, '
                      'one PNG. Does not qualify stage clear or original WWF endurance/animation.')
    text = ROUTE
    text = text.replace('local done=false', 'local done=false\nlocal deathSeen,deathFrame,maxDeathAge=false,nil,0')
    old = "local passed=reason=='active-1-2' and initialLives==r('NumberofLives')"
    assert text.count(old) == 1
    text = text.replace(old, "local passed=reason=='pit-death-recovered' and deathSeen and maxDeathAge>=150 and r('NumberofLives')==initialLives-1 and active()")
    old = "  if r('NumberofLives')~=initialLives then finish('lost-life');return end"
    assert text.count(old) == 1
    text = text.replace(old, """
  if r('GameEngineSubroutine')==11 then
   if not deathSeen then deathSeen=true;deathFrame=frame;assert(r('MmDeathPit')==1,'Expected first-pit death')end
   maxDeathAge=math.max(maxDeathAge,r('MmDeathAge'))
  end
  if deathSeen and r('NumberofLives')==initialLives-1 and active()then
   assert(r('WorldNumber')==0 and r('LevelNumber')==0)
   finish('pit-death-recovered');return
  end
  if r('NumberofLives')<initialLives-1 then finish('extra-life-lost');return end""")
    # Keep this exact failed traversal policy: it naturally reaches the first
    # pit and must now recover. It is not recast as a full-stage success.
    prepare(O / 'pit', ROM, text, refs, expected=digest, timeout=150, allow_interactive=True,
            scope='Same natural failed Hogan route crosses four pipes then falls into first pit. '
                  'Must complete real150-tick native pit death, lose exactly one life and return '
                  'to active1-1. Controller-only, one PNG; not a stage-clear proof.')


if __name__ == '__main__':
    main()
