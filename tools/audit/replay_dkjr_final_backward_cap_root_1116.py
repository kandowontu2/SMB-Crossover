"""Use the authenticated original backward jump for final risers4..6."""
from hashlib import sha256
import json
from pathlib import Path

import replay_dkjr_descending_fourth_cap_root_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

C = Previous.C
PARENT_SHA = 'be07c26f85b722fd128b9c21d2a45092256749f172b95cd8fb5f6f2441d0f76e'
ABILITY = C.R/'tools/audit/plan_dkjr_backward_stair_input_1116.py'
ABILITY_SHA = '2ede0a2fcd5bd2314c6e7dd3b40b8794e0acce5fa4e1eb355eade097c8c77cf4'
H = lambda data: sha256(data).hexdigest()


def controller(raw, *, source=False):
    assert H(Path(Previous.__file__).read_bytes()) == PARENT_SHA
    assert H(ABILITY.read_bytes()) == ABILITY_SHA
    base = Previous.controller(raw, source=source)
    before = " if phase=='final-stairs'then\n  right=true"
    after = """ if phase=='final-stairs'then
  if rootFinalPrep and rootFinalPrep.riser~=finalRiser then rootFinalPrep=nil end
  if rootFinalPrep then
   local q=rootFinalPrep
   assert(updates-q.started<120,'Bounded original backward final-riser preparation '..finalRiser)
   if not q.stopped then
    hold=0
    if player>q.stage or ram(2,0x6d)~=0 then bits=2;return end
    assert(ram(2,0x71)~=2,'Original normal backward-jump mode')
    q.stopped=updates
   end
   local age=updates-q.stopped
   if age<4 then bits=0;return
   elseif age<12 then
    if not q.sent then
     q.sent=true;finalRiserStart=updates;finalRiserAttempts=finalRiserAttempts+1
     remember('final-backward-jump-'..finalRiser)
     events[#events].takeoff_stage=q.stage;events[#events].original_facing=ram(2,0x6d)
    end
    bits=129;return
   elseif not(settled and y==q.target and player>=q.anchor)then bits=1;return end
  end
  right=true"""
    marker = '  elseif settled and y==144-16*(finalRiser-1)then\n'
    prep = """   if finalRiser>=4 and finalRiser<=6 then
    local anchor=2912+16*(finalRiser-1)
    local stage=anchor-12
    if player>=stage then
     assert(finalRiserAttempts<4,'Repeated original final-riser preparation')
     rootFinalPrep={riser=finalRiser,anchor=anchor,stage=stage,target=y-16,started=updates}
     hold=0;bits=2;return
    end
   end
"""
    edits = [('local finalRiser,finalRiserStart,finalRiserAttempts=1,nil,0',
              'local finalRiser,finalRiserStart,finalRiserAttempts=1,nil,0\nlocal rootFinalPrep'),
             (before, after), (marker, marker+prep)]
    text = base
    for old, new in edits:
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)
    restored = text
    for old, new in reversed(edits):
        assert restored.count(new) == 1
        restored = restored.replace(new, old, 1)
    assert restored == base
    LuaRuntime().compile(text)
    assert not any(x in text for x in ('emu.write', 'emu.setState', 'io.open', 'takeScreenshot', 'loadState', 'saveState'))
    return text


if __name__ == '__main__':
    raw, _ = C.proposal(C.BT.ROM.read_bytes())
    text = controller(raw)
    print(json.dumps(dict(factory_SHA256=H(Path(__file__).read_bytes()), Lua_SHA256=H(text.encode()),
                          candidate_SHA256=H(raw), ability_contract_SHA256=ABILITY_SHA,
                          exact_parent_control_restoration=True, new_game_bytes=0, new_helpers=0, outputs=0)))
