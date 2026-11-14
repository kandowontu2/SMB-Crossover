"""Real cold/menu/Main Prince pipe diagnostics; no gameplay state seeds/files.

The source peripheral model uses the existing menu arena and CPU frame
schedule. It cannot establish physical controller cadence or raster quality.
"""
from hashlib import sha256
import argparse,json
from unittest.mock import patch

import replay_prince_pipe_usability_1114 as Factory
import check_prince_natural_sword_1113 as P


def cold(raw):
    Factory.authenticate(raw)
    def proof(image):
        assert image==raw
        return raw
    with patch.object(P,'proof_parent',proof):
        return P.cold(raw)


def run(raw,*,brake=572,pad=8,hold=180,limit=4200,target=2,approach='brake',seed=None):
    text=Factory.controller(raw,brake=brake,pad=pad,hold=hold,target=target,approach=approach)
    if seed is None:m,opening=cold(raw)
    else:
        m=P.N.fork(seed);opening=dict(actual_executed_first_pipe_checkpoint=True)
        old="  assert(initial.x==40 and initial.lives==2 and initial.hp==5,'Authentic starting position, health and lives')"
        assert text.count(old)==1
        lo,hi=(390,448)if target==1 else(496,608)
        text=text.replace(old,f"  assert(initial.x>={lo} and initial.x<{hi} and initial.lives==2 and initial.hp==5,'Genuine source prefix')")
        text=text.replace("  switch('settle-start',0)","  switch('usability-approach',1)"if target==1 else"  firstPipe=initial;switch('later-approach',1)")
    receipts=[];loads=json.loads
    def capture(*a,**kw):
        q=loads(*a,**kw)
        if isinstance(q,dict) and 'later_route'in q:receipts.append(q)
        return q
    with patch.object(P,'controller',lambda image:text),patch.object(P.json,'loads',capture):
        q=P.route(m,raw,limit)
    # The frozen source driver exposes a selected receipt subset. The full
    # diagnostic body remains available in the unchanged emitted Lua receipt.
    q.update(metadata=Factory.metadata(raw,brake=brake,pad=pad,hold=hold,target=target,approach=approach),opening=opening,
        terminal_source=dict(x=P.N.get(m,'Player_X_Position')+256*P.N.get(m,'Player_PageLoc'),
            y=P.N.get(m,'Player_Y_Position'),action=m.ram[2][0x616],pose=m.ram[2][0x617],
            mode=m.ram[2][0x618],health=m.ram[2][0x6cf],lives=P.N.get(m,'NumberofLives'),
            source_x=int.from_bytes(m.ram[2][0x60f:0x611],'little')),
        Mesen=False,outputs=0)
    assert len(receipts)==1
    observation=receipts[0].get('later_route',{}).get('usability',{})
    q['observation']=observation
    q['receipt_SHA256']=sha256(json.dumps(receipts[0],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q,m


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--brake',type=int,default=572);p.add_argument('--pad',type=int,default=8)
    p.add_argument('--hold',type=int,default=180);p.add_argument('--metadata',action='store_true')
    p.add_argument('--target',type=int,choices=(1,2),default=2)
    p.add_argument('--approach',choices=('brake','contact','prefix'),default='brake')
    p.add_argument('--matrix',action='store_true')
    args=p.parse_args();raw=Factory.ROM.read_bytes()
    if args.matrix:
        prefix,seed=run(raw,approach='prefix',target=args.target)
        print(json.dumps(dict(event='prefix',passed=prefix['passed'],terminal=prefix['terminal'],receipt=prefix['receipt_SHA256'])),flush=True)
        assert prefix['passed']
        for pad in(8,9,136):
            q,_=run(raw,pad=pad,approach='contact',target=args.target,seed=seed)
            samples=q['observation'].get('samples',[])
            q['observation']['samples']=samples[::8]if isinstance(samples,list)else[]
            q.pop('events',None)
            print(json.dumps(q,separators=(',',':')),flush=True)
        raise SystemExit(0)
    kwargs=dict(brake=args.brake,pad=args.pad,hold=args.hold,target=args.target,approach=args.approach)
    q=Factory.metadata(raw,**kwargs)if args.metadata else run(raw,**kwargs)[0]
    if not args.metadata:
        samples=q['observation'].get('samples',[])
        q['observation']['samples']=samples[::8]if isinstance(samples,list)else[];q.pop('events',None)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'Observation itself did not complete'
