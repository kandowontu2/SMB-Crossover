"""Narrow memory-only Thomas native maturity/progression repair on a76."""
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

import check_thomas_earned_powerup_1110 as Route
import check_excitebike_powerup_progression_1110 as Ex

C,W,N,L=Ex.C,Ex.W,Ex.N,Ex.L
sys.path.insert(0,str(W.R/'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as Asm

PIN='a76d7610eed8493806200c52b96065af0369b926c55d033e17841f818756e2e0'
ORIGIN=1048592+426*1024
KERNEL_PIN='69a1e4d318c29b86eb8ec1485dfc2c5933d39769f3f22427cf9fb826fdeb2a21'
SOURCE=W.R/'tools/reference/thomas_powerup_progression_1110.s'
QUERIES=bytes.fromhex('08488a489848a50348a50448a50548a50648a50748a50848a50948a50a48a000207cb58d2ac8207cb58d2bc8a000208eb58d2cc8a00320a0b58d2dc868850a68850968850868850768850668850568850468850368a868aa682860')


def proposal(raw):
    assert sha256(raw).hexdigest()==PIN
    b=W.Symbols.bundle();old=raw[ORIGIN:ORIGIN+6144];assert sha256(old).hexdigest()==KERNEL_PIN
    # The native linked addresses shifted3 bytes from the retained symbol
    # aliases. Derive the current host query entry from the live side vector,
    # and verify its whole exact source body, not the stale nominal address.
    side=int.from_bytes(old[14*3+1:14*3+3],'little')
    start=side+18;end=start+len(QUERIES)
    assert (side,start,end)==(0xb5a0,0xb5b2,0xb60d)
    assert old[start-0xa000:end-0xa000]==QUERIES
    source=(W.R/'tools/reference/thomas_host_boundary_1031_v1.s').read_text()
    assert source.count('ThomasHostQueries:')==1 and source.count('jsr ThomasHostQueries')==0
    # This exported component lab helper is absent from all36 actual public
    # service roots. No kernel JSR/JMP operand names it or any interior byte.
    # Its sole source uses are its export/definition, never an address table.
    assert 'jmp ThomasHostQueries' not in source
    for i in range(len(old)-2):
        if old[i] in (0x20,0x4c):
            assert not start<=int.from_bytes(old[i+1:i+3],'little')<end,('query incoming direct root',hex(0xa000+i))
    roots=[int.from_bytes(old[i*3+1:i*3+3],'little') for i in range(36)]
    assert all(not start<=target<end for target in roots)
    for row in (23,33):assert old[row*3:row*3+3]==bytes.fromhex('4c6ca0')
    names=('PowerUpType','Enemy_State','SafecallA_SMC','GuestPowerupUpdate','FarcallJmpTarget_SMC','FarCallCommon')
    defs={name:W.address(b,name) for name in names}
    defs['GuestPowerupBank']=((W.location(b,'GuestPowerupUpdate')-16)//8192)|128
    code=Asm.assemble('\n'.join(f'{n}=${a:04x}' for n,a in defs.items())+'\n'+SOURCE.read_text(),
        {'POLICIES':(start,len(QUERIES))})
    body=code['images']['POLICIES'];assert len(body)==32
    kernel=bytearray(old);kernel[start-0xa000:start-0xa000+len(body)]=body
    for row,name in ((23,'ThomasNativeMature'),(33,'ThomasNativePowerupTick')):
        kernel[row*3:row*3+3]=b'\x4c'+code['symbols'][name].to_bytes(2,'little')
    # Match the existing full8192-byte kernel+8192-byte state fingerprint
    # recipe, including the retained template's two unloaded kernel pages.
    outputs=W.R/'build/thomas-current-lifts-1102-v2/sideoutputs'
    template=next(outputs.glob('*-kernel.bin')).read_bytes();state=next(outputs.glob('*-state.bin')).read_bytes()
    assert len(template)==len(state)==8192
    assert state[4096:6144]==raw[ORIGIN+6144:ORIGIN+8192]
    full_old=old+template[6144:]
    cookie_at=W.location(b,'ThCookie');old_cookie=raw[cookie_at:cookie_at+16]
    assert old_cookie==bytes([167,10,64,1])+sha256(full_old+state).digest()[:12]
    cookie=bytes([167,10,64,2])+sha256(bytes(kernel)+template[6144:]+state).digest()[:12]
    image=bytearray(raw);image[ORIGIN:ORIGIN+6144]=kernel;image[cookie_at:cookie_at+16]=cookie
    return bytes(image),bytes(kernel),cookie,dict(parent=PIN,query_retirement=[start,end],
        query_source_bytes=len(QUERIES),helper_bytes=len(body),maturity=code['symbols']['ThomasNativeMature'],
        tick=code['symbols']['ThomasNativePowerupTick'],cookie_file_offset=cookie_at,cookie=cookie.hex(),
        kernel_SHA256=sha256(kernel).hexdigest(),state_SHA256=sha256(state).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),all_other_kernel_bytes_unchanged=True)


def main():
    raw=Ex.proposal(Route.A5.proposal(W.ROM.read_bytes())[0])[0]
    image,kernel,cookie,record=proposal(raw)
    b=W.Symbols.bundle();b['raw']=image
    row=next(r for r in C.Starts.C.inventory(image)['rows'] if r['name']=='THOMAS')
    opening,m=C.cold(b,row)
    assert bytes(m.ram[3][:6144])==kernel
    assert all(bytes(m.ram[i][0x1fe0:0x1ff0])==cookie for i in (2,3))
    result=Route.route(m)
    assert result['passed'],result
    assert result['calls']['GuestPowerupUpdate']==60 and result['calls']['HandlePowerUpCollision']==1,result
    returned=next(e for e in result['events'] if e['event']=='native_collection_return')
    assert returned['slot']==4 and returned['erased'] and returned['floaty']==6 and returned['sound']==32 and returned['carry'],returned
    assert (result['final']['status'],result['final']['engine'],result['final']['active'],result['final']['timer'])==(1,8,0,0),result
    print(json.dumps(dict(passed=True,parent_ROM_SHA256=PIN,proposal_ROM_SHA256=sha256(image).hexdigest(),
        source_CPU_only=True,Mesen_run=False,ROM_written=False,output_files=0,record=record,
        genuine_cold=opening,natural=result)),flush=True)


if __name__=='__main__':main()
