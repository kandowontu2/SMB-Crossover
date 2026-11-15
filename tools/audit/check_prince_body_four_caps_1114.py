"""Readonly metadata and genuine cold four-cap source replay, no outputs."""
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch
import check_prince_body_world_1114 as Game
import replay_prince_body_four_caps_1114 as Factory

C,P,N=Game.C,Game.P,Game.N


def run(current,*,source=False):
    attempts=[]
    def deny(*args,**kwargs):
        attempts.append(str(args[:1]));raise AssertionError('Unexpected output/launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,info=C.proposal(current.reference1daca);assert C.inverse(raw)==current.reference1daca
        assert C.Build.Old.Packet.extract(current.original)==C.Build.Old.Packet.extract(current.reference1daca)
        text=Factory.controller(raw);metadata=Factory.metadata(raw)
        assert not any(x in text for x in('pad=201','or 201'))
        bad=bytearray(raw);bad[16]^=1
        negatives=0
        for image in(current.original,bytes(bad)):
            try:Factory.controller(image)
            except AssertionError:negatives+=1
            else:raise AssertionError('Unknown image accepted')
        assert negatives==2 and not attempts
        q=dict(passed=True,metadata=metadata,composition=info,public_input=current.metadata(),
            negative_images=negatives,fallback_201_removed=True,write_or_launch_attempts=attempts,
            current_Prince_packet_exact=True,source_replay_executed=source,outputs=0,Mesen=False)
        if source:
            print(json.dumps(dict(event='readonly-metadata-passed',**q),separators=(',',':')),flush=True)
            model,opening=Game.cold(raw);receipts=[];loads=json.loads
            def capture(*args,**kwargs):
                value=loads(*args,**kwargs)
                if isinstance(value,dict)and'later_route'in value:receipts.append(value)
                return value
            with patch.object(P,'controller',lambda image:text),patch.object(P.json,'loads',capture):proof=P.route(model,raw,2400)
            proof.pop('events',None)
            terminal=proof['terminal']
            assert len(receipts)==1
            receipt=receipts[0];q['passed']=bool(proof['passed'])
            if proof['passed']:
                assert terminal['lives']==2 and terminal['hp']>0 and 899<=terminal['x']<944 and abs(terminal['y']-112)<=1
                assert N.get(model,'StarInvincibleTimer')==0 and N.get(model,'PlayerStatus')==1
            q.update(opening=opening,proof=proof,native_power=N.get(model,'PlayerStatus'),Star=N.get(model,'StarInvincibleTimer'),
                live_actor_trace=receipt.get('later_route',{}).get('fourth_actor_trace'),
                exact_native_receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                scope='Complete ordinary four-pipe CPU replay; full1-1/native cadence separate')
        assert not attempts
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',action='store_true');parser.add_argument('--current-bt-f11',action='store_true');args=parser.parse_args()
    if args.current_bt_f11:import current_prince_body_research_f11_1114 as Current
    else:import current_prince_body_research_input_1114 as Current
    result=run(Current.load(Game.Factory.ROM),source=args.source)
    print(json.dumps(result,separators=(',',':')),flush=True)
    if not result['passed']:raise SystemExit(1)
