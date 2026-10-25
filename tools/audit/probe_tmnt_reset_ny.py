"""Original TMNT reset-counter instructions and a bounded native boot probe."""
from pathlib import Path
import hashlib
import importlib.util
import json
import argparse
import csv
from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-review-ny/source-reset-v1')


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', default='source-reset-v1')
    parser.add_argument('--sewer-route', action='store_true')
    parser.add_argument('--counter-marker', action='store_true')
    args = parser.parse_args()
    assert args.label and all(c.isalnum() or c in '-_' for c in args.label)
    OUT = OUT.parent / args.label
    OUT.mkdir(parents=True, exist_ok=False)
    source = Path('C:/NES/Teenage Mutant Ninja Turtles (USA).nes'); raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '15e112c3790add361157dfa42854c3159c956f72e6acd8fabc518615f1ce8525'
    cases = []
    for entry in (0xc6d2, 0xc6d6):
        for counter in (0, 1, 23, 24, 25, 255):
            cpu = MPU(); cpu.memory[0xc000:] = raw[16 + 7 * 16384:16 + 8 * 16384]
            cpu.memory[0x3d8] = counter; cpu.pc = entry; cpu.sp = 0xfd
            cpu.memory[0x1fe], cpu.memory[0x1ff] = 0xef, 0xbf
            for _ in range(6000):
                if cpu.pc == 0xbff0:
                    break
                cpu.step()
            assert cpu.pc == 0xbff0 and cpu.memory[0x3d8] == 0
            cases.append(dict(entry=hex(entry), before=counter, after=0))
    life_cases = []
    for turtle in range(4):
        for counter in (0, 1, 23, 24, 25, 255):
            cpu = MPU(); cpu.memory[0xc000:] = raw[16 + 7 * 16384:16 + 8 * 16384]
            cpu.memory[0x3d8] = counter; cpu.memory[0x67] = turtle; cpu.pc = 0xccd7
            equipment, ammo = [1, 2, 3, 4], [20, 40, 60, 80]
            cpu.memory[0xa8:0xac] = equipment
            cpu.memory[0x73:0x77] = ammo
            for _ in range(100):
                if cpu.pc == 0xccf7:
                    break
                cpu.step()
            equipment[turtle] = ammo[turtle] = 0
            assert cpu.pc == 0xccf7 and cpu.memory[0x3d8] == counter
            assert cpu.memory[0xa8:0xac] == equipment and cpu.memory[0x73:0x77] == ammo
            life_cases.append(dict(turtle=turtle, counter_before=counter, counter_after=counter,
                                   only_selected_equipment_and_ammo_cleared=True))
    script = OUT / 'native.lua'
    script.write_text('''-- Original ROM unchanged. Read-only scene/reset observer.
local f=0;local log=assert(io.open(TEST_DIR..'native.csv','w'))
log:write('frame,mode,submode,inside,stage,turtle,x,y,counter\\n')
local calls=assert(io.open(TEST_DIR..'calls.csv','w'))
calls:write('frame,pc,counter,inside,stage,stack\\n')
local function r(a)return emu.read(a,emu.memType.nesDebug)end
for _,pc in ipairs({0xc57e,0xc5b8,0xc62b,0xc65c,0xc66d,0xcd74,0xc6fb})do
 emu.addMemoryCallback(function()
  local s=emu.getState();local stack={}
  for i=1,12 do stack[#stack+1]=string.format('%02x',r(0x100+(s['cpu.sp']+i)%256))end
  calls:write(f..','..pc..','..r(0x3d8)..','..r(0x5c)..','..r(0x48)..','..table.concat(stack)..'\\n');calls:flush()
 end,emu.callbackType.exec,pc)
end
emu.addEventCallback(function()
 emu.setInput({start=(f>=60 and f<65)or(f>=150 and f<155),
  right=f>=360 and f<440,down=f>=480 and f<620},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1;local v={f}
 for _,a in ipairs({0x1a,0x1b,0x5c,0x48,0x67,0x480,0x460,0x3d8})do v[#v+1]=r(a)end
 log:write(table.concat(v,',')..'\\n')
 if f%120==0 then local p=assert(io.open(TEST_DIR..'frame-'..f..'.png','wb'));p:write(emu.takeScreenshot());p:close()end
 if f==840 then log:close();calls:close();emu.stop(0);return end
end,emu.eventType.endFrame)
''')
    spec = importlib.util.spec_from_file_location('ny_mesen', ROOT / 'tools/run_mesen.py')
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner); runner.ROOT = OUT
    if args.sewer_route:
        text = script.read_text().replace(
            '0xc66d,0xcd74,0xc6fb', '0xc66d,0xcd74,0xc6d2,0xc6d6')
        text = text.replace('right=f>=360 and f<440,down=f>=480 and f<620',
                            'right=f>=360 and f<440,left=f>=650 and f<716,up=f>=720 and f<734,'
                            'down=(f>=480 and f<620)or(f>=760 and f<780)')
        text = text.replace('up=f>=720 and f<734',
                            'up=(f>=720 and f<734)or(f>=800 and f<890)')
        text = text.replace('f==840', 'f==1500')
        script.write_text(text)
    if args.counter_marker:
        text = script.read_text().replace('Read-only scene/reset observer.',
            'Scene/reset observer with one explicitly declared counter marker at frame630.')
        text = text.replace('f=f+1;local v={f}',
            "f=f+1;if f==630 then assert(r(0x5c)==0 and r(0x48)==0);"
            "emu.write(0x3d8,23,emu.memType.nesDebug)end;local v={f}")
        script.write_text(text)
    code = runner.run(script, source, timeout=50, emulator_options=['--nes.ramPowerOnState=AllZeros',
                      '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
    transitions = None
    if args.counter_marker and args.sewer_route and code == 0:
        rows = list(csv.DictReader((OUT / 'native.csv').open()))
        marked = [r for r in rows if int(r['frame']) >= 630]
        assert all(int(r['counter']) == 23 for r in marked)
        entry = next(r for r in marked if int(r['inside']) == 1)
        back = next(r for r in marked if int(r['frame']) > int(entry['frame']) and int(r['inside']) == 0)
        calls = list(csv.DictReader((OUT / 'calls.csv').open()))
        assert not [r for r in calls if int(r['frame']) >= 630]
        transitions = dict(counter_marker_preserved=23, first_sewer_entry_frame=int(entry['frame']),
                           first_sewer_exit_frame=int(back['frame']), generic_clear_calls_during_route=0,
                           scope='Actual controller-driven first sewer entry and exit only.')
    report = dict(passed=code == 0, source_ROM_sha256=hashlib.sha256(raw).hexdigest(),
                  original_generic_clear_cases=cases, native_exit=code,
                  original_life_branch_CCD7_to_CCF7_cases=life_cases,
                  native_first_sewer_counter_lifetime=transitions,
                  declared_RAM_fixture={'frame':630, 'address':'0x03D8', 'value':23} if args.counter_marker else None,
                  native_script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
                  scope='Direct original linked reset-code execution plus bounded native scene/caller observation. No every-transition lifetime claim.')
    (OUT / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
