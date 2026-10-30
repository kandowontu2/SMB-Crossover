"""Remove measured host pixel-capture overhead, retaining every gameplay check.

The first native route timed out at1160frames while losslessly encoding919
screens. Keep that genuine prefix; capture at most8 named screens next time.
"""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]


def main():
    original = R / "tools/audit/current_roster_compact_11_v1.lua"
    target = R / "tools/audit/current_character_sparse_11_1030_v1.lua"
    assert not target.exists()
    text = original.read_text()
    start = text.index(" if entered and(c.level==0 or endpoint or failure)then\n")
    end = text.index(" lastPower=c.status\n", start)
    block = ''' local selected={}
 local function want(name,condition)
  if condition and not markers[name]then selected[#selected+1]=name end
 end
 if entered and(c.level==0 or endpoint or failure)then
  want('first-active',frame==menuReadyAt)
  want('mushroom',c.status==1)
  want('wall-contact',opt('CmWallGrace')>0 and c.status>0)
  want('flower',c.status==2)
  want('dash',opt('CmDashTimer')>0 or opt('CmState')==6)
  want('flagpole',c.level==0 and c.x>=3120)
  want('endpoint',endpoint)
  want('failure',failure~=nil or frame>=C.limit)
 end
 if #selected>0 then
  local screen=emu.getScreenBuffer();assert(#screen==256*240,'Actual full PPU dimensions')
  local t={};for i,v in ipairs(screen)do t[i]=string.pack('<I4',v)end;local raw=table.concat(t)
  captureStamp=stamp();full:write(raw);captures=captures+1
  for _,name in ipairs(selected)do mark(name,raw)end
 end
'''
    text = text[:start] + block + text[end:]
    old = "Controller-only current 1-1 to controlled 1-2. Selected PPU review remains separate; no every-item/ability/source-fidelity/FPS claim."
    assert text.count(old) == 1
    text = text.replace(old, "Controller-only current1-1 to controlled1-2 with every original native state/OAM/CHR/interrupt check retained. At most8 selected PPU screens, not an every-frame pixel recording; no exhaustive items/abilities/source-fidelity/FPS claim.")
    target.write_text(text)
    base = R / "tools/audit/current_character_route_1030_v2.py"
    wrapper = base.with_name("current_character_route_1030_v3.py")
    assert not wrapper.exists()
    text = base.read_text()
    old = "    C.navigation = navigation\n"
    assert text.count(old) == 1
    text = text.replace(old, old + '    C.SCRIPT = R / "tools/audit/current_character_sparse_11_1030_v1.lua"\n'
                        '    C.MARKERS = ["first-active", "mushroom", "wall-contact", "flower", "dash", "flagpole", "endpoint", "failure"]\n')
    wrapper.write_text(text)
    print(json.dumps(dict(observer=str(target), wrapper=str(wrapper),
                          original_observer_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                          original_hardware_state_checks_preserved=True,
                          maximum_PPU_screens=8, native_not_run=True)))


if __name__ == "__main__":
    main()
