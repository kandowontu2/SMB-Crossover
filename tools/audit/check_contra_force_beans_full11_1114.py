"""Source-only Beans stair-phase successor; no seeded gameplay state."""
import argparse
import json
from unittest.mock import patch

import check_contra_force_full11_v2_1114 as Previous
import replay_contra_force_beans_full11_1114 as Factory


def metadata(raw,key='beans'):
    with patch.object(Previous,'Factory',Factory):q=Previous.metadata(raw,key)
    text=Factory.controller(raw,key)
    policy=text.split('local choose=(function()\n',1)[1].split('\nend)()\n',1)[0]
    rt=Factory.Frozen.LuaRuntime(unpack_returned_tuples=True);rt.globals().C=rt.table_from(dict(variant=3))
    choose=rt.eval('function(s)return assert(load(s))()end')(policy)
    def context(**kw):
        c=dict(update=1838,x=2173,y=105,world=0,level=0,areaType=1,grounded=False,heldA=False)
        c.update(kw);ctx=rt.table_from(c)
        ctx.block=lambda x,y:0x54 if y>=208 or(2192<=x<2208 and y>=144)else 0
        ctx.enemy=lambda:None
        return ctx
    b,phase=choose(context());assert phase=='travel','Falling above lower step must not enter landing wait'
    b,phase=choose(context(update=1840,x=2192,y=112,grounded=True));assert phase=='stair-1-land'
    b,phase=choose(context(update=1844,x=2192,y=112,grounded=True));assert phase=='stair-1-cross'and b.a
    q['local_actual_generated_policy_phase_components']=dict(passed=True,
        falling_case_rejected=True,genuine_ground_peak_then_released_cross=True,
        decision_fixtures_not_gameplay_or_physics_evidence=True)
    return q


def run(raw,key='beans'):
    metadata(raw,key)
    with patch.object(Previous,'Factory',Factory):return Previous.run(raw,key)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');args=p.parse_args()
    raw=Factory.ROM.read_bytes();info=metadata(raw)
    print(json.dumps(info,separators=(',',':')),flush=True)
    if not args.metadata:
        q=run(raw);print(json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Beans full-route source gate not passed'
