"""Read-only strict7a80 metadata/cold gate or actual current full route."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse,inspect,json
import check_prince_full_fresh_step_1115 as Previous
import current_prince_gimmick_side_1115 as Current
import replay_prince_full_fresh_current_1115 as Factory

Base=Previous.Base


def cold(raw):
    Current.normalize(raw,kind='prince-current-gimmick-7a80')
    def owning(image):
        assert image==raw,'Wrong current7a80 CPU owning image'
        return raw
    with patch.object(Base.Candidate.Game,'proof_parent',owning):return Base.Candidate.Game.cold(raw)


def run(raw,*,full=False):
    current=Current.normalize(raw,kind='prince-current-gimmick-7a80')
    metadata=Factory.metadata(raw)
    print(json.dumps(dict(event='strict7a80-Prince-metadata',**metadata),separators=(',',':')),flush=True)
    if full:
        source=inspect.getsource(Base.run)
        old='raw,_=C.proposal(parent);text=Replay.controller(raw);metadata=Replay.metadata(raw)'
        new="raw=Current.normalize(parent,kind='prince-current-gimmick-7a80').original;text=Replay.controller(raw);metadata=Replay.metadata(raw)"
        assert source.count(old)==1;source=source.replace(old,new,1)
        old="actual_transition=receipt.get('later_route',{}).get('body_transition'),first_helper_presence=helpers,"
        new=old+"\n        late_pipe={k:receipt.get('later_route',{}).get(k)for k in('fresh_step_outcomes','careful_step_admissions','late_pipe_geometry','late_pipe_control')},"
        assert source.count(old)==1;source=source.replace(old,new,1)
        candidate=SimpleNamespace(**dict(Base.Candidate.__dict__,cold=cold))
        space=dict(Base.__dict__,Current=Current,Replay=Factory,Candidate=candidate)
        exec(compile(source,str(Path(__file__))+':actual7a80-fresh-step','exec'),space)
        q=space['run'](raw)
    else:
        m,opening=cold(raw)
        cookie=raw[Base.C.Packet.COOKIE:Base.C.Packet.COOKIE+16]
        assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
        assert m.bundle['raw']==raw
        q=dict(passed=True,metadata=metadata,opening=opening,actual_CPU_ROM_SHA256=sha256(m.bundle['raw']).hexdigest(),
            both_actual_cold_cookies=True,actual_cold_packet_unchanged16a=True,full_route_executed=False)
    q.update(input=current.metadata(),source_array_mounts=0,outputs=0,Mesen=False,
        scope='Actual current7a80 compiled cold/ordinary source model; native cadence and physical play separate')
    q['current_fresh_step_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');args=ap.parse_args()
    def deny(*args,**kwargs):raise AssertionError('Current Prince source gate attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),full=args.full)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
