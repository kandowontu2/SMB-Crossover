"""Extend the existing bounded native runner to the staged28-slot menu.

Preparation only. The calling root launches exactly one native worker after
reviewing the ready receipt. Historical tool files and proofs are unchanged.
"""
from pathlib import Path
import argparse, json
import current_roster_compact_11_v1 as base

ROOT=base.ROOT


def navigation(raw, location, target):
    count=28
    edges={key:list(raw[location('X5Menu'+key.title()):location('X5Menu'+key.title())+count]) for key in ('left','right','up','down')}
    present=list(raw[location('X5MenuPresent'):location('X5MenuPresent')+count])
    assert present[target]
    result=[]
    for start in range(count):
        if not present[start]:
            result.append('');continue
        queue,seen=[(start,[])],{start}
        for node,route in queue:
            if node==target:
                result.append(route[0] if route else '');break
            for key,table in edges.items():
                next_node=table[node]
                assert 0<=next_node<count and present[next_node]
                if next_node not in seen:
                    seen.add(next_node);queue.append((next_node,route+[key]))
        else:
            raise AssertionError('Unreachable compiled menu profile')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--identity',choices=['popo','nana'],default='popo')
    p.add_argument('--mode',choices=['easy','hard'],default='easy')
    p.add_argument('--frames',type=int,default=1600)
    p.add_argument('--policy',type=Path,default=ROOT/'tools/playthroughs/full_roster_policy_og.lua')
    a=p.parse_args();a.replay=None
    if a.smoke:
        assert a.identity=='popo' and a.mode=='easy'
    base.BASE.update(popo=(19,20,'IcVariant',0),nana=(19,20,'IcVariant',1))
    base.navigation=navigation
    base.prepare(a)
    ready=a.output.resolve()/'ready.json';record=json.loads(ready.read_text())
    if a.smoke:
        script=ROOT/'tools/audit/roster_expansion_smoke_v1.lua'
        body='ROSTER_CONFIG='+base.lua(record['config'])+'\n'
        body+='for name,value in pairs(ROSTER_CONFIG.extra_ram)do assert(L[name]==nil or L[name]==value);L[name]=value end\n'
        # Equates used only by this smoke script must come from the actual DBG.
        _,_,address,_,_=base.linked(a.rom.resolve())
        for name in ['IcVariant','TimerControl','Block_Buffer_1']:
            body+='L['+base.lua(name)+']='+str(address(name))+'\n'
        body+='dofile('+base.lua(script.as_posix())+')\n'
        run=a.output.resolve()/'run.lua';run.write_text(body)
        record['bindings'][str(run)]=base.sha(run)
        record['bindings'][str(script)]=base.sha(script)
        record['explicit_endpoint']='Natural Popo/Nana/Popo preview toggles, genuine Start and480 active opening updates; no full-level claim'
        record['maximum_offline_selected_frames']=8
        record['container_cap_bytes']=0
        record['max_total_frames']=a.frames
    record['bindings'][str(Path(__file__).resolve())]=base.sha(__file__)
    record['staged_new_roster']=True
    ready.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(ready=str(ready),sha256=base.sha(ready),endpoint=record['explicit_endpoint'])))


if __name__=='__main__':
    main()
