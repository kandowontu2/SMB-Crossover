"""Strict portable composition/inverse, immutable preservation and replay pins."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from unittest.mock import patch
import compose_prince_body_world_1114 as C
import replay_prince_body_edge8_1114 as Edge
import replay_prince_pipe_direct_1114 as Frozen


def run(current):
    assert C.digest(current)in C.PARENTS.values()
    common=C.DK.inverse(current)if C.digest(current)==C.DK.CANDIDATE else current
    parents=(common,C.DK.proposal(common)[0]);outputs=[];attempts=[];rejected=0
    def forbidden(*a,**kw):attempts.append('write or subprocess');raise AssertionError('Source-only proof forbids file writes/launch')
    def reject(fn):
        nonlocal rejected
        try:fn()
        except AssertionError:rejected+=1
        else:raise AssertionError('Unknown image unexpectedly accepted')
    with patch.object(Path,'write_bytes',forbidden),patch.object(Path,'write_text',forbidden),patch.object(subprocess,'Popen',forbidden),patch.object(subprocess,'run',forbidden):
        for parent in parents:
            raw,info=C.proposal(parent);assert C.inverse(raw)==parent
            # Inverse is executable without reading the mutable installed ROM.
            original_reader=Path.read_bytes
            def read(path,*a,**kw):
                assert path.resolve()!=C.Build.Old.F.ROM.resolve(),'Inverse attempted mutable Downloads read'
                return original_reader(path,*a,**kw)
            C.inverse.cache_clear()
            with patch.object(Path,'read_bytes',read):assert C.inverse(raw)==parent
            outputs.append(info)
            reject(lambda:C.proposal(raw))
            altered=bytearray(raw);altered[100]^=1
            reject(lambda:C.inverse(bytes(altered)))
            reject(lambda:C.inverse(raw[:-1]))
            reject(lambda:Frozen.controller(raw,pad=9))
            if C.digest(raw)==Edge.PIN:edge=Edge.metadata(raw)
        reject(lambda:C.proposal(C.normalize_parent(common,kind='common82').reference421))
        altered=bytearray(common);altered[100]^=1
        reject(lambda:C.proposal(bytes(altered)))
    assert not attempts
    q=dict(passed=True,compositions=outputs,portable_exact_parent_inverse_cases=2,
        unknown_image_and_frozen_API_rejections=rejected,mutable_Downloads_reads_during_inverse=0,
        write_or_subprocess_attempts=0,frozen_edge8=edge,
        frozen_granted_sources_exact=True,outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':print(json.dumps(run(C.Build.Old.F.ROM.read_bytes()),separators=(',',':')),flush=True)
