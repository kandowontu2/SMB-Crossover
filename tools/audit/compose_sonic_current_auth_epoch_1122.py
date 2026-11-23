"""Exact59 Sonic authorization reuse; dedicated source, memory bytes only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_sonic_original_motion_1122 as M
import measure_dkjr_shared_epoch_fit_1114 as Fit
import profile_sonic_empty_cpu_1110 as B

PIN='59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
SOURCE=M.R/'tools/reference/sonic_current_auth_epoch_1122.s'
LAYOUT=dict(GATE=(0xa8dc,36),UTIL=(0xb06b,33),HEADER=(0xb8f0,16),SONIC_EPOCH=(0xda40,128))
H=M.H

def off(bank,pc):return 16+bank*8192+(pc&8191)

@lru_cache(maxsize=1)
def program():
    bundle=B.W.Symbols.bundle()
    defs=''.join(f'{n}=${B.W.address(bundle,n):04x}\n' for n in ('GameEngineSubroutine','GamePauseStatus','TimerControl'))
    p=M.assemble(defs+SOURCE.read_text(encoding='ascii'),LAYOUT)
    assert p['used']['SONIC_EPOCH']<=128
    return p

def proposal(parent):
    assert isinstance(parent,bytes) and len(parent)==2097168 and H(parent)==PIN
    p=program();out=bytearray(parent);spans=[]
    def put(at,before,after,role):
        assert len(before)==len(after) and parent[at:at+len(before)]==before,(role,hex(at),parent[at:at+len(before)].hex(),before.hex())
        assert not any(at < x['file']+x['bytes'] and x['file'] < at+len(after) for x in spans)
        out[at:at+len(after)]=after
        spans.append(dict(file=at,bytes=len(after),role=role,old_SHA256=H(before),new_SHA256=H(after)))
    old_selector=Fit.OLD_SELECTOR
    # Root's bounded common admission: keep original target until helper
    # returns, hold its validated normalized offset on the real stack, and
    # consume that byte on both auth exits before the mapped Co frame.
    import compose_dkjr_dispatch_epoch_1123 as Shared
    new_selector=Fit.once(Shared.guarded_selector(),' adc #1\n lsr\n cmp #2\n beq MiniTry',' and #$fd\n cmp #4\n beq MiniTry')
    olds=M.assemble(old_selector,dict(SELECTOR=(0xa740,127)))
    news=M.assemble(new_selector,dict(SELECTOR=(0xa740,127)))
    assert olds['used']['SELECTOR']==127 and news['used']['SELECTOR']<=127
    put(off(65,0xa740),olds['images']['SELECTOR'],news['images']['SELECTOR'].ljust(127,b'\xea'),'shared bounded selector, owner43 plus Mini admission, row0 mandatory full')
    def branch(q):return bytes((0x90,(q['symbols']['MiniFullCheck']-0xa7d7)&255,0xb0,(q['symbols']['MiniAuthorized']-0xa7d9)&255,0xea))
    put(off(65,0xa7d5),branch(olds),branch(news),'existing checked-result branches')
    # The retained source-fit file spells the actual inline-map revision;
    # every byte is asserted against this exact parent before substitution.
    oldh=M.assemble(Fit.OLD_HELPER,Fit.HELPER_LAYOUT)
    for name,oldname in (('GATE','GATE'),('UTIL','UTIL'),('HEADER','HEADER')):
        pc,size=LAYOUT[name]
        put(off(85,pc),oldh['images'][oldname].ljust(size,b'\xff'),p['images'][name].ljust(size,b'\xff'),'existing native85 '+name)
    kernel=M.kernel(parent)
    stamp=bytes.fromhex('a50e8d1bc1a9018d1ac1')
    assert kernel.count(stamp)==1
    ix=kernel.index(stamp)+2;pc=0xa000+ix
    physical=M.CHR+M.CODE_PAGES[ix//1024]*1024+ix%1024
    put(physical,kernel[ix:ix+3],b'\x20'+p['symbols']['StampSonicEpoch'].to_bytes(2,'little'),'Sonic HostMain successful epoch stamp')
    pc,size=LAYOUT['SONIC_EPOCH'];at=M.CHR+334*1024+(pc-0xd800)
    put(at,b'\xff'*size,p['images']['SONIC_EPOCH'].ljust(size,b'\xff'),'Sonic owner-private guarded epoch and stamp')
    oldcookie=parent[M.COOKIE_AT:M.COOKIE_AT+16]
    assert oldcookie==bytes.fromhex('a72b01')+sha256(b''.join(M.page(parent,n)for n in M.COOKIE_PAGES)).digest()[:13]
    cookie=oldcookie[:3]+sha256(b''.join(M.page(out,n)for n in M.COOKIE_PAGES)).digest()[:13]
    put(M.COOKIE_AT,oldcookie,cookie,'complete Sonic packet cookie')
    result=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,result,strict=True))if a!=b}
    owned={i for s in spans for i in range(s['file'],s['file']+s['bytes'])}
    assert changed<=owned
    assert parent[off(65,0xaee2):off(65,0xaf85)]==result[off(65,0xaee2):off(65,0xaf85)]
    assert parent[off(126,0x9c6e):off(126,0x9cb6)]==result[off(126,0x9c6e):off(126,0x9cb6)]
    assert parent[off(82,0xb16d):off(82,0xb189)]==result[off(82,0xb16d):off(82,0xb189)]
    return result,dict(parent_SHA256=PIN,candidate_SHA256=H(result),source_SHA256=H(SOURCE.read_bytes()),shared_selector_source_SHA256=H(Path(Shared.__file__).read_bytes()),selector_used=news['used'],used=p['used'],symbols=p['symbols'],selector_symbols=news['symbols'],spans=spans,changed_bytes=len(changed),state=dict(epoch=0xc3f0,exclusive_owner=43,cold_clear_half_open=[0xc000,0xc900]),all_unowned_exact=True,full_checker_and_Prince_predicate_exact=True,outputs=0,native_qualified=False)

if __name__=='__main__':
    _,q=proposal(M.ROM.read_bytes());print('SONIC AUTH PROPOSAL '+json.dumps(q,separators=(',',':')),flush=True)
