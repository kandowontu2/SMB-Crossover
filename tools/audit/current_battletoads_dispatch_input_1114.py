"""Explicit read-only F11/score571 boundary for unallocated dispatch research."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import compose_battletoads_camera_handoff_1114 as BT
import compose_native_floatey_score_1114 as Score

ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def normalize(raw,*,kind):
    assert isinstance(raw,bytes)
    if kind=='f11':assert sha256(raw).hexdigest()==BT.CANDIDATE;image=raw
    elif kind=='score-571':
        assert sha256(raw).hexdigest()==Score.CANDIDATE
        image=Score.inverse(raw);assert Score.proposal(image)[0]==raw
    else:raise AssertionError('Explicit f11 or score-571 input kind required')
    assert sha256(image).hexdigest()==BT.CANDIDATE and BT.proposal(BT.inverse(image))[0]==image
    return image


def load(path=None):
    raw=(ROM if path is None else Path(path)).read_bytes();pin=sha256(raw).hexdigest()
    kind={BT.CANDIDATE:'f11',Score.CANDIDATE:'score-571'}.get(pin)
    assert kind is not None,'Unknown/dirty dispatch research input'
    return normalize(raw,kind=kind),dict(actual_input_SHA256=pin,explicit_input_kind=kind,
        normalized_research_SHA256=BT.CANDIDATE,normalization_for_source_research_only=True,
        future_current_composition_must_preserve_all10_score_bytes=True)


def checks(raw):
    base=normalize(raw,kind='f11'if sha256(raw).hexdigest()==BT.CANDIDATE else'score-571')
    score=Score.proposal(base)[0];rejects=[]
    for name,image,kind in(('F11_as_score',base,'score-571'),('score_as_F11',score,'f11'),
            ('unknown_kind',base,'automatic'),('truncated',base[:-1],'f11')):
        try:normalize(image,kind=kind)
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Wrong typed input accepted',name))
    for name,image,kind,at in(('dirty_F11',base,'f11',90000),('dirty_score',score,'score-571',90000),('dirty_protected_score',score,'score-571',Score.AT)):
        changed=bytearray(image);changed[at]^=1
        try:normalize(bytes(changed),kind=kind)
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Dirty typed input accepted',name))
    original=Path.read_bytes
    def no_live(path):
        assert path.resolve()!=ROM.resolve(),'Mutable Nightly re-read during strict inverse'
        return original(path)
    with patch.object(Path,'read_bytes',no_live):
        assert normalize(base,kind='f11')==normalize(score,kind='score-571')==base
    return dict(f11_SHA256=BT.CANDIDATE,score571_SHA256=Score.CANDIDATE,
        source_only_normalization=True,strict_inverse_roundtrip=True,rejects=rejects,mutable_Nightly_reads=0,
        ROM_changes=False,outputs=0)


if __name__=='__main__':
    raw,info=load();q=checks(raw);q.update(info);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
