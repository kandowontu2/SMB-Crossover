"""Continue the qualified natural Thomas Star route through the remaining 1-1."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import replay_thomas_star_1113 as Star
from run_stdout_mesen_1110 import R, run


PREFIX = 'c44cae59ac7d13437f06421620313853442de4e9d24bc5d99cc7972d0f49fd99'
OUTPUT = R/'build/thomas-star-stage-native-1113'


def controller():
    text = Star.controller()
    assert sha256(text.encode()).hexdigest() == PREFIX
    text = Star.once(text, 'local pickupReturns={}',
                     'local pickupReturns={}\nlocal stageStarted,starConfirmed=nil,nil\nlocal lateBirths,lateCarries={},{}')
    text = Star.once(text, 'local lifts={{400,176},{560,160},{688,144},{864,144}}',
                     'local lifts={{400,176},{560,160},{688,144},{864,144},{2560,176},{2816,176}}')
    text = Star.once(text, "phaseTo(lift>#lifts and 'flower-approach' or 'approach-lift')",
                     "phaseTo(lift>4 and 'flower-approach' or 'approach-lift')")
    text = Star.once(text, 'pickup_returns=pickupReturns,recent=history,terminal=state()',
                     'pickup_returns=pickupReturns,star_confirmed=starConfirmed or false,late_births=lateBirths,late_carries=lateCarries,recent=history,terminal=state()')

    source = Star.SOURCE.read_text()
    first = source.index(' local left,top=lifts[lift][1]')
    after = source.index('\nend\nlocal function drive()', first)
    lift_body = source[first:after]
    lift_body = Star.once(lift_body, "phaseTo(lift>#lifts and 'flower-approach' or 'approach-lift')", "phaseTo('full-stage')")
    stage = '''local function stageControl(s,actors)
 local x,y,ground=s.x,s.y,s.state==0
 if not stageStarted then
  stageStarted=epoch;lift=5;previousY=nil;phaseTo('full-stage')
 end
 local age=epoch-phaseEpoch
 if phase=='full-stage'and lift<=6 and x>=lifts[lift][1]-112 then phaseTo('approach-lift');age=0 end
 if phase=='full-stage'then
  if ground and r(0x79c)==0 and hostile(s,actors)then return 4+(epoch%24<6 and 64 or 0)end
  return ground and epoch%8<3 and (solid(x+20,y+31)or not solid(x+12,y+32))and 9 or 1
 end
 local left=lifts[lift][1]
 for _,a in ipairs(actors)do
  if a.flag==1 and a.id==37 and a.x==left and a.contact==a.slot then
   lateCarries[left]=lateCarries[left]or {boarded=s,actor=a}
   if phase=='cross'then lateCarries[left].depart=s end
  end
 end
''' + lift_body + '\nend\n'
    text = Star.once(text, 'local function control(s,actors)', stage+'local function control(s,actors)')
    text = Star.once(text, 'if #pickups>=3 then return 0 end', 'if #pickups>=3 then return stageControl(s,actors)end')
    text = Star.once(text, " assert(r(0x764)==0 and r(0x761)==0 and r(0x7ffb)==0 and r(0x7ffc)==0,'1-1 and cheats off')", ''' assert(r(0x7ffb)==0 and r(0x7ffc)==0,'Cheats off')
 if r(0x764)==0 and r(0x761)==1 then
  if s.engine~=8 then pad=0;return end
  assert(#pickups==3 and ticks[1]==60 and ticks[2]==60 and starConfirmed,'Three natural items and completed hosted progression')
  assert(#crossings==6 and #lateBirths==2,'All six authored pipe crossings and both late births')
  assert(lateCarries[2560]and lateCarries[2560].depart and lateCarries[2816]and lateCarries[2816].depart,'Both native late carries')
  assert(s.lives==2 and s.status==2,'Retained lives and upgrades in active 1-2')
  finish(true,'Natural mushroom, flower and Star then full 1-1 into active 1-2');return
 end
 assert(r(0x764)==0 and r(0x761)==0,'Remain in 1-1 until active 1-2')''')
    text = Star.once(text, "assert(epoch<4400,'Logical route bound')", "assert(epoch<9000,'Logical route bound')")
    text = Star.once(text, "assert(frame<12500,'Physical frame bound')", "assert(frame<20000,'Physical frame bound')")
    text = Star.once(text, " if #pickups==3 and epoch-pickups[3].player.epoch>=8 then", " if #pickups==3 and not starConfirmed and epoch-pickups[3].player.epoch>=8 then")
    text = Star.once(text, "  finish(true,'Earned mushroom, flower and Star through ordinary controller input');return", '  starConfirmed=s')
    text = Star.once(text, ' if a.x~=1200 then return end', ''' if a.x==2560 or a.x==2816 then
  local left=word(0x71f,0x71d);local right=word(0x720,0x71e)
  assert(a.id==37 and a.flag==1 and a.y==192,'Late lift native placement')
  assert(a.x-left>=256 and a.x-left<=287 and a.x>right,'Late lift starts beyond camera right')
  lateBirths[#lateBirths+1]={actor=a,frame=frame,epoch=epoch,camera_left=left,camera_right=right,relative_left=a.x-left,center=a.x+16}
  return
 end
 if a.x~=1200 then return end''')
    assert 'emu.write' not in text and 'io.open' not in text and 'takeScreenshot' not in text
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'))
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    assert sha256(raw).hexdigest() == Star.PIN
    from check_thomas_star_route_1113 import authenticate
    authenticate(raw)
    text = controller()
    if args.check_only:
        import check_thomas_stdout_controller_source_1110 as Mock
        assert sha256(Mock.Base.DLL.read_bytes()).hexdigest() == Mock.Base.DLL_SHA
        lua = Mock.Base.LuaRuntime(unpack_returned_tuples=True)
        assert lua.eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
        lua.execute(Mock.Base.MOCK)
        lua.globals().host.env['SMB_STDOUT_ROM_SHA'] = Star.PIN
        lua.execute(text)
        Mock.startup(lua)
        print(json.dumps(dict(compiles=True, opening_input_updates=60, output_files=0,
                              ROM_SHA256=Star.PIN, script_SHA256=sha256(text.encode()).hexdigest())), flush=True)
        return
    args.output.mkdir(exist_ok=True)
    script = args.output/'controller.lua'
    script.write_text(text, encoding='utf-8', newline='\n')
    if args.prepare_only:
        print(json.dumps(dict(prepared=True, output_files=1, script=str(script), script_SHA256=sha256(script.read_bytes()).hexdigest())), flush=True)
        return
    result = run(script, args.rom, args.output/'capture', Star.PIN, 240)
    print(json.dumps({key: result[key] for key in ('passed', 'receipt_SHA256', 'script_SHA256', 'receipt')}), flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
