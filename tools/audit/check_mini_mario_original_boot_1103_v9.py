"""Read-only original-GB parameter binding; one screenshot, no RAM dumps."""
from pathlib import Path
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/mini-mario-original-1103-v9'
ROM = Path('C:/Users/kando/Downloads/SuperMarioBrosMini.gb')
EXPECTED = '837d39a438f85c5b3ef32c4e41c6c4403147046a7e93bdeac039a09a4a202c81'

LUA = r'''
local frames=0
local matches={}
local mt=assert(emu.memType.gameboyDebug,'Game Boy CPU debug memory')
-- Exact declaration order from preserved platform.c, source defaults plus overrides.
local parameters={0,1,81,14,226,21,0,16,128,0,0,1,0,1,0,48,0,8,0,2,0,32}
local observations={}
local function inspect()
 local hits={}
 for address=0xC000,0xDFFF-#parameters+1 do
  local good=true
  for i,value in ipairs(parameters)do
   if emu.read(address+i-1,mt)~=value then good=false;break end
  end
  if good then
   hits[#hits+1]=address
   matches[address]=true
  end
 end
 local cells={}
 for _,address in ipairs(hits)do cells[#cells+1]=tostring(address)end
 observations[#observations+1]='{"frame":'..frames..',"parameter_base_addresses":['..table.concat(cells,',')..']}'
end
emu.addEventCallback(function()
 local pad={}
 if frames>=180 and frames<184 then pad.start=true end
 if frames>=700 and frames<820 then pad.right=true;pad.b=true end
 if frames>=730 and frames<758 then pad.a=true end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frames=frames+1
 assert(frames<=1200,'Original reference frame bound')
 if frames==300 or frames==600 or frames==1000 then inspect()end
 if frames==1000 then
  local png=assert(io.open(OUTPUT..'original-gameboy.png','wb'));png:write(emu.takeScreenshot());png:close()
 end
 if frames==1200 then
  local unique=0;for _ in pairs(matches)do unique=unique+1 end
  local f=assert(io.open(OUTPUT..'parameter-observation.json','w'))
  f:write('{"frames":'..frames..',"unique_matches":'..unique..',"observations":['..table.concat(observations,',')..']}\n');f:close()
  assert(unique==1,'One exact22B live original parameter block expected')
  print('PASS originalGB live parameter block, including hold gravity512; no instruction equivalence claim')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
'''


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    assert sha(ROM) == EXPECTED
    assert not any(ROM.with_suffix(s).exists() for s in ('.ips','.bps','.ups'))
    script = OUT/'original.lua'
    script.write_text(LUA,encoding='utf-8')
    sys.path[:0] = [str(ROOT/'tools'),str(ROOT/'tools/audit')]
    from mesen_session_guard_v1 import require_free_workspace
    from run_mesen import run
    sessions = require_free_workspace(ROOT,ROM,allow_interactive=True)
    (OUT/'sessions-before.json').write_text(json.dumps(sessions,indent=2)+'\n')
    os.environ['SMB_RUN_OUTPUT'] = str(OUT/'capture')
    code = run(script,ROM,timeout=45,emulator_options=['--doNotSaveSettings'])
    assert sha(ROM) == EXPECTED
    observed = json.loads((OUT/'capture/parameter-observation.json').read_text()) if (OUT/'capture/parameter-observation.json').exists() else None
    result = dict(passed=code==0,original_GB_reference_only=True,ROM_SHA256=EXPECTED,
        exit_code=code,observation=observed,emulated_memory_writes=False,screenshot_count=1,
        scope='Actual original Game Boy ROM cold boot/controller observation and exact live22B parameter-pattern binding only. No RAM/PPU dumps or frame sequences. This is not Game Boy-versus6502 CPU instruction equivalence, original-source compilation, native NES gameplay or a nightly update.',
        bindings={str(p.resolve()):sha(p) for p in (ROM,Path(__file__),script,
            ROOT/'tools/run_mesen.py',ROOT/'tools/audit/capture_budget.py',ROOT/'tools/audit/mesen_session_guard_v1.py')})
    (OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))
    raise SystemExit(code)


if __name__=='__main__':
    main()
