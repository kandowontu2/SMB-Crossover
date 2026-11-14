"""Exact source Iron far-ledge replay; source fixtures use measured negative."""
import argparse
import json
from unittest.mock import patch

import check_contra_force_grounded_full11_1114 as Previous
import replay_contra_force_iron_full11_1114 as Factory


def metadata(raw,key='iron'):
    with patch.object(Previous,'Factory',Factory):q=Previous.metadata(raw,key)
    text=Factory.controller(raw,key)
    policy=text.split('local choose=(function()\n',1)[1].split('\nend)()\n',1)[0]
    rt=Factory.Frozen.LuaRuntime(unpack_returned_tuples=True);rt.globals().C=rt.table_from(dict(variant=2))
    choose=rt.eval('function(s)return assert(load(s))()end')(policy)
    c=rt.table_from(dict(update=2617,x=2229,y=112,world=0,level=0,areaType=1,grounded=True,heldA=False))
    c.block=lambda x,y:0x54 if y>=208 or((2192<=x<2208 or 2240<=x<2256)and y>=144)else 0
    c.enemy=lambda:None
    b,phase=choose(c)
    assert phase=='stair-1-far-landing'and b.right and not b.left and not b.a
    q['measured_Iron_negative_counterexample_component']=dict(passed=True,x=2229,y=112,
        actual_ground_on_far_ledge_continues_right=True,decision_fixture_not_physics_evidence=True)
    return q


def run(raw):
    metadata(raw)
    with patch.object(Previous,'Factory',Factory):return Previous.run(raw,'iron')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');args=p.parse_args()
    raw=Factory.ROM.read_bytes();info=metadata(raw);print(json.dumps(info,separators=(',',':')),flush=True)
    if not args.metadata:
        q=run(raw);print(json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Iron far-landing full-route source gate not passed'
