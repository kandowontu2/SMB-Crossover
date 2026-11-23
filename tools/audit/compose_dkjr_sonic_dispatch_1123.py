"""Exact287 combined DK/Sonic authorization proposal; bytes remain in memory.

This replaces the already installed Sonic helper rather than composing the
historical DK-only patch over it. No ROM, shared-slot, or delivery write API.
"""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_dispatch_epoch_1123 as D
import compose_sonic_current_auth_epoch_1122 as S
import repair_rogue_side_pipe_1123 as Rogue

M, Fit, H = S.M, S.Fit, S.H
PIN = '28708fa9a4e7dd88f1aaa72653b7d5a6ba0fb3c6d5abf544a526b09d333a884c'
CANDIDATE = '14b0b4c23baa1ff454d25720b0585dd45f7fa4179bbba6b7f38d68b6e0c141b5'
PARENT_DK_COOKIE = bytes.fromhex('a72801bbdb7d84eb2485d69d23df750c')
PARENT_SONIC_COOKIE = bytes.fromhex('a72b0158e8caa097edbf84fef762ea81')
SOURCE = M.R/'tools/reference/dkjr_sonic_dispatch_1123.s'
LAYOUT = dict(GATE=(0xa8dc,36), UTIL=(0xb06b,36), HEADER=(0xb8f0,16))
SONIC_LAYOUT = dict(SONIC_EPOCH=(0xda40,128))
FROZEN_SONIC = 'cfc53456c07f79b186e952204039105d079dd7b2a8eed69edcc316490ccdf158'


def selector_source(combined=True):
    admission = (' cmp #3\n beq MiniTry\n and #$fd\n cmp #4\n beq MiniTry'
                 if combined else ' and #$fd\n cmp #4\n beq MiniTry')
    return Fit.once(D.guarded_selector(), ' adc #1\n lsr\n cmp #2\n beq MiniTry', admission)


@lru_cache(maxsize=1)
def program():
    assert H(S.SOURCE.read_bytes()) == FROZEN_SONIC
    old = S.program()
    # Relink the retained Sonic scope to the combined helper. Its guards and
    # successful HostMain stamp are copied from this exact frozen source.
    frozen = S.SOURCE.read_text(encoding='ascii').split('.segment "SONIC_EPOCH"',1)[1]
    base = M.assemble('ReadSonicEpoch=$da40\n'+SOURCE.read_text(encoding='ascii'), LAYOUT)
    bundle = S.B.W.Symbols.bundle()
    names = ('GameEngineSubroutine','GamePauseStatus','TimerControl')
    defs = ''.join(f'{name}=${S.B.W.address(bundle,name):04x}\n' for name in names)
    defs += 'FrameCounter=$0e\nSharedEpoch=$c3f0\n'
    defs += ''.join(f'{name}=${base["symbols"][name]:04x}\n' for name in ('CheckCodeHeader','RestoreC'))
    sonic = M.assemble(defs+'.segment "SONIC_EPOCH"'+frozen, SONIC_LAYOUT)
    assert sonic['used']['SONIC_EPOCH'] == old['used']['SONIC_EPOCH'] == 72
    assert sonic['symbols']['StampSonicEpoch'] == old['symbols']['StampSonicEpoch'] == 0xda81
    a,b=old['images']['SONIC_EPOCH'],sonic['images']['SONIC_EPOCH']
    expected=a
    for name in ('CheckCodeHeader','RestoreC'):
        before=b'\x4c'+old['symbols'][name].to_bytes(2,'little')
        after=b'\x4c'+base['symbols'][name].to_bytes(2,'little')
        assert expected.count(before)==1
        expected=expected.replace(before,after,1)
    assert b==expected
    selector = M.assemble(selector_source(),dict(SELECTOR=(0xa740,127)))
    assert selector['used']['SELECTOR'] == 127
    assert base['used'] == dict(GATE=34,UTIL=35,HEADER=14)
    main = M.assemble(D.NEW_MAIN,dict(MAIN=(D.MAIN,D.MAIN_SIZE)))
    assert main['used']['MAIN'] <= D.MAIN_SIZE
    return base,sonic,selector,main


@lru_cache(maxsize=1)
def static_changes():
    base,sonic,selector,main = program()
    old = S.program()
    prior_selector = M.assemble(selector_source(False),dict(SELECTOR=(0xa740,127)))
    changes = [
        (S.off(65,0xa740),prior_selector['images']['SELECTOR'].ljust(127,b'\xea'),
         selector['images']['SELECTOR'],'bounded combined admission; public row0 complete'),
        (S.off(65,0xa7d5),S.checked_branches(prior_selector),S.checked_branches(selector),
         'existing checked-result branch slot'),
    ]
    for name,(pc,size) in LAYOUT.items():
        old_size=S.LAYOUT[name][1]
        before=old['images'][name].ljust(old_size,b'\xff')
        if name=='UTIL':before+=bytes.fromhex('4cdca8')
        changes.append((S.off(85,pc),before,base['images'][name].ljust(size,b'\xff'),
                        'native85 '+name+('; retires private row0 mirror' if name=='UTIL' else '')))
    pc,size=SONIC_LAYOUT['SONIC_EPOCH'];at=M.CHR+334*1024+pc-0xd800
    changes.append((at,old['images']['SONIC_EPOCH'].ljust(size,b'\xff'),
                    sonic['images']['SONIC_EPOCH'].ljust(size,b'\xff'),'retained Sonic scope, two relinked continuations'))
    changes.append((D.MAIN_FILE,D.OLD_MAIN,main['images']['MAIN'].ljust(D.MAIN_SIZE,b'\xea'),
                    'DK successful score/motor epoch C8FF'))
    return tuple(changes)


