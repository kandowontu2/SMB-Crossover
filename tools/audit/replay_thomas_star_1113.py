"""Prepare Thomas's ordinary-controller Star replay from the qualified flower route."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

from run_stdout_mesen_1110 import R, run


SOURCE = R/'tools/playthroughs/thomas_flower_stdout_1112.lua'
SOURCE_PIN = 'cde6a22ba2d5144d82964e095f77db18dbf66a79b03eca3d810507f6b7f5c2cf'
PIN = '318a087735b4204c74274b4107efbc302bc15a674a7f6f9d3bed598cea90d08d'


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def controller(gap_wait=0):
    assert sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_PIN
    text = SOURCE.read_text()
    text = once(text, "local mode=tonumber(os.getenv('SMB_TEST_VARIANT')or '0')", 'local mode=1')
    text = once(text, 'local flowerAttempts,flowerPeak,lastJump,flowerHelper,helperY,helperBirth=0,255,false,nil,nil,nil',
                'local flowerAttempts,flowerPeak,lastJump,flowerHelper,helperY,helperBirth=0,255,false,nil,nil,nil\n'
                f'local gapPending,starStarted=false,nil\nlocal gapWait,gapWaitFrame,gapTrace={gap_wait},nil,{{}}\nlocal pickupReturns={{}}')
    text = once(text, 'flower_helper=flowerHelper or false,flower_helper_birth=helperBirth or false,recent=history,terminal=state()',
                'flower_helper=flowerHelper or false,flower_helper_birth=helperBirth or false,gap_wait=gapWait,gap_trace=gapTrace,pickup_returns=pickupReturns,recent=history,terminal=state()')
    text = once(text, 'if #pickups>=2 then return 2 end', '''if #pickups>=2 then
  if #pickups>=3 then return 0 end
  if not starStarted then starStarted=epoch;phaseTo('star-approach')end
  if phase=='star-wait'then
   local star=nil
   for _,a in ipairs(actors)do if a.id==46 and a.kind==2 then star=a;break end end
   if star then return x<star.x-8 and 1 or x>star.x+4 and 2 or ground and 8 or 0 end
   return ground and 8 or 0
  end
  if x>=1606 and ground then phaseTo('star-wait');return 9 end
  if ground and x>=1364 and x<1372 and y==176 and gapWait>0 then
   if not gapWaitFrame then gapWaitFrame=frame end
   if frame-gapWaitFrame<gapWait then return 0 end
  end
  if ground and x>=1372 and x<1424 and y==176 and solid(x+3,y+32)and not solid(x+12,y+32)then gapPending=true end
  if gapPending and (s.state==1 and r(0x8e)&128~=0 or x>=1378)then gapPending=false end
  if gapPending then return 9 end
  if ground and x>=1350 and x<1372 and y==176 then return 1 end
  if hostile(s,actors)then return 4+(epoch%24<6 and 64 or 0)end
  return ground and epoch%8<3 and (solid(x+20,y+31)or not solid(x+12,y+32))and 9 or 1
 end''')
    start = text.index(' if #pickups==2 and s.active==0 and s.status==2')
    end = text.index(' pad=control(s,actors)', start)
    text = text[:start]+''' if #pickups==3 and epoch-pickups[3].player.epoch>=8 then
  assert(ticks[1]==60 and ticks[2]==60 and #crossings==4 and s.timer==0 and s.engine==8,'Native post-Star control')
  assert(helperBirth and flowerHelper and flowerHelper.depart,'Native flower assistance observed')
  assert(r(0x79c)>0 and s.status==2 and s.lives==2,'Natural Star retained source status and lives')
  finish(true,'Earned mushroom, flower and Star through ordinary controller input');return
 end
'''+text[end:]
    text = once(text, 'if a.id==46 and a.kind<=1 then', 'if a.id==46 and a.kind<=2 then')
    text = once(text, "which<=2 and a.flag==1 and a.id==46 and a.kind==which-1", "which<=3 and a.flag==1 and a.id==46 and a.kind==which-1")
    text = once(text, "   assert((c['cpu.ps']or c['cpu.p'])&1~=0 and r(0x10+i)==0 and r(0x10d+i)==6 and q.sound>0,'Native pickup effects')", '''   local ps=c['cpu.ps']or c['cpu.p']
   q.native_return={kind=q.item.kind,a=c['cpu.a'],x=c['cpu.x'],y=c['cpu.y'],ps=ps,carry=ps&1,
    flag=r(0x10+i),floaty=r(0x10d+i),floaty_timer=r(0x129+i),sound_writes=q.sound,sound_queue=r(0x104),
    star=r(0x79c),music=r(0x101),player=now}
   pickupReturns[#pickupReturns+1]=q.native_return
   assert(r(0x10+i)==0 and r(0x10d+i)==6 and q.sound>0,'Native pickup effects')
   assert(ps&1==(q.item.kind==2 and 0 or 1),'Exact source kind-specific return carry')''')
    text = once(text, "   assert(now.active==1 and now.age==0 and now.engine==9 and now.timer==255,'Hosted freeze starts')",
                "   if q.item.kind<2 then assert(now.active==1 and now.age==0 and now.engine==9 and now.timer==255,'Hosted freeze starts')\n"
                "   else assert(r(0x79c)==35 and r(0x101)==64 and now.active==0 and now.status==2,'Native Star timer/music/status');q.star_timer=r(0x79c);q.star_music=r(0x101)end")
    marker = "emu.addEventCallback(guarded('Controller poll',function()\n"
    text = once(text, marker, '''local function gapSample(kind)
 if not game or #gapTrace>=48 then return end
 local s=state()
 if s.x<1362 or s.x>1382 then return end
 s.kind=kind;s.saved=r(0xdc);s.counter=r(0x0e);s.pad=pad
 s.source_last=emu.read(0x4803,emu.memType.nesWorkRam)
 s.source_have=emu.read(0x4804,emu.memType.nesWorkRam)
 s.source_air=emu.read(0x4069,emu.memType.nesWorkRam)
 s.source_b6=emu.read(0x40b6,emu.memType.nesWorkRam)
 gapTrace[#gapTrace+1]=s
end
exec(0xa103,'Thomas source movement input',function()
 if not game then return end
 local q=emu.convertAddress(0xa103)
 if not q or q.memType~=emu.memType.nesWorkRam or q.address~=3*8192+0x103 then return end
 assert(r(0xa103)==8 and r(0xa104)==72 and r(0xa105)==138,'Pinned Thomas movement entry')
 gapSample('movement')
end)
''' + marker + ''' if game and #pickups==2 and phase=='star-approach'then
  local s=state()
  if s.x>=1362 and s.x<1378 and s.y==176 then
   local waiting=gapWaitFrame and frame-gapWaitFrame<gapWait
   pad=waiting and 0 or (s.state==0 and s.x>=1372 and 9 or 1)
   gapSample('input-poll')
  end
 end
''')
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'))
    parser.add_argument('--output', type=Path, default=R/'build/thomas-star-native-1113')
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--gap-wait', type=int, default=0, choices=range(9))
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    from check_thomas_star_route_1113 import authenticate
    authenticate(raw)
    text = controller(args.gap_wait)
    if args.check_only:
        import check_thomas_stdout_controller_source_1110 as Mock
        assert sha256(Mock.Base.DLL.read_bytes()).hexdigest() == Mock.Base.DLL_SHA
        lua = Mock.Base.LuaRuntime(unpack_returned_tuples=True)
        assert lua.eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
        lua.execute(Mock.Base.MOCK)
        lua.globals().host.env['SMB_STDOUT_ROM_SHA'] = PIN
        lua.execute(text)
        Mock.startup(lua)
        assert 'emu.write' not in text and 'io.open' not in text and 'takeScreenshot' not in text
        print(json.dumps(dict(compiles=True, opening_input_updates=60, controller_only=True, output_files=0,
                              script_SHA256=sha256(text.encode()).hexdigest(), ROM_SHA256=PIN)), flush=True)
        return
    args.output.mkdir(exist_ok=True)
    script = args.output/'controller.lua'
    script.write_text(text, encoding='utf-8', newline='\n')
    if args.prepare_only:
        print(json.dumps(dict(prepared=True, script=str(script), script_SHA256=sha256(script.read_bytes()).hexdigest(),
                              ROM_SHA256=PIN, output_files=1)), flush=True)
        return
    result = run(script, args.rom, args.output/'capture', PIN, 240)
    print(json.dumps({key: result[key] for key in ('passed','receipt_SHA256','script_SHA256','receipt')}), flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
