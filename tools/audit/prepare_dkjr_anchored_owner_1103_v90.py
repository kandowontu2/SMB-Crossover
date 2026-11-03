"""Relink the private current-owner proposal to the entrance89 payload."""
import inspect
import json
from pathlib import Path
import prepare_dkjr_current_owner_1103_v79 as P

A,R,O=P.A,P.R,P.O


def main():
    text=inspect.getsource(P.main)
    text=text.replace('native-event-','native-entrance-').replace('-v74','-v89').replace('-v79','-v90')
    text=text.replace("Path(__file__),C.O/", "Path(__file__),V79_PATH,C.O/")
    env=dict(P.__dict__,__file__=__file__,V79_PATH=Path(P.__file__))
    exec(compile(text,__file__,'exec'),env);env['main']()


def image():
    q=json.loads((O/'native-owner-proposal-v90.json').read_text())
    for rel,digest in q['bindings'].items():assert A.sha((R/rel).read_bytes())==digest,rel
    base,_=P.C.image();raw=bytearray(base['raw']);assert A.sha(raw)==q['parent_memory_SHA256']
    for row in q['patches']:
        at=row['file_offset'];old,new=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(old)]==old
        raw[at:at+len(new)]=new
    assert A.sha(raw)==q['expected_memory_only_SHA256']
    return dict(base,raw=bytes(raw)),q


if __name__=='__main__':main()
