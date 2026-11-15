"""Read-only source/space measurement for Gimmick-only empty-bounce side query."""
from hashlib import sha256
import json
import replay_gimmick_flower_side_probe_current_1115 as Current

R,W,N,PIN=Current.R,Current.W,Current.N,Current.PIN


def measure(raw):
    assert sha256(raw).hexdigest()==PIN
    b=dict(W.Symbols.bundle(),raw=raw)
    segments=[]
    for seg in b['segs'].values():
        if seg.get('name','').strip('"')in('GIMMICK_CORE','GIMMICK_MOVE','GIMMICK_COLD'):
            segments.append(seg)
    names=('GmCoreStart','GmCoreEnd','GmHead','GmFoot','GmSide','GmBodyProbe','GmScreenPoint','GmEmitRecord','GmStarRecord','GmDraw','Block_Buffer_1','Block_Buffer_2','BlockBufferAddr','MTileAttribute','GmTemp2')
    symbols={name:dict(pc=W.address(b,name),file=W.location(b,name)if'ooffs'in b['segs'].get(b['syms'][name].get('seg'),{})else None,metadata=b['syms'][name])for name in names}
    labels=[]
    for name,sym in b['syms'].items():
        if'seg'in sym and b['segs'][sym['seg']].get('name','').strip('"')=='GIMMICK_CORE':
            labels.append((W.address(b,name),name))
    return dict(ROM_SHA256=PIN,segments=segments,symbols=symbols,last_core_labels=sorted(labels)[-20:],
        outputs=0,Mesen_run=False,ROM_composition=False,scope='Measurement only; no spare grant or candidate implied')


if __name__=='__main__':
    print('RESULT '+json.dumps(measure(Current.ROM.read_bytes()),separators=(',',':')),flush=True)
