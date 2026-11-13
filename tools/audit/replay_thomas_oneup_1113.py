"""Prepare and run Thomas's natural hidden-1UP lift, fresh jump and native award."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import compose_thomas_oneup_lift_1113 as Fix
import replay_thomas_star_1113 as Star
from run_stdout_mesen_1110 import R, run


PIN = '65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643'


def controller():
    assert sha256(Star.SOURCE.read_bytes()).hexdigest() == Star.SOURCE_PIN
    text = Star.SOURCE.read_text()
    text = Star.once(text, "local mode=tonumber(os.getenv('SMB_TEST_VARIANT')or '0')", 'local mode=1')
    text = Star.once(text, 'local lifts={{400,176},{560,160},{688,144},{864,144}}',
                     'local oneupJump,oneupHead,oneupAward,oneupHeadAttempt=nil,nil,nil,nil\nlocal lifts={{400,176},{560,160},{688,144},{864,144}}')
    text = Star.once(text, 'flower_helper=flowerHelper or false,flower_helper_birth=helperBirth or false,recent=history,terminal=state()',
                     'oneup_helper=flowerHelper or false,oneup_helper_birth=helperBirth or false,oneup_jump=oneupJump or false,oneup_head=oneupHead or false,oneup_head_attempt=oneupHeadAttempt or false,oneup_award=oneupAward or false,recent=history,terminal=state()')
    text = Star.once(text, 'local function control(s,actors)', 'local function prefixControl(s,actors)')
    text = Star.once(text, 'local function drive()', '''local function control(s,actors)
 local x,y,ground=s.x,s.y,s.state==0
 if s.active~=0 then return 0 end
 local helper=nil
 for _,a in ipairs(actors)do if a.id==37 and a.x==1008 then helper=a;break end end
 local previous=helperY;helperY=helper and helper.y or nil
 local boarded=helper and helper.contact==helper.slot
 if phase=='cross'and lift==4 and x>=960 then
  crossings[#crossings+1]={pipe=912,epoch=epoch,x=x};phaseTo('oneup-retreat')
 end
 if not phase:find('oneup%-')then return prefixControl(s,actors)end
 local age=epoch-phaseEpoch
 if #pickups==2 then return 0 end
 if phase=='oneup-retreat'then
  if x>984 or not ground then return 2 end
  phaseTo('oneup-wait');return 0
 elseif phase=='oneup-wait'then
  if helper and helper.y>=188 and(not previous or helper.y>=previous)then phaseTo('oneup-runup')end
  return 0
 elseif phase=='oneup-runup'then
  if age>=6 then phaseTo('oneup-hop')end
  return 1
 elseif phase=='oneup-hop'then
  if x>=1022 or age>=64 then
   if boarded then flowerHelper={boarded=s,actor=helper};phaseTo('oneup-jump')
   elseif ground or age>=64 then phaseTo('oneup-retreat')end
   return 0
  end
  return age<3 and 9 or 1
 elseif phase=='oneup-jump'then
  oneupJump=oneupJump or {player=s,actor=helper}
  if oneupHead then phaseTo('oneup-chase');return 0 end
  assert(age<24,'Fresh original jump reaches hidden block')
  return 9
 end
 local item=nil
 for _,a in ipairs(actors)do if a.id==46 and a.kind==3 then item=a;break end end
 if item and item.state&128~=0 then return x<item.x-8 and 1 or x>item.x+4 and 2 or 0 end
 return 0
end
local function drive()''')
    text = Star.once(text, " assert(s.lives==2 and s.engine~=11,'Route life and death check')",
                     " assert(s.lives>=2 and s.lives<=3 and s.engine~=11,'Route life and death check')")
    first = text.index(' if #pickups==2 and s.active==0 and s.status==2')
    after = text.index(' pad=control(s,actors)', first)
    text = text[:first]+''' if s.lives==3 and not oneupAward then
  assert(#pickups==2 and pickups[2].item.kind==3,'Native 1UP collector precedes award')
  oneupAward=s
 end
 if oneupAward and epoch-oneupAward.epoch>=8 then
  assert(ticks[1]==60 and ticks[2]==0 and #crossings==4 and s.timer==0 and s.engine==8,'Native recovery and four pipe crossings')
  assert(helperBirth and flowerHelper and oneupJump and oneupHead,'Offscreen native lift, board, fresh jump and hidden head hit')
  assert(s.status==1 and s.lives==3,'Native 1UP preserves upgrade and awards exactly one life')
  finish(true,'Earned mushroom and hidden 1UP through native lift and original fresh jump');return
 end
'''+text[after:]
    text = Star.once(text, 'if a.id==46 and a.kind<=1 then', 'if a.id==46 and(a.kind==0 or a.kind==3)then')
    text = Star.once(text, "which<=2 and a.flag==1 and a.id==46 and a.kind==which-1",
                     "which<=2 and a.flag==1 and a.id==46 and a.kind==(which==1 and 0 or 3)")
    text = Star.once(text, "r(0x10d+i)==6 and q.sound>0,'Native pickup effects'",
                     "r(0x10d+i)==(q.item.kind==3 and 11 or 6)and q.sound>0,'Native pickup effects'")
    text = Star.once(text, "   assert(now.active==1 and now.age==0 and now.engine==9 and now.timer==255,'Hosted freeze starts')", '''   if q.item.kind==0 then
    assert(now.active==1 and now.age==0 and now.engine==9 and now.timer==255,'Hosted freeze starts')
   else
    assert(oneupHead and now.active==0 and now.status==1 and now.lives==2,'Natural 1UP immediate native grant')
    q.native_return={ps=c['cpu.ps']or c['cpu.p'],flag=r(0x10+i),floaty=r(0x10d+i),floaty_timer=r(0x129+i),sound_writes=q.sound,player=now}
   end''')
    text = text.replace('births[a.kind+1]', 'births[a.kind==3 and 2 or 1]')
    text = text.replace('matures[a.kind+1]', 'matures[a.kind==3 and 2 or 1]')
    text = text.replace('births[q.item.kind+1]', 'births[q.item.kind==3 and 2 or 1]')
    text = text.replace('matures[q.item.kind+1]', 'matures[q.item.kind==3 and 2 or 1]')
    text = Star.once(text, ' if a.x~=1200 then return end', ' if a.x~=1008 then return end')
    text = Star.once(text, "end)\nexec(0x82d9,'GameLoop'", '''end)
exec(0x9ef5,'Hidden 1UP head contact',function()
 if not game or not mapped(0x9ef5,126)then return end
 local c=emu.getState()
 if c['cpu.a']~=96 then return end
 local source=emu.read(0x4069,emu.memType.nesWorkRam)
 oneupHeadAttempt={player=state(),tile=c['cpu.a'],saved=r(0xdc),source_air=source,
  source_b6=emu.read(0x40b6,emu.memType.nesWorkRam),native_yspeed=r(0x8e),jump_requested=oneupJump~=nil,boarded=flowerHelper~=nil}
 assert(oneupJump and flowerHelper and not oneupHead,'One original jump from boarded lift')
 assert(r(0xdc)&8~=0 and source&4~=0 and r(0x8e)&128~=0,'Actual Up and original rising source jump at hidden block')
 oneupHead=oneupHeadAttempt
end)
exec(0x82d9,'GameLoop' ''')
    assert 'emu.write' not in text and 'io.open' not in text and 'takeScreenshot' not in text
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=R/'build/thomas-oneup-native-1113')
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    raw = Fix.Current.ROM.read_bytes()
    if sha256(raw).hexdigest() == PIN:
        raw = Fix.inverse(raw)
    image, _ = Fix.proposal(raw)
    assert sha256(image).hexdigest() == PIN
    text = controller()
    if args.check_only:
        import check_thomas_stdout_controller_source_1110 as Mock
        lua = Mock.Base.LuaRuntime(unpack_returned_tuples=True)
        assert lua.eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
        lua.execute(Mock.Base.MOCK)
        lua.globals().host.env['SMB_STDOUT_ROM_SHA'] = PIN
        lua.execute(text)
        Mock.startup(lua)
        print(json.dumps(dict(compiles=True, opening_input_updates=60, output_files=0,
                              candidate_SHA256=PIN, script_SHA256=sha256(text.encode()).hexdigest())), flush=True)
        return
    args.output.mkdir(exist_ok=True)
    rom, script = args.output/'candidate.nes', args.output/'controller.lua'
    rom.write_bytes(image)
    script.write_text(text, encoding='utf-8', newline='\n')
    if args.prepare_only:
        print(json.dumps(dict(prepared=True, ROM=str(rom), ROM_SHA256=PIN, script=str(script),
                              script_SHA256=sha256(script.read_bytes()).hexdigest(), output_files=2)), flush=True)
        return
    result = run(script, rom, args.output/'capture', PIN, 240)
    print(json.dumps({key: result[key] for key in ('passed', 'receipt_SHA256', 'script_SHA256', 'receipt')}), flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
