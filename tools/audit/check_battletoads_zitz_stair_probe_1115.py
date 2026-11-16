"""Compile/authenticate passive Zitz probe and check actual source callbacks."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse,json
import replay_battletoads_zitz_stair_probe_1115 as F
import check_battletoads_carry_current_1115 as Retained

C=F.C


def run(raw,source=False):
    metadata=F.metadata(raw);original=F.Base.controller(raw,'zitz');text=F.controller(raw)
    assert C.H(original.encode())==F.FROZEN_LUA
    assert original.count('emu.setInput(')==text.count('emu.setInput(')
    assert original.count('btInput=choose(context())')==text.count('btInput=choose(context())')==1
    assert original.count("if frame>=16000 or updates>=10000 then finish('bounded-route-timeout')end")==text.count("if frame>=16000 or updates>=10000 then finish('bounded-route-timeout')end")==1
    assert original.count("and nextUpdates==25 and identity()and r('NumberofLives')==2")==text.count("and nextUpdates==25 and identity()and r('NumberofLives')==2")==1
    rejects=[]
    for label,bad in(('parent67',C.inverse(raw)),('truncated',raw[:-1]),('unknown',bytes(len(raw)))):
        try:F.controller(bad)
        except AssertionError:rejects.append(label)
        else:raise AssertionError(('Passive probe accepted wrong image',label))
    result=dict(metadata=metadata,file_SHA256=C.H(Path(F.__file__).read_bytes()),strict_rejections=rejects,
        original_choose_called_once_at_original_completed_Main_point=True,
        original_setInput_and_success_timeout_conditions_unchanged=True,
        extra_callbacks_only_read_game_memory=True,outputs=0,Mesen_run=False)
    if source:
        Factory=SimpleNamespace(ROM=F.ROM,W=F.W,N=F.N,IDENTITIES=('zitz',),normalize=F.Base.normalize,
            bindings=lambda image,key:F.bindings(image),controller=lambda image,key:F.controller(image),
            metadata=lambda image,key:F.metadata(image))
        Runner=Retained.Old.R.Frozen.Cold.Runner
        with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',F.Model.cold):q=Runner.run(raw,'zitz',6500)
        receipt=q['receipt'];assert q['passed']and receipt['passed']
        assert(receipt['Main_returned'],receipt['flag']['Main'],receipt['castle']['Main'],receipt['entrance']['Main'])==(4003,2805,2868,3406)
        assert(receipt['terminal']['source_HP'],receipt['terminal']['lives'],receipt['terminal']['x'],receipt['terminal']['y'],receipt['next_area_updates'])==(43,2,40,176,25)
        probe=receipt['stair_probe']
        assert probe['worker_entries']==probe['worker_returns']==receipt['Bt_source_steps']
        assert len(probe['first'])<=3 and len(probe['tail'])<=4 and probe['group_count']<=32
        assert len(probe['first'])+len(probe['tail'])+int(bool(probe.get('first_stair_A_saved_mismatch')))<=8
        result.update(actual_source_callback_entry_return_pairs=probe['worker_returns'],
            original_source_full_route_milestones_and_terminal_identical=True,
            callback_return_PC=F.bindings(raw)['stair_probe']['worker_return']['pc'],
            source_probe=probe,source_only=True,hardware_jump_or_race_cause_not_inferred=True)
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',action='store_true');args=ap.parse_args()
    parent=C.load_current_image();raw=C.proposal(parent)[0]
    def deny(*a,**kw):raise AssertionError('Passive source observer attempted output/native')
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Observer reread mutable Nightly'
        return reader(path)
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(raw,args.source)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