def proposal(parent):
    assert isinstance(parent,bytes) and len(parent)==2097168 and H(parent)==PIN
    assert H(Rogue.restore_pipe_bytes(parent)) == S.CANDIDATE
    base,sonic,selector,_ = program()
    out=bytearray(parent);spans=[]

    def put(at,before,after,role):
        assert len(before)==len(after) and parent[at:at+len(before)]==before, (role,hex(at))
        assert not any(at<s['file']+s['bytes'] and s['file']<at+len(after) for s in spans)
        out[at:at+len(after)]=after
        spans.append(dict(file=at,bytes=len(after),role=role,old_SHA256=H(before),new_SHA256=H(after)))

    mirror=S.off(85,0xb08c)
    assert parent[mirror:mirror+114] == bytes.fromhex('4cdca8')*38
    for change in static_changes():
        put(*change)
    dk_cookie=b'\xa7\x28\x01'+sha256(D.packet(parent)).digest()[:13]
    assert parent[D.COOKIE:D.COOKIE+16]==dk_cookie==PARENT_DK_COOKIE
    put(D.COOKIE,dk_cookie,dk_cookie[:3]+sha256(D.packet(out)).digest()[:13],'complete DK packet cookie')
    sonic_cookie=b'\xa7\x2b\x01'+sha256(b''.join(M.page(parent,n) for n in M.COOKIE_PAGES)).digest()[:13]
    assert parent[M.COOKIE_AT:M.COOKIE_AT+16]==sonic_cookie==PARENT_SONIC_COOKIE
    put(M.COOKIE_AT,sonic_cookie,sonic_cookie[:3]+sha256(b''.join(M.page(out,n) for n in M.COOKIE_PAGES)).digest()[:13],
        'complete retained Sonic packet cookie')
    candidate=bytes(out)
    assert H(candidate)==CANDIDATE
    changed={i for i,(a,b) in enumerate(zip(parent,candidate,strict=True)) if a!=b}
    owned={i for s in spans for i in range(s['file'],s['file']+s['bytes'])}
    assert changed<=owned and len(parent)==len(candidate)
    assert candidate[mirror+3:mirror+114]==parent[mirror+3:mirror+114]
    # Entire Rogue native bank, checker, predicate, transport and source-side
    # loop are outside this proposal; compare bytes rather than broad hashes.
    for bank,lo,hi in ((95,0xa000,0xc000),(65,0xaee2,0xaf85),(65,0xab12,0xab50),
                       (126,0x9c6e,0x9cb6),(82,0xb16d,0xb189),(126,0x80c2,0x80c9)):
        start=S.off(bank,lo)
        assert candidate[start:start+hi-lo]==parent[start:start+hi-lo]
    assert parent[S.off(126,0x80c2):S.off(126,0x80c2)+7] == bytes.fromhex('8da17d8d165160')
    return candidate,dict(parent_SHA256=PIN,candidate_SHA256=H(candidate),
        source_SHA256=H(SOURCE.read_bytes()),used=base['used'],selector_used=selector['used'],
        helper_symbols=base['symbols'],selector_symbols=selector['symbols'],
        sonic_symbols=sonic['symbols'],spans=spans,changed_bytes=len(changed),
        epochs=dict(DK=0xc8ff,Mini=0xc3f0,Sonic=0xc3f0),
        public_row0_full=True,retired_private_mirror=[0xb08c,0xb08f],
        retained_private_rows=[1,37],all_unowned_exact=True,
        Rogue_bank95_exact=True,Prince_predicate_exact=True,
        outputs=0,native_qualified=False)


def inverse(candidate):
    assert isinstance(candidate,bytes) and H(candidate)==CANDIDATE
    restored=bytearray(candidate)
    for at,before,after,role in static_changes():
        assert candidate[at:at+len(after)]==after, role
        restored[at:at+len(before)]=before
    restored[D.COOKIE:D.COOKIE+16]=PARENT_DK_COOKIE
    restored[M.COOKIE_AT:M.COOKIE_AT+16]=PARENT_SONIC_COOKIE
    parent=bytes(restored)
    assert H(parent)==PIN and proposal(parent)[0]==candidate
    return parent


if __name__=='__main__':
    _,q=proposal(M.ROM.read_bytes())
    print('COMBINED DISPATCH PROPOSAL '+json.dumps(q,separators=(',',':')),flush=True)
