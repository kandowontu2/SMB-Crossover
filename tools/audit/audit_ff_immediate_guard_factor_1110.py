"""Zero-growth FF immediate duplicate-guard proposal; in-memory CPU only.

Public gates and all full-cookie guards stay unchanged. Only an immediately
authenticated typed caller may enter that gate after its redundant guard.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import profile_ff_empty_cpu_v2_1110 as P

L,W,N,Fix=P.L,P.W,P.N,P.Fix
PROFILE_PIN='abeb873f46a97dadf2ed652a194d34540c3046a03266ba67e8d406b092915418'
PAIRS=(('FwSvcMovement','FwHostMovement'),('FwSvcHead','FwHostHead'),
       ('FwSvcSide','FwHostSide'),('FwSvcHeadWithin','FwHostHeadWithin'),
       ('FwSvcBody','FwHostBody'),('FwSvcAdder','FwHostAdder'),
       ('FwSvcBoxProfile','FwBox'),('FwSvcFullBox','FwHostBox'))


def proposal(image,b):
    output=bytearray(image);patches=[]
    check=W.address(b,'FwCheck');active=W.address(b,'FwSvcActive')
    for service,gate in PAIRS:
        at=W.location(b,gate);pc=W.address(b,gate)
        prefix=image[at:at+10]
        assert prefix[:5]==b'\x08\x20'+check.to_bytes(2,'little')+b'\xb0', (gate,prefix.hex())
        assert prefix[5]==3 and prefix[6]==0x4c and prefix[9]==0x28,(gate,prefix.hex())
        assert image[at+10:at+13]==b'\x8d'+(W.address(b,'SafecallA_SMC')+1).to_bytes(2,'little')
        start=W.location(b,service);size=int(b['syms'][service]['size'],0)
        data=image[start:start+size]
        assert data.count(b'\x20'+active.to_bytes(2,'little'))==1
        opcode=0x20 if service=='FwSvcMovement' else 0x4c
        target=bytes((opcode,))+pc.to_bytes(2,'little')
        assert data.count(target)==1,(service,data.hex())
        offset=data.index(target)
        assert data[offset-1]==0x28,(service,data.hex())
        before=image[start+offset:start+offset+3]
        after=bytes((opcode,))+(pc+10).to_bytes(2,'little')
        output[start+offset:start+offset+3]=after
        patches.append(dict(service=service,public_gate=gate,transfer=W.address(b,service)+offset,
            file=start+offset,old=before.hex(),new=after.hex(),ready=pc+10,skipped_prefix=prefix.hex()))
    # These are operand replacements, with no newly allocated byte or lease.
    changed=[i for i,(a,z) in enumerate(zip(image,output)) if a!=z]
    assert len(output)==len(image) and len(changed)<=16
    assert all(any(r['file']+1<=i<r['file']+3 for r in patches) for i in changed)
    for _,gate in PAIRS:
        at=W.location(b,gate);assert output[at:at+26]==image[at:at+26]
    return bytes(output),patches,changed


def main():
    assert sha256(Path(P.__file__).read_bytes()).hexdigest()==PROFILE_PIN
    original=W.ROM.read_bytes();assert sha256(original).hexdigest()==W.PIN
    image,kernel,cookie,*_=Fix.proposal(original);assert sha256(image).hexdigest()==L.PIN
    b=W.Symbols.bundle();trial,patches,changed=proposal(image,b)
    with patch.object(L,'sample',lambda *a,**k:None):
        old,oldcold,_=L.cold_menu(image,0,cookie,kernel)
        new,newcold,_=L.cold_menu(trial,0,cookie,kernel)
    assert L.app(old)==L.app(new)
    entries={(190,W.address(b,name)):name for pair in PAIRS for name in pair}
    entries[190,W.address(b,'FwCheck')]='FwCheck'
    rows=[]
    for phase,pad in (('idle_empty',0),('walking_empty',1)):
        for update in range(16):
            results=[]
            for m in (old,new):
                before=P.state(m)
                assert not any(before['enemy_flags']) and (before['lives'],before['engine'])==(2,8)
                m.controller_pad=pad;W.clear_logs(m);nmi=P.normal_nmi(m)
                idle=W.address(b,'IdleLoop');c=N.NesMPU(memory=m,pc=idle)
                c.sp,c.p=255,0x31;c.stPushWord(0xe33b);calls=Counter()
                for _ in range(300000):
                    if (c.pc,c.sp)==(idle+12,252):break
                    name=entries.get(P.point(m,c.pc))
                    if name:calls[name]+=1
                    assert m[c.pc];c.step()
                else:raise AssertionError('Main bound')
                results.append(dict(cycles=c.processorCycles,NMI=nmi,calls=dict(calls),regs=L.regs(c),
                    hardware=tuple(m.ppu_log),state=P.state(m)))
                assert not any(P.state(m)['enemy_flags']) and not m.blocked
            a,z=results
            assert L.app(old)==L.app(new),(phase,update,'application difference')
            assert all(a[k]==z[k] for k in ('NMI','regs','hardware','state')),(phase,update,a,z)
            assert (a['calls']['FwCheck'],z['calls']['FwCheck'])==(29,21),(phase,update,a,z)
            assert a['cycles']-z['cycles']==2728,(phase,update,a,z)
            rows.append(dict(phase=phase,update=update,before=a['cycles'],after=z['cycles'],saved=2728,
                old_cookie_checks=29,new_cookie_checks=21,state=z['state']))
    print(json.dumps(dict(passed=True,in_memory_proposal_only=True,source_CPU_only=True,
        Mesen_run=False,output_files=0,ROM_written=False,parent_SHA256=L.PIN,
        proposed_SHA256=sha256(trial).hexdigest(),kernel_unchanged=True,cookie_unchanged=True,
        changed_bytes=len(changed),new_allocated_bytes=0,patches=patches,cold_old=oldcold,cold_new=newcold,
        actual_Main_updates=len(rows),saved_cycles_each_Main=2728,
        first=rows[0],last=rows[-1],
        scope='Eight immediate typed transfers only. Full owner/cookie guard remains at every typed native entry and every public gate. Actual cold/menu and32 empty controller Main pairs have equal AXYP/stack/nativebody/FFstate/OAM/PPU/NMI results, differing only dead stack and redundant mapper transactions. Conditional proposal: broad lifecycle/fault/real-IRQ and fullstage qualification still required; no candidate written.')),flush=True)


if __name__=='__main__':main()
