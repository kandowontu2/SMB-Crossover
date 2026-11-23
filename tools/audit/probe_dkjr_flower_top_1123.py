"""Bounded real-menu DK Flower upper-turn inspection; no gameplay writes.

The first mode preserves every pad from the frozen failed policy and only
adds bounded read-only launch-gate samples, stopping after the upper turn.
"""
from pathlib import Path
from unittest.mock import patch
import json
import probe_dkjr_flower_helper_1123 as Previous

C,Check,Head,H=Previous.C,Previous.Check,Previous.Head,Previous.H
PREVIOUS_SHA='c4872bc1380b83577ed3760d8d6de11bcfd61618a11acdccf7c301b58d81c0d1'
COMPOSER_SHA='b8e043769a15ebcebb36e50b3d5eb255dc305783f95ad077638f59d880952395'
BASE_CONTROLLER=Previous.controller

GATES=r'''
  local d=flower.launch_probe
  if not d then d={minimum=255,count=0};flower.launch_probe=d end
  if top<=170 then
   d.started=d.started or updates
   local minimum=top<d.minimum;d.minimum=math.min(d.minimum,top)
   local key=table.concat({player,y,top,ram(2,0x210),ram(2,0x6b),ram(2,0x6c),
    read(0x1e),ram(2,0x6d),ram(2,0x14),a.state},':')
   if d.count<32 and(minimum or(top<=162 and key~=d.last))then
    d.count=d.count+1;d.last=key
    events[#events+1]={event='flower-launch-gate',Main=updates,x=player,y=y,top=top,
     source_y=ram(2,0x210),source=ram(2,0x6b),prior=ram(2,0x6c),
     native_state=read(0x1e),facing=ram(2,0x6d),held=ram(2,0x14),item_state=a.state,
     x_gate=player>=1291 and player<=1293,face_gate=ram(2,0x6d)==1,
     ride=ride,ground=ground,released=released,mature=a.state&128~=0,
     height_gate=top>=146 and top<=160,footer=y+32,source_footer=ram(2,0x210)+17}
   end
  end
  if d.started and top>d.minimum+5 and updates-d.started>16 then
   finish(false,'Read-only upper-turn launch inspection complete; minimum '..d.minimum)
   return 0
  end
'''


def pins():
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    assert H(Path(C.__file__).read_bytes())==COMPOSER_SHA


def controller(raw):
    pins();text=BASE_CONTROLLER(raw)
    marker=" if flower.phase=='side-position'then\n  assert(a,'Flower is present at the clear-side staging point')\n"
    result=Check.Replay.one(text,marker,marker+GATES)
    assert Check.Replay.one(result,marker+GATES,marker)==text
    assert not any(t in result for t in ('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    Check.LuaRuntime().compile(result)
    return result


def main():
    pins();parent=C.Old.M.ROM.read_bytes();raw,proposal=C.proposal(parent)
    print('DK FLOWER UPPER BINDING '+json.dumps(dict(proposal=proposal,prior_source=PREVIOUS_SHA,
        composer_source=COMPOSER_SHA,diagnostic_only=True,ordinary_pads_unchanged=True,outputs=0),separators=(',',':')),flush=True)
    with patch.object(Previous,'controller',controller):q=Previous.run(raw)
    q.update(source_SHA256=H(Path(__file__).read_bytes()),diagnostic_only=True,ordinary_pads_unchanged=True)
    print('DK FLOWER UPPER '+json.dumps(q,separators=(',',':')),flush=True)
    print('RECEIPT '+H(json.dumps(q,sort_keys=True,separators=(',',':')).encode()),flush=True)


if __name__=='__main__':main()
