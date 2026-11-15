"""Strict16a controller metadata and actual-ROM ordinary source replay."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import compose_prince_body_transition_590_1115 as C
import check_prince_body_transition_candidate_1115 as Candidate
import replay_prince_body_transition_1115 as Replay


def run(parent,*,scope='four-caps',source=False):
    def deny(*args,**kwargs):raise AssertionError('Read-only control proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,info=C.proposal(parent);assert C.inverse(raw)==parent
        metadata={name:Replay.metadata(raw,scope=name)for name in('four-caps','opposed-loss')}
        rejected=[]
        for name,image in(('parent590',parent),('truncated',raw[:-1]),('dirty',raw[:16]+bytes([raw[16]^1])+raw[17:])):
            for replay_scope in metadata:
                try:Replay.controller(image,scope=replay_scope)
                except AssertionError:rejected.append([name,replay_scope])
                else:raise AssertionError('Foreign image accepted by strict16a control')
        q=dict(passed=True,composition=info,metadata=metadata,scope=scope,rejected_images=rejected,
            frozen_navigation_and_default_factories_preserved=True,source_replay_executed=source,outputs=0,Mesen=False)
        print(json.dumps(dict(event='strict16a-readonly-controller-metadata',**metadata),separators=(',',':')),flush=True)
        if source:
            m,opening=Candidate.cold(raw);text=Replay.controller(raw,scope=scope);receipts=[];loads=json.loads
            def capture(*args,**kwargs):
                value=loads(*args,**kwargs)
                if isinstance(value,dict)and'later_route'in value:receipts.append(value)
                return value
            with patch.object(Candidate.Game,'controller',lambda image:text),patch.object(Candidate.Game.json,'loads',capture):
                proof=Candidate.Game.route(m,raw,2400 if scope=='four-caps'else 5100)
            assert len(receipts)==1;receipt=receipts[0];proof.pop('events',None);proof.pop('sword_trace',None)
            q.update(passed=bool(proof['passed']),opening=opening,proof=proof,
                actual_readback=receipt.get('new_candidate_readback'),
                actual_transition=receipt.get('later_route',{}).get('body_transition'),
                first_fourth_cap=receipt.get('later_route',{}).get('fourth_practical_cap'),
                exact_native_receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                actual_CPU_ROM_SHA256=C.digest(m.bundle['raw']),no_source_array_mounts=True,
                source_binding_limit='Actual16a CPU; source peripheral does not establish native physical cadence; first boot consumer transport is a separate proof')
            if proof['passed']:
                assert receipt['new_candidate_readback']['bytes']==4027
                assert proof['terminal']['hp']>0 and proof['terminal']['lives']==2
                if scope=='four-caps':assert proof['reason']=='Four real native pipe caps through ordinary jump and Up'
                else:assert q['actual_transition']['loss']and q['actual_transition']['sheath']and q['actual_transition']['movement']and q['actual_transition']['readmitted']
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',action='store_true');p.add_argument('--scope',choices=('four-caps','opposed-loss'),default='four-caps');args=p.parse_args()
    q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),scope=args.scope,source=args.source)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
