"""Measured-stall controller units and actual current67/bc5 source routes."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse,json
import replay_battletoads_stair_progress_1115 as F
import hot_draw_bt_67e_model_1115 as Model
import check_battletoads_carry_current_1115 as Retained

C=F.C


def units(parent,image):
    rt=F.Base.Original.LuaRuntime(unpack_returned_tuples=True)
    def trial(points,**changes):
        detector=rt.execute(F.MONITOR+'\nreturn btStairNoProgress')
        out=[]
        for x,y,ground in points:
            c=dict(char=33,world=0,level=0,areaType=1,engine=8,x=x,y=y,grounded=ground);c.update(changes)
            out.append(bool(detector(rt.table_from(c))))
        return out
    native=[(2177+i%2,128,True)for i in range(24)]
    out=trial(native);assert out[:16]==[False]*16 and out[16:]==[True]*8
    assert not any(trial([(2160+2*i,128,True)for i in range(24)]))
    assert not any(trial([(2177,112+2*i,True)for i in range(24)]))
    for changes in(dict(char=0),dict(world=1),dict(level=1),dict(areaType=0),dict(engine=11)):
        assert not any(trial(native,**changes))
    assert not any(trial([(2177,128,True)]*15+[(2177,128,False)]+[(2177,128,True)]*16))
    assert not any(trial([(2177,128,True)]*15+[(2180,128,True)]+[(2180,128,True)]*15))
    rows=[];rejects=[]
    for raw in(parent,image):
        rows.append(F.metadata(raw))
        for key in F.IDENTITIES:
            old=F.Base.controller(raw,key);new=F.controller(raw,key)
            assert old.count('emu.setInput(')==new.count('emu.setInput(')
            assert old.count('btInput=choose(context())')==new.count('btInput=choose(context())')==1
            assert old.count("if frame>=16000 or updates>=10000 then finish('bounded-route-timeout')end")==new.count("if frame>=16000 or updates>=10000 then finish('bounded-route-timeout')end")==1
    for key in F.IDENTITIES:assert F.controller(parent,key).split('\n',1)[1]==F.controller(image,key).split('\n',1)[1]
    for label,bad in(('truncated',image[:-1]),('unknown',bytes(len(image))),('old7fb',C.reference(parent))):
        try:F.controller(bad,'zitz')
        except AssertionError:rejects.append(label)
        else:raise AssertionError(('Unknown policy input accepted',label))
    assert F.Base.cadence_reads(parent).split('\n',1)[1]==F.Base.cadence_reads(image).split('\n',1)[1]
    assert C.H(F.Base.cadence_reads(image).split('\n',1)[1].encode())=='f76943af78cedc9d38c6433ed438a2040ccc186c18c2dd6fb686a4fbde179f7e'
    return dict(explicit_controller_unit_fixture_not_gameplay=True,native2177_2178_oscillation_triggers_sample17=True,
        forward_vertical_progress_air_and_outside_domain_reset=True,rows=rows,strict_rejections=rejects,
        parent_candidate_each_identity_policy_body_byte_identical=True,original_setInput_choose_timeout_and_clear_unchanged=True,
        frozen80_cadence_body_unchanged=True,F_SHA256=C.H(Path(F.__file__).read_bytes()))


def stage(raw,key):
    Runner=Retained.Old.R.Frozen.Cold.Runner
    with patch.object(Runner,'Factory',F),patch.object(Runner,'cold',Model.cold):q=Runner.run(raw,key,6500)
    assert q['passed']and q['receipt']['passed'],q
    return dict(actual_ROM_SHA256=C.H(raw),identity=key,route=q,ordinary_controls_only=True,gameplay_seeds=0,
        actual_candidate_or_parent_code_retained=True,physical_timing_or_native_claim=False)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('units','parent-rash','parent-zitz','candidate-rash','candidate-zitz'));a=ap.parse_args()
    loaded=C.load_current_image();parent=F.Base.parent(loaded);image,_=C.proposal(parent)
    def deny(*args,**kw):raise AssertionError('Controller source gate attempted output/native')
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Controller reread mutable Nightly'
        return reader(path)
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q=units(parent,image)if a.mode=='units'else stage(parent if a.mode.startswith('parent')else image,a.mode.split('-')[1])
    q.update(mode=a.mode,source_only=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
