"""Strict prefix-only parent/candidate controller packaging, no outputs."""
from pathlib import Path
from unittest.mock import patch
import json
import compose_hot_draw_bt_67e_1115 as C
import replay_hot_draw_bt_67e_1115 as F


def run(parent,image):
    reader=Path.read_bytes;rejected=[]
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Packaging reread mutable Nightly'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Packaging attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        rows=[];bodies=[]
        for raw in(parent,image):
            text=F.cadence_reads(raw);q=F.observer_config(raw);body=text.split('\n',1)[1];bodies.append(body)
            assert C.H(body.encode())==F.BODY_SHA and q['ram']['NmiSkipped']==314
            assert q['sha']==C.H(raw)and q['hot_draw_118']['bytes']==list(raw[C.FILE:C.FILE+118])
            assert q['hot_draw_118']['bank_SHA256']==C.H(raw[16+66*8192:16+67*8192])
            rows.append(dict(ROM_SHA256=C.H(raw),cadence_Lua_SHA256=C.H(text.encode()),
                body_SHA256=C.H(body.encode()),NmiSkipped_RAM=q['ram']['NmiSkipped'],
                Hot118_SHA256=q['hot_draw_118']['span_SHA256'],Hot118_bank_SHA256=q['hot_draw_118']['bank_SHA256'],
                whole_ROM_and_physical118_metadata_bound=True,
                runtime_Hot_callback_added=False,actual_existing_hook_bytes_bank_hashes_verified=True,
                stage_controllers={key:C.H(F.controller(raw,key).encode())for key in F.IDENTITIES}))
        assert bodies[0]==bodies[1]
        for label,raw in(('7fb',C.reference(parent)),('dirty',image[:-1]),('unknown',bytes(len(image)))):
            try:F.cadence_reads(raw)
            except AssertionError:rejected.append(label)
            else:raise AssertionError(('Unknown cadence input accepted',label))
    return dict(rows=rows,body_byte_identical=True,prefix_only_changes=True,
        strict_rejections=rejected,mutable_Nightly_reads_after_load=0,
        C_SHA256=C.H(Path(C.__file__).read_bytes()),F_SHA256=C.H(Path(F.__file__).read_bytes()),
        source_only=True,outputs=0,Mesen_run=False)


if __name__=='__main__':
    raw=C.load_current_image();parent=F.parent(raw);image,_=C.proposal(parent);q=run(parent,image)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
