"""Compare original odd-size MMC1 ROM and a private padded diagnostic copy."""
from pathlib import Path
import hashlib
import json
import os
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools'), str(R / 'tools/audit')]
import audit.capture_budget as B
import run_mesen

O = R / 'build/kamikaze-original-boot-1030-v1'
SOURCE = Path('C:/NES/the stash/Kamikaze_Mario_DX_Plus_V1.9_SMB1_Hack.nes')
EMU = R / 'build/verification/kamikaze-private-emulator-v1/Mesen.exe'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
LUA = r'''
local frame=0
local log=assert(io.open(OUTPUT..'cpu.csv','w'));log:write('frame,PC\n')
local function dump(a,n,k)local q={};for i=0,n-1 do q[#q+1]=string.char(emu.read(a+i,k))end;return table.concat(q)end
emu.addEventCallback(function()
 local p={}
 if(frame>=240 and frame<246)or(frame>=600 and frame<606)then p.start=true end
 emu.setInput(p,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame%30==0 then local s=emu.getState();log:write(frame..','..tostring(s['cpu.pc'])..'\n')end
 if frame==180 or frame==480 or frame==899 then
  local stem=OUTPUT..'frame-'..frame
  local f=assert(io.open(stem..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  f=assert(io.open(stem..'.bin','wb'));f:write(dump(0,8192,emu.memType.nesPpuDebug),dump(0x3f00,32,emu.memType.nesPpuDebug),dump(0,256,emu.memType.nesSpriteRam),dump(0,2048,emu.memType.nesDebug));f:close()
 end
 if frame>=900 then log:close();emu.stop(0);return end
end,emu.eventType.endFrame)
'''


def main():
    assert not O.exists()
    O.mkdir()
    raw = SOURCE.read_bytes()
    assert sha(SOURCE) == '5e866dab7fd0d3f402dff679748a68f9c98d32ffa6c970923be97b79f33617d1'
    assert raw[4:7] == bytes([5, 2, 16])
    # Original file is never changed. Keep all five original PRG banks and
    # place its genuine reset/menu bank at the last bank of a 128KiB image.
    header = bytearray(raw[:16])
    header[4] = 8
    padded = O / 'padded-diagnostic.nes'
    padded.write_bytes(header + raw[16:16 + 81920] + bytes(32768)
                       + raw[16 + 65536:16 + 81920] + raw[16 + 81920:])
    prior = B.preflight
    def preflight(output):
        return prior(output, reserved_bytes=512 * 1024 * 1024, reserved_files=64)
    B.preflight = preflight
    B.RUN_BYTES = 512 * 1024 * 1024
    B.PAYLOAD_BYTES = B.RUN_BYTES - 1000000
    options = ['--doNotSaveSettings', '--nes.removeSpriteLimit=false',
               '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
               '--nes.randomizeMapperPowerOnState=false']
    rows = []
    for name, rom in [('original', SOURCE), ('padded', padded)]:
        out = O / name
        out.mkdir()
        script = out / 'run.lua'
        script.write_text(LUA, newline='\n')
        os.environ['SMB_RUN_OUTPUT'] = str(out)
        code = run_mesen.run(script, rom, str(EMU), 60, emulator_options=options)
        row = dict(name=name, ROM=str(rom), ROM_sha256=sha(rom), exit_code=code,
                   script_sha256=sha(script), maximum_frames=900, screenshots=3,
                   no_emulated_state_writes=True, options=options)
        rows.append(row)
        (out / 'terminal.json').write_text(json.dumps(row, indent=2) + '\n')
        assert code == 0
    (O / 'comparison.json').write_text(json.dumps(dict(
        rows=rows, source_unchanged=sha(SOURCE) == '5e866dab7fd0d3f402dff679748a68f9c98d32ffa6c970923be97b79f33617d1',
        emulator=sha(EMU), runner=sha(R / 'tools/run_mesen.py'),
        scope='Private source-game boot diagnostic; no ROM release, game-code changes, or host gameplay claim.'
    ), indent=2) + '\n')
    print(json.dumps(rows))


if __name__ == '__main__':
    main()
