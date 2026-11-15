"""Source-qualify the exact per-class current FF native1UP replay text."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_ff_natural_oneup_current_1114 as Factory
import check_smb1_alts_full11_1114 as Runner
import check_shared_world_sprite_images_1114 as Cold


def run(raw,key):
    arena=[];original=Runner.LuaRuntime
    def cold(image,identity):
        with patch.object(Cold,'Factory',Factory):m=Cold.cold(image,identity)
        arena.append(m);return m
    class Runtime:
        def __init__(self,*a,**kw):self.inner=original(*a,**kw)
        def __getattr__(self,n):return getattr(self.inner,n)
        def execute(self,text):
            api=self.inner.globals().emu;read=api.read;api.memType.nesPpuDebug=3
            api.read=lambda at,kind=0:arena[0].vram[at&0x3fff]if kind==3 else read(at,kind)
            return self.inner.execute(text)
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold),patch.object(Runner,'LuaRuntime',Runtime):
        return Runner.run(raw,key,7000)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,default='fighter-life');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('FF native1UP source test attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):q=run(raw,a.identity)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Current FF production1UP replay remains source-unqualified'
