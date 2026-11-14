"""Source-only Iron near-peak mount; normal controls, no helper placement."""
import argparse
import json
from unittest.mock import patch

import check_contra_force_completed_full11_1114 as Previous
import replay_contra_force_iron_mount_full11_1114 as Factory


def metadata(raw,key='iron'):
    with patch.object(Previous,'Factory',Factory):q=Previous.metadata(raw,key)
    text=Factory.controller(raw,key);prefix=text.split(Factory.MARKER,1)[0]
    rt=Factory.Frozen.LuaRuntime(unpack_returned_tuples=True);choose=rt.execute(prefix+'\nreturn choose')
    def c(**kw):
        d=dict(update=2600,x=2177,y=128,world=0,level=0,areaType=1,grounded=True,heldA=False)
        d.update(kw);v=rt.table_from(d);v.enemy=lambda:None;v.block=lambda x,y:0x54 if y>=208 else 0
        return v
    b,phase=choose(c());assert b.right and b.a and phase=='mount-1-mount'
    b,phase=choose(c(update=2604,x=2192,y=90,grounded=False));assert not b.right and not b.left and b.a
    b,phase=choose(c(update=2625,x=2192,y=112));assert phase=='mount-1-release'and not b.a
    b,phase=choose(c(update=2629,x=2192,y=112));assert phase=='mount-1-cross'and b.right and b.a
    q['actual_generated_mount_decisions']=dict(passed=True,lower_step_fresh_A=True,
        earns_near_peak_alignment_before_released_fresh_cross=True,decision_fixture_not_physics_evidence=True)
    return q


def run(raw):
    metadata(raw)
    with patch.object(Previous,'Factory',Factory):return Previous.run(raw,'iron')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');args=p.parse_args()
    raw=Factory.ROM.read_bytes();info=metadata(raw);print(json.dumps(info,separators=(',',':')),flush=True)
    if not args.metadata:
        q=run(raw);print(json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Iron normal-input near-peak route did not pass'
