"""Run the explicit three-field Karnov stock fixture under capture limits."""

from hashlib import sha256
import argparse
import json
from pathlib import Path

import capture_budget as Budget
from mesen_session_guard_v1 import require_free_workspace
from replay_karnov_bomb_1112 import R, controller


OUTPUT = R/'build/metal-flower-native-1112'
PIN = '318a087735b4204c74274b4107efbc302bc15a674a7f6f9d3bed598cea90d08d'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contact', action='store_true')
    parser.add_argument('--rom', type=Path, default=OUTPUT/'candidate.nes')
    args = parser.parse_args()
    rom = args.rom
    raw = rom.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    text = controller(raw, 'fixture')
    if args.contact:
        text = text.replace('local phaseFrames, phaseCodes = {}, {}',
                            'local phaseFrames, phaseCodes, enemyTrace = {}, {}, {}')
        text = text.replace('"minimum_contact_SP":%d}', '"enemy_trace":[%s],"minimum_contact_SP":%d}')
        text = text.replace('hit,nearby,bombX,bombY,minimumSP))',
                            "hit,nearby,bombX,bombY,table.concat(enemyTrace,','),minimumSP))")
        text = text.replace("    phaseCodes[#phaseCodes+1]=code;phaseFrames[#phaseFrames+1]=updates", '''    phaseCodes[#phaseCodes+1]=code;phaseFrames[#phaseFrames+1]=updates
    if code>=129 then
     for slot=0,5 do
      if r('Enemy_Flag',slot)==1 and r('Enemy_ID',slot)==6 then
       local ex=r('Enemy_PageLoc',slot)*256+r('Enemy_X_Position',slot)
       local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
       local oam={}
       for at=0,252,4 do
        local ox=emu.read(at+3,emu.memType.nesSpriteRam)
        local oy=emu.read(at,emu.memType.nesSpriteRam)
        if oy<240 and math.abs(ox-(ex-camera))<=16 then
         oam[#oam+1]=string.format('[%d,%d,%d]',ox,oy,emu.read(at+1,emu.memType.nesSpriteRam))
        end
       end
       enemyTrace[#enemyTrace+1]=string.format('{"phase":%d,"x":%d,"nativeY":%d,"bombSourceY":%d,"oam":[%s]}',code,ex,r('Enemy_Y_Position',slot),source(0xc2),table.concat(oam,','))
      end
     end
    end''')
        old = "  if phase=='choose' then pad.select=true"
        assert text.count(old) == 1
        text = text.replace(old, "  if phase=='seed' then pad.right=true\n  elseif phase=='choose' then pad.select=true")
        text = text.replace("elseif phase=='retreat' then pad.right=world()<initial+36 end",
                            "elseif phase=='retreat' then pad.left=world()>initial-60 end")
        old = "   if phase=='seed' and timer>=4 and r('Player_State')==0 then"
        assert text.count(old) == 1
        text = text.replace(old, '''   local inRange=false
   for slot=0,5 do
    local dx=r('Enemy_PageLoc',slot)*256+r('Enemy_X_Position',slot)-world()
    if r('Enemy_Flag',slot)==1 and r('Enemy_ID',slot)==6 and dx>=48 and dx<=60 then inRange=true end
   end
   if phase=='seed' and timer>=4 and r('Player_State')==0 and inRange then''')
        text = text.replace("and visible[128] and (visible[130] or visible[131])",
                            "and visible[128] and (visible[130] or visible[131]) and hit>0")
    assert text.count('emu.write(') == 3
    for offset, value in ((0x8e, 255), (0x8f, 2), (0xbb, 1)):
        assert f'emu.write(2*8192+0x{offset:x},{value},emu.memType.nesWorkRam)' in text
    # The stock fixture seeds only three declared source values after real
    # character selection. All movement, arming, timing and rendering run live.
    prefix = '''local addMemory,addEvent=emu.addMemoryCallback,emu.addEventCallback
local failed=false
local function guarded(fn)
 return function(...)
  if failed then return end
  local ok,why=pcall(fn,...)
  if not ok then
   failed=true
   print('KARNOV_FIXTURE_ERROR '..tostring(why))
   print('SMB_NATIVE_RECEIPT {"passed":false,"fixture":true,"reason":"callback-error"}')
   emu.stop(1)
  end
 end
end
emu.addMemoryCallback=function(fn,...)return addMemory(guarded(fn),...)end
emu.addEventCallback=function(fn,...)return addEvent(guarded(fn),...)end
'''
    script = OUTPUT/'controller.lua'
    script.write_text(prefix + text, encoding='utf-8', newline='\n')
    script_pin = sha256(script.read_bytes()).hexdigest()
    other = require_free_workspace(R, rom, allow_interactive=True)
    command = ['C:/mesen2/Mesen.exe', '--testRunner', '--enableStdout', '--timeout=60',
               '--doNotSaveSettings', '--nes.removeSpriteLimit=false',
               '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
               '--nes.randomizeMapperPowerOnState=false', str(script), str(rom)]
    result = Budget.run_capped(command, output=OUTPUT/'capture', timeout=75, reserved_files=1)
    receipts = [json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
                for line in result.stdout.splitlines() if line.startswith('SMB_NATIVE_RECEIPT ')]
    assert len(receipts) == 1, (result.returncode, result.stdout[-1500:], result.stderr[-1500:])
    receipt = receipts[0]
    assert sha256(rom.read_bytes()).hexdigest() == PIN
    assert sha256(script.read_bytes()).hexdigest() == script_pin
    report = dict(passed=bool(receipt['passed']), fixture=True,
                  script_SHA256=script_pin,
                  receipt_SHA256=sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest(),
                  receipt=receipt, other_processes_untouched=[p['ProcessId'] for p in other],
                  stderr=result.stderr[-1500:])
    print(json.dumps(report), flush=True)
    assert result.returncode == 0 and receipt['passed']
    assert receipt['ROM_SHA256'] == PIN and receipt['fixture_offsets'] == [142, 143, 187]
    return report


if __name__ == '__main__':
    main()
