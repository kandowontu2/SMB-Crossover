"""Source-funded stateless FF mux tail; memory-only CPU proposal and proofs."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
from py65.disassembler import Disassembler

import audit_ff_immediate_guard_factor_1110 as G
import audit_ff_retired_palette_funding_1110 as Funding

L,W,N,Fix=G.L,G.W,G.N,G.Fix
R=W.R
SOURCE=R/'tools/reference/ff_mux_unused_tail_1110.s'
BASE_PIN='58811ce678361678deff8f32966e945869be75e0f017e2bf36b2e2430ab96ebd'
SEAMS=set();COUNTS=Counter()


def proposal(raw):
    image,kernel,cookie,*_=Fix.proposal(raw)
    b=W.Symbols.bundle();image,redirects,_=G.proposal(image,b)
    assert sha256(image).hexdigest()==BASE_PIN
    begin=W.address(b,'FfMuxNativeLate');end=W.address(b,'FfMuxNativeLateEnd')
    assert (begin,end)==(0xbecf,0xbfd6)
    # Explicit granted MAIN capacity ends at BFE0, before the cookie; this
    # is source-declared residual capacity, never inferred FF-byte padding.
    reservation=json.loads((R/'docs/qa/checkpoints/2026-10-30/ff-source-epoch-reservations/receipt.json').read_text())
    assert any(h['start']==begin and h['end']==0xbfe0 and h['bytes']==273 for h in reservation['FF_exclusive_RAM3_code_only']['holes'])
    assert kernel[end-0xa000:0x1fe0]==b'\xff'*10
    # B679..B68B is the18B remainder of the closed27B palette-pointer
    # retirement. V2 owns its first9B priority leaf and preserves B68B Mux.
    assert kernel[0x1679:0x168b]==b'\xff'*18
    attr=W.address(b,'Player_SprAttrib').to_bytes(2,'little')
    assert kernel[0x1670:0x1679]==b'\xad'+attr+b'\x29\x20\x8d'+attr+b'\x60'
    assert sha256(raw[1048592+893*1024+0x1670:1048592+893*1024+0x168b]).hexdigest()=='04f8ffb4dca20b686e6445b1771d644482df154441c01b0f89a02b32ec33b721'
    roots=[target for _,target in Funding.gateways(image,b)]
    seen,_,indirect=Funding.walk(kernel,roots)
    assert not indirect and not any(0xb679<=pc<0xb68b or end<=pc<0xbfe0 for pc in seen)
    main=kernel[begin-0xa000:end-0xa000]
    pattern=bytes((0xa9,0xef,0x85,W.address(b,'R6'),0xa5,W.address(b,'R0'),0xcd))+W.address(b,'RgOamUsed').to_bytes(2,'little')+b'\xb0'
    assert main.count(pattern)==1
    branch=begin+main.index(pattern)+9
    old=kernel[branch-0xa000:branch-0xa000+2]
    assert branch+2+(old[1] if old[1]<128 else old[1]-256)==W.address(b,'FfMuxEpochClearTag')
    packet=b'\x20'+W.address(b,'FfMuxPacket').to_bytes(2,'little')
    assert main.count(packet)==1
    packet_at=begin+main.index(packet)
    definitions={n:W.address(b,n) for n in ('Sprite_Attributes','RgOamRotation')}
    definitions['FfMuxOriginalPacketCall']=packet_at
    preamble='\n'.join(f'{n}=${v:04x}' for n,v in definitions.items())
    program=Fix.V1.Asm.assemble(preamble+'\n'+SOURCE.read_text(),{'TAIL':(0xb679,18),'STUB':(end,10)})
    assert program['used']==dict(TAIL=18,STUB=6)
    revised=bytearray(kernel)
    revised[0x1679:0x168b]=program['images']['TAIL']
    revised[end-0xa000:end-0xa000+6]=program['images']['STUB']
    delta=program['symbols']['FfMuxUnusedTailStub']-(branch+2)
    assert -128<=delta<=127
    revised[branch-0xa000+1]=delta&255
    assert revised[0x1fe0:0x1ff0]==b'\xff'*16
    newcookie=bytes((0xa7,22,0,12))+sha256(revised).digest()[:12]
    out=bytearray(image);out[1048592+893*1024:1048592+901*1024]=revised
    out[511774:511790]=newcookie
    return bytes(out),bytes(revised),newcookie,program,dict(branch=branch,old=old.hex(),new=bytes((old[0],delta&255)).hex(),packet=packet_at),image,kernel,cookie


def signature(m,c):
    return (L.regs(c),bytes(m[:256]),bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000]),
        bytes(m[0x15a:0x17b]),tuple(bytes(v) for v in m.ram[:3]),tuple(m.rawtags),
        m.vram,m.chr_latches,m.upper,m.ppu_addr,m.toggle,m.ppuctrl,tuple(m.ppu_log))


def seam(m,c,stop,key=None):
    if c.pc>=0x8000 and m.rawtags[(c.pc-0x8000)//8192]==3 and c.pc in SEAMS:
        token=(c.pc,key,c.p&4)
        if token not in L.SAMPLE_KEYS:
            L.SAMPLE_KEYS.add(token);q,d=L.clone(m,c)
            L.SAMPLES.append(('mux_unused_tail',stop,q,d))


def frame(m,observe=False):
    idle=W.address(m.bundle,'IdleLoop');W.clear_logs(m);N.consume(m)
    c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
    L.finish(m,c,(idle+12,252),(lambda q,d:seam(q,d,(idle+12,252))) if observe else None)
    return c


def bind(seed,image,kernel,cookie):
    m=L.clone(seed);m.bundle=dict(m.bundle,raw=image);m.ram[3][:]=kernel
    m.ram[3][0x1fe0:0x1ff0]=cookie
    for i,tag in enumerate(m.rawtags):
        if tag&128:m.raw_page(i,tag)
    return m


def mux_units(seed,image,trial,oldkernel,kernel,oldcookie,cookie):
    b=seed.bundle;entry=W.address(b,'FfMuxNativeLate')
    minimum=maximum=None
    for rotation in range(0,256,4):
        for count in range(64):
            case=rotation*16+count;outputs=[];cycles=[]
            for raw,code,header in ((image,oldkernel,oldcookie),(trial,kernel,cookie)):
                m=bind(seed,raw,code,header);m.raw_page(1,3)
                N.put(m,CurrentBank=3,NmiDisable=255,RgOamRotation=rotation,RgOamUsed=count*4,
                    RgOamPlayerStart=((case*7)%16)*4,SmFreezeTurn=(case%8 if case%8<7 else 255),
                    SmFreezePaletteControl=(0,1,4,5,8,255)[case%6],AreaType=(0,1,2,3,4,255)[case%6])
                for i in range(256):m[0x200+i]=(73*i+17*case+29)&255
                for part in range(64):m[0x200+part*4]=(0,31,239,240,248,255)[(part+case)%6]
                for slot in (0,12,24):m[0x5c1c+slot]=(case+slot//12)%5
                c=N.NesMPU(memory=m,pc=entry)
                c.a,c.x,c.y,c.p,c.sp=83,71,37,0x35,224;c.stPushWord(0x5aff)
                L.finish(m,c,(0x5b00,224),(lambda q,d:seam(q,d,(0x5b00,224),'unit_masked')) if raw is trial and rotation==0 and count in (0,1,63) else None)
                expected=bytearray(code);expected[0x1fe0:0x1ff0]=header
                assert bytes(m.ram[3])==expected
                outputs.append(signature(m,c));cycles.append(c.processorCycles)
            assert outputs[0]==outputs[1],('all-tail/rotation/mux/OAM unit difference',rotation,count)
            saved=cycles[0]-cycles[1]
            minimum=saved if minimum is None else min(minimum,saved)
            maximum=saved if maximum is None else max(maximum,saved)
            COUNTS['all64_rotations_all64_used_counts_full_mux_pairs']+=1
    assert minimum==-8 and maximum==1378,(minimum,maximum)
    print(json.dumps(dict(event='full_mux_matrix_pass',cases=dict(COUNTS),saved_min=minimum,saved_max=maximum,
        dense_frame_limit='One unused sprite costs8 more cycles; zero-unused original path unchanged.')),flush=True)


def lifecycle(seed,image,trial,oldkernel,kernel,oldcookie,cookie):
    for variant in range(4):
        for scenario in ('ready','new_life','life_award','new_area','new_world','unready'):
            outputs=[]
            for raw,code,header in ((image,oldkernel,oldcookie),(trial,kernel,cookie)):
                m=bind(seed,raw,code,header)
                N.put(m,FfVariant=variant,FfPower=2,FfEarned=2,FfHealCharges=3 if variant==1 else 0,
                    SavedJoypadBits=0,SavedJoypad1Bits=0,A_B_Buttons=0,Player_State=0)
                if scenario=='new_life':N.put(m,NumberofLives=1)
                elif scenario=='life_award':N.put(m,NumberofLives=3)
                elif scenario=='new_area':N.put(m,AreaAddrsLOffset=1)
                elif scenario=='new_world':N.put(m,WorldNumber=1)
                elif scenario=='unready':N.put(m,FfReady=0)
                m.controller_pad=0;c=frame(m)
                outputs.append(signature(m,c))
            assert outputs[0]==outputs[1],('whole Main lifecycle difference',variant,scenario)
            COUNTS['four_class_six_scenarios_actual_Main_lifecycle_pairs']+=1
    for flags in (0x31,0xf1):
        for byte in range(16):
            outputs=[]
            for raw,code,header in ((image,oldkernel,oldcookie),(trial,kernel,cookie)):
                m=bind(seed,raw,code,header);m.ram[3][0x1fe0+byte]^=1;N.put(m,NmiDisable=255)
                entered=[]
                def watch(q,d):
                    if d.pc>=0x8000 and q.rawtags[(d.pc-0x8000)//8192]==3:entered.append(d.pc)
                c=L.call(m,'FwHostGraphics',x=0,y=0,p=flags,observe=watch)
                assert not entered and not c.p&1
                outputs.append(signature(m,c))
            assert outputs[0]==outputs[1],('full-cookie rejection differs',byte,flags)
            COUNTS['all16_header_bytes_two_flags_reject_source_graphics']+=1
    m=bind(seed,trial,kernel,cookie);L.forced(m);reads=m.ppu_reads;c=L.call(m,'FwLoad')
    assert c.p&1 and m.ppu_reads==reads;COUNTS['new_warm_zero_reads']+=1
    m=bind(seed,trial,oldkernel,oldcookie);c=L.call(m,'FwCheck');assert not c.p&1
    L.forced(m);reads=m.ppu_reads;c=L.call(m,'FwLoad')
    assert c.p&1 and m.ppu_reads-reads==16400
    COUNTS['588_warm_rejected_then_real_new_cold_reload']+=1
    print(json.dumps(dict(event='lifecycle_and_cookie_pass',cases=dict(COUNTS))),flush=True)


def main():
    trial,kernel,cookie,program,hook,image,oldkernel,oldcookie=proposal(W.ROM.read_bytes())
    memory=[0]*65536;memory[0xa000:0xc000]=kernel
    dis=Disassembler(N.NesMPU(memory=memory));SEAMS.add(hook['branch'])
    for start,size in ((0xb679,18),(0xbfd6,6)):
        at=start
        while at<start+size:SEAMS.add(at);at+=dis.instruction_at(at)[0]
        assert at==start+size
    with patch.object(L,'sample',lambda *a,**k:None):
        old,oldcold,_=L.cold_menu(image,0,oldcookie,oldkernel)
        new,newcold,_=L.cold_menu(trial,0,cookie,kernel)
    savings=[];L.SAMPLES.clear();L.SAMPLE_KEYS.clear();L.PATHS.clear();L.DEEPEST=None
    for phase,pad in (('idle',0),('walking',1)):
        for update in range(16):
            cpus=[]
            for m in (old,new):
                assert not any(N.get(m,'Enemy_Flag',i) for i in range(6))
                m.controller_pad=pad;cpus.append(frame(m,m is new))
            assert signature(old,cpus[0])==signature(new,cpus[1]),('actual Main mismatch',phase,update)
            savings.append(cpus[0].processorCycles-cpus[1].processorCycles)
            COUNTS['actual_empty_Main_pairs']+=1
    assert min(savings)>900,savings
    print(json.dumps(dict(event='actual_Main_pass',saved=savings,mean=sum(savings)/len(savings),
        new_Main=cpus[1].processorCycles,branch=hook,program_bytes=program['used'])),flush=True)
    mux_units(new,image,trial,oldkernel,kernel,oldcookie,cookie)
    lifecycle(new,image,trial,oldkernel,kernel,oldcookie,cookie)
    reached={c.pc for _,_,_,c in L.SAMPLES}
    assert reached==SEAMS,('missing changed instruction seams',sorted(SEAMS-reached))
    q,d=L.clone(new,cpus[1]);L.SAMPLES.append(('genuine_idle_normal_NMI',(d.pc,d.sp),q,d))
    vectors=L.irq_checks(image)
    print(json.dumps(dict(passed=True,proposal_only=True,source_CPU_only=True,Mesen_run=False,
        ROM_written=False,output_files=0,parent_SHA256=BASE_PIN,proposal_SHA256=sha256(trial).hexdigest(),
        kernel_SHA256=sha256(kernel).hexdigest(),cookie=cookie.hex(),source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
        code_bytes=program['used'],hook=hook,cold=[oldcold,newcold],saved_min=min(savings),saved_max=max(savings),
        saved_mean=sum(savings)/len(savings),cases=dict(COUNTS),all_changed_instruction_seams=len(SEAMS),real_vectors=vectors,
        scope='Actual paired empty Main, explicit all-tail/rotation/arbitrary-OAM full mux units and lifecycle/header fixtures, with actual IRQ/NMI cuts. Full metadata clearing retained; no unused-attribute-zero assumption. Source proposal only; no fullstage or native cadence claim, and overwhelming lag remains.')),flush=True)


if __name__=='__main__':main()
