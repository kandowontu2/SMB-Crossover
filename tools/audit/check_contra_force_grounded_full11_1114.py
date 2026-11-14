"""Source-only completed-ground CF full-stage controls; all four choices."""
import argparse
import json
from unittest.mock import patch

import check_contra_force_full11_v2_1114 as Previous
import replay_contra_force_grounded_full11_1114 as Factory


def metadata(raw,key):
    with patch.object(Previous,'Factory',Factory):q=Previous.metadata(raw,key)
    text=Factory.controller(raw,key)
    policy=text.split('local choose=(function()\n',1)[1].split('\nend)()\n',1)[0]
    rt=Factory.Frozen.LuaRuntime(unpack_returned_tuples=True)
    rt.globals().C=rt.table_from(dict(variant=Factory.IDENTITIES[key][1]))
    choose=rt.eval('function(s)return assert(load(s))()end')(policy)
    def context(**kw):
        c=dict(update=1838,x=2173,y=105,world=0,level=0,areaType=1,grounded=False,heldA=False)
        c.update(kw);ctx=rt.table_from(c)
        ctx.block=lambda x,y:0x54 if y>=208 or(2192<=x<2208 and y>=144)else 0
        ctx.enemy=lambda:None
        return ctx
    b,phase=choose(context());assert phase=='travel'
    b,phase=choose(context(update=1840,x=2192,y=112,grounded=True));assert phase=='stair-1-land'
    b,phase=choose(context(update=1844,x=2192,y=112,grounded=True));assert phase=='stair-1-cross'and b.a
    q['actual_generated_policy_components']=dict(passed=True,falling_does_not_enter_landing_wait=True,
        actual_ground_peak_admitted_then_fresh_jump=True,decision_fixtures_not_physics_evidence=True)
    return q


def run(raw,key):
    metadata(raw,key)
    with patch.object(Previous,'Factory',Factory):return Previous.run(raw,key)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,required=True)
    p.add_argument('--metadata',action='store_true');args=p.parse_args();raw=Factory.ROM.read_bytes()
    info=metadata(raw,args.identity);print(json.dumps(info,separators=(',',':')),flush=True)
    if not args.metadata:
        q=run(raw,args.identity);print(json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'CF completed-ground full-route source gate not passed'
