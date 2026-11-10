"""Memory-only repair of current raw37's rejected native powerup tick.

The previous current census and continuation checkers are retained. This
proposal uses only the original Ex linker gap between ExHostEnd and CODE.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from unittest.mock import patch

import audit_current_roster_powerups_1110 as C
import check_roster_powerup_continuation_1110 as Route
import check_ff_white_mushroom_current_1110 as W
import check_ff_head_lifetime_irq_1110 as L
sys.path.insert(0,str(W.R/'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as Asm

N=C.N
SOURCE=W.R/'tools/reference/excitebike_powerup_progression_1110.s'
ORIGIN=1048592+728*1024
KERNEL_PIN='7ceb512a4427abf6ff77ce6a4b1c98badceb9dcb4b3264c453c168eced55e2f8'


def proposal(raw):
    assert sha256(raw).hexdigest()==C.PIN
    b=W.Symbols.bundle();original=raw[ORIGIN:ORIGIN+6144]
    assert sha256(original).hexdigest()==KERNEL_PIN
    old=W.R/'build/excitebike-pose-1101-v3'
    labels={n:int(a,16) for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',
        (old/'heat-host.lbl').read_text(),re.M)}
    assert (old/'heat-kernel.bin').read_bytes()==original
    assert labels['ExHostEnd']==0xaf7a
    # Explicit linker segment starts and emitted host-end label establish
    # this bounded gap. All original bytes must still equal the old linker
    # fill. We do not treat arbitrary zero bytes as free code.
    cfg=(old/'host.cfg').read_text()
    assert 'EX_HOST:load=K,type=ro,start=$a950;' in cfg and 'CODE:load=K,type=ro,start=$b000;' in cfg
    assert not [(n,a) for n,a in labels.items() if 0xaf7a<a<0xb000]
    assert original[0xf7a:0x1000]==bytes(134)
    assert original[0x563:0x566]==bytes.fromhex('4c6fa5')
    names=('SafecallA_SMC','FarcallJmpTarget_SMC','GuestPowerupUpdate','FarCallCommon')
    definitions={n:W.address(b,n) for n in names}
    definitions['GuestPowerupBank']=((W.location(b,'GuestPowerupUpdate')-16)//8192)|128
    code=Asm.assemble('\n'.join(f'{n}=${a:04x}' for n,a in definitions.items())+'\n'+SOURCE.read_text(),
        {'TICK':(0xaf7a,134)})
    leaf=code['images']['TICK'];assert len(leaf)==18
    kernel=bytearray(original);kernel[0xf7a:0xf7a+18]=leaf
    kernel[0x563:0x566]=bytes.fromhex('4c7aaf')
    metadata=raw[ORIGIN+6144:ORIGIN+8192];art=raw[ORIGIN+8192:ORIGIN+11264]
    assert metadata==(old/'host-metadata.bin').read_bytes() and art==(old/'body-native.chr').read_bytes()
    old_cookie=bytes([167,37,1])+sha256(original+metadata+art).digest()[:13]
    assert old_cookie==(old/'heat-cookie.bin').read_bytes() and raw.count(old_cookie)==1
    cookie=bytes([167,37,2])+sha256(kernel+metadata+art).digest()[:13]
    cookie_at=raw.index(old_cookie)
    assert 16+65*8192<=cookie_at<16+66*8192
    image=bytearray(raw);image[ORIGIN:ORIGIN+6144]=kernel;image[cookie_at:cookie_at+16]=cookie
    changed=[i for i,(a,z) in enumerate(zip(raw,image)) if a!=z]
    assert set(changed)<=set(range(ORIGIN+0x563,ORIGIN+0x566))|set(range(ORIGIN+0xf7a,ORIGIN+0xf7a+18))|set(range(cookie_at,cookie_at+16))
    return bytes(image),bytes(kernel),cookie,dict(helper=0xaf7a,helper_bytes=18,vector33=0xa563,
        cookie_file_offset=cookie_at,old_cookie=old_cookie.hex(),new_cookie=cookie.hex(),
        changed_bytes=len(changed),source_declared_gap=[0xaf7a,0xb000],
        kernel_SHA256=sha256(kernel).hexdigest(),source_SHA256=sha256(SOURCE.read_bytes()).hexdigest())


def main():
    raw=C.ROM.read_bytes();image,kernel,cookie,record=proposal(raw)
    b=W.Symbols.bundle();b['raw']=image
    row=next(r for r in C.Starts.C.inventory(image)['rows'] if r['name']=='EXCITEBIKE')
    opening,m=C.cold(b,row)
    assert bytes(m.ram[3][:6144])==kernel and bytes(m.ram[2][0x1fe0:0x1ff0])==cookie
    assert bytes(m.ram[3][0x1fe0:0x1ff0])==cookie
    results=[]
    for kind in range(4):
        q=Route.directed(m,kind,85);results.append(q)
        assert q['actor_erased'] and q['hosted_recovered'],q
        if kind<2:
            assert q['real_Main_NMI_updates']==60 and q['states'][-1]['PlayerStatus']==1,q
            assert q['states'][-1]['GameEngineSubroutine']==8 and q['states'][-1]['TimerControl']==0,q
            assert q['calls']['GuestPowerupUpdate']==60,q
        elif kind==2:assert q['collected']['StarInvincibleTimer']==35,q
        else:assert q['collected']['floaty']==11,q
        print(json.dumps(dict(event='fixed_directed_progression',kind=kind,updates=q['real_Main_NMI_updates'],
            final=q['states'][-1],calls=q['calls'])),flush=True)
    q=Route.natural(m,750)
    assert q['passed'],q
    print(json.dumps(dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,output_files=0,
        parent_ROM_SHA256=C.PIN,proposal_ROM_SHA256=sha256(image).hexdigest(),record=record,
        cold_actual_menu=opening,directed_cases=4,natural=q,
        scope='In-memory source proposal; actual cold native menu/parser, four directed callbacks and ordinary-controller first earned mushroom. Physical/native timing and broad lifecycle/IRQ qualification pending.')),flush=True)


if __name__=='__main__':main()
