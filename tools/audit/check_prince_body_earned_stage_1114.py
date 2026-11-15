"""Cold ordinary earned-sword full-stage source replay, stdout only."""
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch
import check_prince_body_world_1114 as Game
import replay_prince_body_earned_stage_1114 as Factory
import check_bub_current_budget_1113 as Frames

C,P,N=Game.C,Game.P,Game.N


def run(current,*,source=False):
    attempts=[]
    def deny(*args,**kwargs):
        attempts.append(str(args[:1]));raise AssertionError('Unexpected output/launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,info=C.proposal(current.reference1daca)
        assert C.inverse(raw)==current.reference1daca
        assert C.Build.Old.Packet.extract(current.original)==C.Build.Old.Packet.extract(current.reference1daca)
        text=Factory.controller(raw);metadata=Factory.metadata(raw)
        assert not any(s in text for s in('pad=201','or 201'))
        assert Factory.Full.Fix.CANDIDATE not in text
        q=dict(passed=True,metadata=metadata,composition=info,public_input=current.metadata(),
            current_Prince_packet_exact=True,write_or_launch_attempts=attempts,
            source_replay_executed=source,outputs=0,Mesen=False)
        if source:
            print(json.dumps(dict(event='earned-stage-readonly-metadata-passed',**q),separators=(',',':')),flush=True)
            model,opening=Game.cold(raw);receipts=[];loads=json.loads;ticks=0
            def capture(*args,**kwargs):
                value=loads(*args,**kwargs)
                if isinstance(value,dict)and'later_route'in value:receipts.append(value)
                return value
            def frame(m,*args,**kwargs):
                nonlocal ticks
                result=Frames.frame(m,whole_pass=True);ticks+=1
                if ticks%500==0:
                    print(json.dumps(dict(event='earned-stage-progress',Main_pass=ticks,
                        x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
                        hp=m.ram[2][0x6cf],sword=m.ram[2][0x6ee],engine=N.get(m,'GameEngineSubroutine')),separators=(',',':')),flush=True)
                return result
            with patch.object(P,'controller',lambda image:text),patch.object(P.Frames,'frame',frame),patch.object(P.json,'loads',capture):
                proof=P.route(model,raw,6500)
            assert len(receipts)==1
            receipt=receipts[0];late=receipt.get('later_route',{});ending=late.get('finish',{})
            proof.pop('events',None)
            if isinstance(proof.get('flower'),dict):proof['flower']={k:v for k,v in proof['flower'].items()if k!='trace'}
            if isinstance(proof.get('sword_trace'),list):proof['sword_trace']=proof['sword_trace'][-6:]
            q.update(opening=opening,proof=proof,
                Main_entries=receipt.get('Main_entries'),Main_returns=receipt.get('Main_returns'),
                Main_pending=receipt.get('Main_pending'),grounded_1_2_completed_returns=receipt.get('grounded_1_2_completed_returns'),
                observed_natural_Star=receipt.get('observed_natural_Star'),
                flag=ending.get('flag'),castle=ending.get('castle'),third_gap=ending.get('gap'),
                ending_obstruction=ending.get('obstruction'),ending_climbs=ending.get('climbs'),
                ending_jumps=ending.get('jumps'),
                earned_stage=late.get('earnedStage'),
                native_power=N.get(model,'PlayerStatus'),Star=N.get(model,'StarInvincibleTimer'),
                exact_native_receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                scope='Actual Main/NMI CPU model with whole returned Main passes; native cadence separate')
            q['passed']=bool(proof['passed'])
            if proof['passed']:
                assert receipt['Main_entries']==receipt['Main_returns']and not receipt['Main_pending']
                assert receipt['grounded_1_2_completed_returns']==25
                assert ending.get('flag')and ending.get('castle')and ending.get('gap')
        assert not attempts
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',action='store_true');parser.add_argument('--current-bt-f11',action='store_true');args=parser.parse_args()
    if args.current_bt_f11:import current_prince_body_research_f11_1114 as Current
    else:import current_prince_body_research_input_1114 as Current
    print(json.dumps(run(Current.load(Game.Factory.ROM),source=args.source),separators=(',',':')),flush=True)
