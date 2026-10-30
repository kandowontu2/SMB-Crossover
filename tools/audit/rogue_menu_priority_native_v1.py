"""Cold native all80 sweep with an explicit physical Rogue preview check."""
from pathlib import Path
import json
import os
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
import rogue_current_native_v1 as base

O = R/'build/rogue-current-menu-v6'


def main():
    out = O/'native/menu'
    assert not out.exists()
    controls = json.loads((O/'preview-priority-controls.json').read_text())
    digest = base.sha(O/'candidate.nes')
    assert controls['passed'] and controls['ROM_sha256'] == digest
    template = R/'tools/audit/full_roster_menu_native_v1.lua'
    code = template.read_text()
    def replace(old, new):
        nonlocal code
        assert code.count(old) == 1, old
        code = code.replace(old, new)
    replace('(s==2 or s==7 or s==11)and v==1', '(s==7 or s==11)and v==1')
    replace("else add('',s,0,'initial')end", "else add('',s,0)end")
    replace("(s==28 and v==1 and 'wwf-alt')", "(s==2 and v==1 and 'rogue-preview')or(s==28 and v==1 and 'wwf-alt')")
    replace("  shot(s.tag);at=at+1;age=0", '''  if s.slot==2 and s.variant==1 then
   local parts=0
   for i=0,63 do
    local y=emu.read(i*4,emu.memType.nesSpriteRam)
    if y>=144 and y<192 then
     local x=emu.read(i*4+3,emu.memType.nesSpriteRam)
     if x>=110 and x<=145 then
      assert(emu.read(i*4+2,emu.memType.nesSpriteRam)&32==0,'Physical Rogue preview priority')
      parts=parts+1
     end
    end
   end
   assert(parts==5,'All five genuine Rogue preview parts reach hardware OAM')
  end
  shot(s.tag);at=at+1;age=0''')
    replace("'{\"passed\":true,\"frames\":%d", "'{\"ROM_sha256\":\""+digest+"\",\"Rogue_hardware_parts\":5,\"passed\":true,\"frames\":%d")
    out.mkdir(parents=True)
    controller = out/'controller.lua'
    controller.write_text(code, newline='\n')
    inputs = {str(p): base.sha(p) for p in [Path(__file__).resolve(), template,
              controller, O/'controls.json', O/'preview-priority-controls.json']}
    os.environ['SMB_RUN_OUTPUT'] = str(out)
    result = base.run(controller, O/'candidate.nes', timeout=180, emulator_options=[
        '--doNotSaveSettings', '--nes.removeSpriteLimit=false', '--nes.ramPowerOnState=AllZeros',
        '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
    assert base.sha(O/'candidate.nes') == digest
    for path, expected in inputs.items():
        assert base.sha(path) == expected, path
    (out/'binding.json').write_text(json.dumps(dict(ROM_sha256=digest, exit_code=result,
        no_native_RAM_writes=True, normal_sprite_limit=True, inputs=inputs), indent=2)+'\n')
    raise SystemExit(result)


if __name__ == '__main__':
    main()
