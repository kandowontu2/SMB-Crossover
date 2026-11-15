"""Strict current16a merge/inverse and real native-side component falsifiers."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import compose_gimmick_empty_side_1115 as C
import check_gimmick_empty_side_components_1115 as U


def run(actual):
    raw,info=C.current_proposal(actual);assert C.current_inverse(raw)==actual
    assert C.current_proposal(C.current_inverse(raw))[0]==raw
    def forbid_read(path):
        assert path.resolve()!=C.ROM.resolve(),'Current inverse must not reread mutable nightly'
        return original_read(path)
    original_read=Path.read_bytes
    with patch.object(Path,'read_bytes',forbid_read):assert C.current_inverse(raw)==actual
    rejects=[]
    for name,image,method in(('parent_as_inverse',actual,C.current_inverse),('candidate_as_forward',raw,C.current_proposal),('truncated',raw[:-1],C.current_inverse)):
        try:method(image)
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Dirty current boundary accepted',name))
    for name,at in(('own_query',202888),('own_renderer',203015),('unowned_Mini',203743),('Prince_current',700000),('CHR',1500000)):
        dirty=bytearray(raw);dirty[at]^=1
        try:C.current_inverse(bytes(dirty))
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Dirty inverse accepted',name))
    rows=[]
    for tile in(0,35,81,97,96):
        pair=[]
        for image,new in((actual,False),(raw,True)):
            m=U.seed(U.bundle(image,new));base=U.W.address(m.bundle,'Block_Buffer_1')
            for i in range(416):m[base+i]=0
            m[base+125]=tile
            U.N.put(m,Local_eb=0,Player_CollisionBits=255,SideCollisionTimer=0,GuestHurtTicks=0,PlayerFacingDir=2)
            z=U.N.invoke(m,'DoPlayerSideCheck',a=93,x=77,y=0,p=0x31)
            pair.append(dict(x=U.N.get(m,'Player_X_Position')+256*U.N.get(m,'Player_PageLoc'),vx=U.N.get(m,'Player_X_Speed'),
                side_timer=U.N.get(m,'SideCollisionTimer'),raw_tile=m[base+125],CPU=z['CPU'],AXYP=U.regs(z)))
        if tile==35:
            assert (pair[0]['x'],pair[0]['vx'],pair[0]['side_timer'])==(1247,0,16)
            assert (pair[1]['x'],pair[1]['vx'],pair[1]['side_timer'],pair[1]['raw_tile'])==(1231,254,0,35)
        else:assert {k:v for k,v in pair[0].items()if k!='CPU'}=={k:v for k,v in pair[1].items()if k!='CPU'}
        rows.append(dict(tile=tile,parent16a=pair[0],candidate=pair[1]))
    return dict(passed=True,parent16a_SHA256=sha256(actual).hexdigest(),runtime_SHA256=sha256(raw).hexdigest(),proposal=info,
        strict_rejections=rejects,portable_inverse_no_mutable_nightly_dependency=True,native_side_component_rows=rows,
        scope='Declared native-side CPU fixtures on exact current combined image, not a native run or ordinary seeded route',outputs=0,Mesen_run=False)


if __name__=='__main__':
    actual=C.ROM.read_bytes()
    def forbid(*args,**kwargs):raise AssertionError('Current qualification attempted files/launch')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch('subprocess.Popen',forbid):q=run(actual)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
