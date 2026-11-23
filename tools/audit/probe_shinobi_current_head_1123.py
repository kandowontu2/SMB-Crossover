"""Current93f binding of the immutable bcc Shinobi head/pickup diagnostic.

Expected negative witness, never a pickup pass. Root alone may --run.
"""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import probe_shinobi_first_mushroom_1123 as Prior
import repair_goku_hidden_head_1123 as Goku

PIN=Goku.CANDIDATE
SOURCE='48f26eebf9d564a2dc4f4f8b381a7cd4bf2b6cb5bdc588f0ac32575347aca4f4'
LUA='1cc87d61652db521aed69b3b9824ef937e5304a1f07c30efe2bd367c07066ca4'
H,ROM=Prior.H,Prior.ROM


def controller(raw):
    assert H(raw)==PIN and H(Path(Prior.__file__).read_bytes())==SOURCE
    parent=Goku.recover_parent(raw)
    assert H(parent)==Prior.PIN==Goku.BASE
    # Goku's two native query spans are disjoint from every Sh carrier,
    # the complete resident owner, its cookie and all diagnostic hooks.
    for page in set((503,504,505,516,517)+Prior.CODE_PAGES):
        at=1048592+page*1024
        assert raw[at:at+1024]==parent[at:at+1024]
    at=16+65*8192;assert raw[at:at+8192]==parent[at:at+8192]
    text=Prior.controller(parent).decode()
    assert text.count(Prior.PIN)==1
    program=text.replace(Prior.PIN,PIN).encode()
    assert LUA is None or H(program)==LUA
    return program


def execute(raw,source,limit):
    program=controller(raw)
    def pinned(image):
        assert image==raw
        return program
    with patch.object(Prior,'PIN',PIN),patch.object(Prior,'controller',pinned),patch.object(Prior,'LUA',LUA):
        q=Prior.source(raw,limit)if source else Prior.native(raw)
    q['current_binding']=dict(parent_SHA256=Goku.BASE,ROM_SHA256=PIN,
        original_source_SHA256=SOURCE,controller_SHA256=H(program),
        inverse='repair_goku_hidden_head_1123.recover_parent',
        Shinobi_all_12_carriers_and_resident_exact=True,
        pickup_success_claimed=False)
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group()
    g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=600);a=p.parse_args()
    assert 200<=a.limit<=900
    raw=ROM.read_bytes()
    if a.run:q=execute(raw,False,a.limit)
    else:
        def deny(*args,**kwargs):raise AssertionError('Source-only Shinobi check attempted output/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            q=execute(raw,True,a.limit)if a.source else dict(passed=True,controller_SHA256=H(controller(raw)),outputs=0)
    print('SHINOBI_CURRENT '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
