"""Controller-only mirrored inhale after jumping past the first natural Goomba."""
import json
import argparse
from pathlib import Path
from hashlib import sha256
from run_stdout_mesen_1110 import R, run


def controller(variant=1, hard=False):
    text=(R/'tools/playthroughs/kirby_current_inhale_stdout_1110_v3.lua').read_text()
    text=text.replace('local lastIngress', "local crossing='approach'\nlocal landFrame=0\nlocal lastIngress")
    text=text.replace('~=0x41','~=0x42').replace('fresh.facing~=1','fresh.facing~=2')
    text=text.replace("r('PlayerFacingDir')~=1", "r('PlayerFacingDir')~=2")
    text=text.replace('local gap=a.x-x()', 'local gap=x()-a.x')
    start=text.index(' if firstActive and not finished then\n')
    end=text.index(' emu.setInput(input,0)',start)
    text=text[:start]+''' if firstActive and not finished then
  input={right=true}
  if erased then input={}
  elseif constructor then
   local a=actor(constructor.slot)
   if crossing=='approach' and a.x-x()<=180 and r('Player_State')==0 then crossing='air' end
   if crossing=='air' then
    input={right=true,a=true,up=true}
    if x()-a.x>=32 then crossing='land';landFrame=frame;input={b=true};events[#events+1]={crossing=crossing,player=player(),target=a} end
   elseif crossing=='land' then
    input={b=frame-landFrame<2}
    if r('Player_State')==0 then crossing='inhale';events[#events+1]={crossing=crossing,player=player(),target=a} end
   elseif crossing=='inhale' then
    input={left=true}
    if launch then input.b=true
    else
     local gap=x()-a.x
     if a.flag==1 and a.id==6 and a.state<2 and r('PlayerFacingDir')==2 and
        r('Player_State')==0 and a.y_high==1 and math.abs(a.y-r('Player_Y_Position')-8)<=12 and
        gap>=gapLo and gap<=gapHi then
      launch={player=player(),target=a,gap=gap};input.b=true
     end
    end
   end
  end
 end
'''+text[end:]
    text=text.replace("if x()>=400 then", "if x()>=448 then")
    if variant == 2:
        text=text.replace('if x()-a.x>=32 then', 'if x()-a.x>=16 then')
    if hard:
        identity="r('KbVariant')==0 and r('CrossoverBehaviorVersion')==0 and noCheats()"
        assert text.count(identity)==1
        text=text.replace(identity, identity.replace("Version')==0", "Version')==1"))
        entry=" press('start')\n ready(function()return r('CrossoverMenuState')==2"
        assert text.count(entry)==1
        text=text.replace(entry, """ press('down');press('a')
 assert(r('CrossoverMenuState')==4,'Actual Options opens')
 press('down');press('a')
 assert(r('CrossoverBehaviorVersion')==1,'Actual Hard selected')
 press('b')
 ready(function()return r('CrossoverMenuState')==0 and r('DisableScreenFlag')==0 end,180,'title return')
 press('start')
 ready(function()return r('CrossoverMenuState')==2""")
        text=text.replace('Actual Easy Kirby selection','Actual Hard Kirby selection')
    return text


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--variant',type=int,choices=(1,2),default=1)
    parser.add_argument('--hard',action='store_true')
    args=parser.parse_args()
    rom=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    output=R/'build/kirby-left-inhale-1112'
    output.mkdir(exist_ok=True)
    script=output/'controller.lua'
    script.write_text(controller(args.variant,args.hard),encoding='utf-8',newline='\n')
    result=run(script,rom,output/'capture',sha256(rom.read_bytes()).hexdigest(),60,variant=args.variant)
    print(json.dumps({k:result[k] for k in ('passed','receipt_SHA256','script_SHA256','receipt')}),flush=True)
    assert result['passed']


if __name__=='__main__':
    main()
