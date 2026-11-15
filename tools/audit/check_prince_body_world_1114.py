"""Actual auth/cold/Main controller qualification of the fitted Prince image.

Everything stays in memory. Menu unit peripheral limits and native cadence
remain distinct; no gameplay position/health/actor/terrain seeds are supplied.
"""
from hashlib import sha256
import argparse,json
from unittest.mock import patch
import compose_prince_body_world_1114 as C
import replay_prince_body_world_1114 as Factory
import check_prince_natural_sword_1113 as P
import check_prince_pipe_usability_1114 as Legacy

N=P.N


def cold(raw):
    Factory.authenticate(raw)
    with patch.object(P,'proof_parent',lambda image:raw if image==raw else (_ for _ in()).throw(AssertionError('Wrong cold image'))):
        model,opening=P.cold(raw)
    q=C.allocation();cookie=raw[C.Build.Old.Packet.COOKIE:C.Build.Old.Packet.COOKIE+16]
    assert all(bytes(model.ram[k][0x1fe0:0x1ff0])==cookie for k in(2,3))
    for span in q['decoded_spans']:
        lo,hi=span['live_CPU_half_open'];bank=span['live_RAM_bank']
        # Both granted extents remain within their single 8K work page.
        actual=bytes(model.ram[bank][lo&8191:(lo&8191)+(hi-lo)])
        assert C.digest(actual)==span['proposed_SHA256'],span['name']
    return model,dict(opening,headers_exact=True,granted_code_transport_exact=True,
        UI_scope='Compiled menu peripheral unit; actual vblank/native cadence separate')


def route(raw,model,*,mode='direct',pad=9,limit=4200,edge=432):
    text=Factory.controller(raw,mode=mode,pad=pad,edge=edge)
    receipts=[];loads=json.loads
    def capture(*a,**kw):
        q=loads(*a,**kw)
        if isinstance(q,dict)and'later_route'in q:receipts.append(q)
        return q
    with patch.object(P,'controller',lambda image:text),patch.object(P.json,'loads',capture):
        q=P.route(model,raw,limit)
    assert len(receipts)==1
    receipt=receipts[0];observation=receipt.get('later_route',{}).get('usability',{})
    samples=observation.get('samples',[])
    if isinstance(samples,list):observation['samples']=samples[::8]
    q.pop('events',None)
    marks=receipt.get('events',[])
    return dict(q,ROM_SHA256=C.digest(raw),mode=mode,pad=pad,
        controller_SHA256=sha256(text.encode()).hexdigest(),observation=observation,
        route_marks=marks,
        receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        observed_pipe_climb=bool(observation.get('hang')and observation.get('top')),
        no_gameplay_seeds=True,outputs=0,Mesen=False)


def run(parent,*,mode='direct',pad=9,edge=432):
    raw,info=C.proposal(parent);assert C.inverse(raw)==parent
    model,opening=cold(raw)
    return dict(composition=info,opening=opening,result=route(raw,model,mode=mode,pad=pad,edge=edge))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('direct','contact','pits','edge','pits-intuitive','earned','earned-intuitive-fourth'),default='direct')
    p.add_argument('--pad',type=int,choices=(1,8,9,129),default=9);p.add_argument('--matrix',action='store_true');p.add_argument('--followups',action='store_true');p.add_argument('--edge',type=int,default=432);a=p.parse_args()
    if a.matrix or a.followups:
        parent=Factory.ROM.read_bytes();raw,info=C.proposal(parent);assert C.inverse(raw)==parent
        model,opening=cold(raw)
        print(json.dumps(dict(event='composition-and-cold',composition=info,opening=opening),separators=(',',':')),flush=True)
        cases=(('edge',129,432),('edge',129,434),('earned',9,432))if a.followups else(('direct',1,432),('direct',129,432),('contact',8,432),('pits',9,432))
        for mode,pad,edge in cases:
            q=route(raw,N.fork(model),mode=mode,pad=pad,edge=edge)
            print(json.dumps(q,separators=(',',':')),flush=True)
    else:print(json.dumps(run(Factory.ROM.read_bytes(),mode=a.mode,pad=a.pad,edge=a.edge),separators=(',',':')),flush=True)
