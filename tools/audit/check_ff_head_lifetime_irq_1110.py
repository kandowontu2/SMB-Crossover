"""Frozen FFv2 cold/menu, ABI, rejection and real-vector CPU checks; stdout.

Controller cold starts are distinguished from explicit lifecycle/terrain/ABI
and interrupt-cut fixtures. No ROM, packet, receipt or capture is written.
"""
import argparse
from collections import Counter
import copy
from hashlib import sha256
import json
from pathlib import Path
from py65.disassembler import Disassembler

import check_ff_head_corner_1110_v2 as Fix
import check_ff_white_mushroom_current_1110 as W

N, UI = W.N, W.UI
PIN = '96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd'
SOURCE_PIN = '6e58b2460852e808031f64ce733545ca0bffc78da05e5b68860d929e98c7f0cd'
CHECKER_PIN = 'e508771dbac9dfb42c33ca41b3d3af4c07f98f81fd2f742205f6e4a3ce690665'
SAMPLES, SAMPLE_KEYS = [], set()
PATHS=Counter()
DEEPEST=None
PATCHED_PCS={0xb907,0xb996,0xb9a0,0xb9aa,0xb3d3,0xb3d6,0xb3d7}


def clone(m, c=None):
    q = list.__new__(type(m))
    list.extend(q, list.__iter__(m))
    for name, value in m.__dict__.items():
        setattr(q, name, value if name == 'bundle' else
                [] if name in ('writes','ram_writes','ppu_log','blocked') else copy.deepcopy(value))
    if c is None:
        return q
    d = copy.copy(c)
    d.memory = q
    return q, d


def regs(c):
    return c.pc, c.a, c.x, c.y, c.p, c.sp


def finish(m, c, stop, observe=None):
    for _ in range(500000):
        if (c.pc,c.sp) == stop:
            return c
        if observe:
            observe(m,c)
        assert m[c.pc], ('BRK',hex(c.pc),m.rawtags)
        c.step()
    raise AssertionError(('CPU bound',hex(c.pc),c.sp,stop))


def start(m, name, a=83, x=71, y=37, p=0x31):
    at = W.address(m.bundle,name)
    m[W.address(m.bundle,'SafecallA_SMC')+1] = a
    target = W.address(m.bundle,'FarcallJmpTarget_SMC')
    m[target+1],m[target+2] = at & 255,at >> 8
    c = N.NesMPU(memory=m,pc=W.address(m.bundle,'FarCallCommon'))
    c.a = ((W.location(m.bundle,name)-16)//8192)|128
    c.x,c.y,c.p,c.sp = x,y,p,224
    c.stPushWord(0x5aff)
    return c


def call(m, name, observe=None, **kw):
    W.clear_logs(m)
    return finish(m,start(m,name,**kw),(0x5b00,224),observe)


def app(m):
    return (bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000]),
            tuple(bytes(r) for r in m.ram),tuple(m.rawtags))


def body(m):
    names = ('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
             'Player_Y_Speed','Player_State','NumberofLives','GameEngineSubroutine')
    return tuple(N.get(m,n) for n in names),bytes(m[0x5c00:0x5fff])


def sample(m,c,stop,origin,key=None):
    if c.pc < 0x8000 or not getattr(m,'ff_derivative',False):
        return
    tag = m.rawtags[(c.pc-0x8000)//8192]
    own = tag == 3 and (0xb620 <= c.pc < 0xb66f or 0xb670 <= c.pc < 0xb679 or
                       0xbb47 <= c.pc < 0xbb55 or c.pc in PATCHED_PCS)
    if not own and key is None:
        return
    token = (origin,tag,c.pc,key) if key is not None else (tag,c.pc)
    if token not in SAMPLE_KEYS:
        SAMPLE_KEYS.add(token)
        q,d = clone(m,c)
        SAMPLES.append((origin,stop,q,d))


def frame(m, observe=None):
    idle = W.address(m.bundle,'IdleLoop')
    m.controller_pad = 0
    W.clear_logs(m)
    N.consume(m)
    c = N.NesMPU(memory=m,pc=idle)
    c.sp,c.p = 255,0x31
    c.stPushWord(0xe33b)
    stop = (idle+12,252)
    def watch(mem,cpu):
        sample(mem,cpu,stop,'genuine_menu_Main')
        if observe:
            observe(mem,cpu)
    return finish(m,c,stop,watch)


def cold_menu(raw, variant, cookie, kernel):
    b = W.Symbols.bundle();b['raw'] = raw
    new_image = sha256(raw).hexdigest() == PIN
    previous = N.Bus;N.Bus = W.ControllerBus
    try:
        m = UI.seed(b,21)
    finally:
        N.Bus = previous
    m.ff_derivative=new_image
    for _ in range(variant):
        UI.key(m,32)
    begin = UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',
             a=begin['A'],x=begin['X'],y=begin['Y'],p=begin['P'])
    N.invoke(m,'PauseRoutine',a=0)
    pending, loads = None, []
    load_pc = W.address(b,'FwLoad')
    def observe(mem,c):
        nonlocal pending
        if pending and (c.pc,c.sp) == pending['return']:
            if c.p & 1:
                writes = [r for r in mem.ram_writes[pending['writes']:] if r[0] == 3]
                delta = mem.ppu_reads-pending['reads']
                if delta:
                    assert delta == 16400 and writes[0] == (3,0x1fe0,0)
                    assert writes[-1] == (3,0x1fe0,167)
                    assert bytes(mem.ram[3][0x1fe0:0x1ff0]) == cookie
                    expected = bytearray(kernel);expected[0x1fe0:0x1ff0] = cookie
                    assert bytes(mem.ram[3]) == expected
                    loads.append(dict(PPU_reads=delta,RAM3_writes=len(writes),first=writes[0],last=writes[-1]))
            pending = None
        if c.pc >= 0x8000:
            tag = mem.rawtags[(c.pc-0x8000)//8192]
            if tag == 3:
                assert bytes(mem.ram[3][0x1fe0:0x1ff0]) == cookie, ('unready source execution',hex(c.pc))
            if tag == 190 and c.pc == load_pc:
                ret = mem[0x100+((c.sp+1)&255)]+256*mem[0x100+((c.sp+2)&255)]+1
                pending = dict(return_ignored=0,reads=mem.ppu_reads,writes=len(mem.ram_writes))
                pending['return'] = (ret,(c.sp+2)&255)
            if new_image and variant == 0 and tag == 190 and c.pc in {
                W.address(b,'FwCopy256'),W.address(b,'FwVerify256'),W.address(b,'FwPublishCookie')}:
                # One actual cold copy/readback point, plus validity publication.
                sample(mem,c,(W.address(b,'IdleLoop')+12,252),'genuine_cold',
                       (N.get(mem,'R1'),c.x if c.pc == W.address(b,'FwPublishCookie') else 0))
    for epoch in range(250):
        last_cpu=frame(m,observe)
        if (N.get(m,'OperMode'),N.get(m,'OperMode_Task'),N.get(m,'GameEngineSubroutine')) == (1,3,8):
            break
    else:
        raise AssertionError('cold controller bound')
    # Execute the first real active movement/body Main as well, so the new
    # capture wrapper and all retargeted head candidates have reached cuts.
    last_cpu=frame(m,observe)
    assert N.get(m,'FfVariant') == variant and len(loads) == 1
    return m,dict(variant=variant,first_active_Main=epoch+1,Main_updates=epoch+2,
                  cold=loads[0],cookie=cookie.hex()),last_cpu


def forced(m):
    N.put(m,SelectedCharacter=22,OperMode=1,Mirror_PPUMASK=0,
          DisableScreenFlag=1,NmiDisable=255)


def lifecycle(old, new, original, trial, kernel, cookie):
    rows = Counter()
    for variant in range(4):
        m = clone(new);forced(m);N.put(m,FfVariant=variant)
        before,reads = bytes(m.ram[3]),m.ppu_reads
        c = call(m,'FwLoad')
        assert c.p & 1 and m.ppu_reads == reads and bytes(m.ram[3]) == before
        rows['new_warm_zero_PPU_reads'] += 1
    m = clone(old);m.bundle = dict(m.bundle,raw=trial)
    for i,tag in enumerate(m.rawtags):
        if tag & 128:m.raw_page(i,tag)
    c = call(m,'FwCheck');assert not c.p & 1
    forced(m);reads=m.ppu_reads;c=call(m,'FwLoad')
    assert c.p & 1 and m.ppu_reads-reads == 16400
    assert bytes(m.ram[3][0x1fe0:0x1ff0]) == cookie
    expected=bytearray(kernel);expected[0x1fe0:0x1ff0]=cookie
    assert bytes(m.ram[3]) == expected
    rows['old_warm_rejected_then_real_cold_reload'] += 1
    # Fault the destination immediately before its first genuine readback.
    m=clone(old);m.bundle=dict(m.bundle,raw=trial)
    for i,tag in enumerate(m.rawtags):
        if tag & 128:m.raw_page(i,tag)
    forced(m);fault=[]
    def inject(mem,c):
        if c.pc == W.address(mem.bundle,'FwVerify256') and not fault:
            mem.ram[3][0] ^= 1;fault.append(1)
    c=call(m,'FwLoad',observe=inject)
    assert fault and not c.p & 1 and m.ram[3][0x1fe0] == 0
    rows['native_readback_fault_rejects_validity'] += 1
    for byte in range(16):
        for name in ('FwHostHead','FwHostMovement'):
            for flags in (0x31,0xf1):
                m=clone(new);m.ram[3][0x1fe0+byte]^=1
                N.put(m,NmiDisable=255)
                before=app(m);entered=[]
                def watch(mem,c):
                    if c.pc>=0x8000 and mem.rawtags[(c.pc-0x8000)//8192] == 3:entered.append(c.pc)
                    if c.pc == W.address(mem.bundle,'FwCheckByte')+3 and c.x == byte:
                        sample(mem,c,(0x5b00,224),'header_fault',(byte,name))
                c=call(m,name,p=flags,observe=watch)
                # Genuine FarCallCommon loads transported A before the gate,
                # so its incoming N/Z correspond to A83, independently of
                # the caller's deliberately contradictory fixture flags.
                expected_flags = flags & ~0x83
                assert (c.a,c.x,c.y,c.p) == (83,71,37,expected_flags), (byte,name,hex(flags),regs(c))
                assert not entered and app(m)==before
                rows['full_header_fault_gate_rejections'] += 1
    for owner in range(256):
        if owner == 22:continue
        m=clone(new);N.put(m,SelectedCharacter=owner);before=app(m)
        c=call(m,'FwHostHead')
        assert (c.a,c.x,c.y,c.p)==(83,71,37,0x30) and app(m)==before
        rows['foreign_owner_gate_rejections'] += 1
    # Paired native callback fixtures: identical application state, each
    # version's correctly authenticated original cold code and ROM.
    old_kernel=original[1048592+893*1024:1048592+901*1024]
    old_cookie=original[511774:511790]
    for field in ('GameEngineSubroutine','GamePauseStatus'):
        for value in range(256):
            pair=[]
            for raw,code,header in ((original,old_kernel,old_cookie),(trial,kernel,cookie)):
                m=clone(new);m.bundle=dict(m.bundle,raw=raw);m.ram[3][:]=code
                m.ram[3][0x1fe0:0x1ff0]=header
                for i,tag in enumerate(m.rawtags):
                    if tag & 128:m.raw_page(i,tag)
                fields=dict(GameEngineSubroutine=8,GamePauseStatus=0);fields[field]=value
                N.put(m,**fields)
                before=bytes(m.ram[3]);c=call(m,'FwSvcHead',y=0)
                assert bytes(m.ram[3])==before
                pair.append(((c.a,c.x,c.y,c.p,c.sp),bytes(m[:256]),
                             bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000]),tuple(m.rawtags)))
            assert pair[0]==pair[1], ('native callback matrix',field,value)
            rows['native_callback_'+field+'_0_to_255'] += 1
    for variant in range(4):
        for scenario in ('ready','new_life','life_award','new_area','new_world','unready'):
            pair=[]
            for raw,code,header in ((original,old_kernel,old_cookie),(trial,kernel,cookie)):
                m=clone(new);m.bundle=dict(m.bundle,raw=raw);m.ram[3][:]=code
                m.ram[3][0x1fe0:0x1ff0]=header
                for i,tag in enumerate(m.rawtags):
                    if tag&128:m.raw_page(i,tag)
                N.put(m,FfVariant=variant,FfPower=2,FfEarned=2,
                      FfHealCharges=3 if variant==1 else 0,SavedJoypadBits=0,
                      SavedJoypad1Bits=0,A_B_Buttons=0,Player_State=0)
                if scenario=='new_life':N.put(m,NumberofLives=1)
                elif scenario=='life_award':N.put(m,NumberofLives=3)
                elif scenario=='new_area':N.put(m,AreaAddrsLOffset=1)
                elif scenario=='new_world':N.put(m,WorldNumber=1)
                elif scenario=='unready':N.put(m,FfReady=0)
                current=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                before=bytes(m.ram[3]);c=call(m,'FwHostMovement')
                assert bytes(m.ram[3])==before
                assert N.get(m,'FfVariant')==variant
                power=0 if scenario in ('new_life','unready') else 2
                charges=3 if variant==1 and power else 0
                assert (N.get(m,'FfPower'),N.get(m,'FfEarned'),N.get(m,'FfHealCharges'))==(power,power,charges)
                ff=bytearray(m[0x5c00:0x6000]);ff[0x48:0x4a]=b'\x00\x00'
                pair.append(((c.a,c.x,c.y,c.p,c.sp),bytes(m[:256]),bytes(m[0x200:0x800]),
                             bytes(ff),tuple(m.rawtags),tuple(bytes(z) for z in m.ram[:3])))
                if raw is trial:
                    assert bytes(m[0x5c48:0x5c4a])==current.to_bytes(2,'little')
            assert pair[0]==pair[1], ('genuine Ensure via movement',variant,scenario)
            rows['life_area_world_Ensure_callback_pairs']+=1
    return dict(rows)


def abi(seed, program):
    rows=Counter();b=seed.bundle;at=W.address(b,'FfRenderBuffer')
    climb=next(i for i in range(256) if seed[W.address(b,'MTileAttribute')+i]&2)
    for previous in (2225,2226,2239):
        for tile in (0,0x61,0x23,0xc2,0xc3,climb):
            for y in range(256):
                for flags in (0x31,0xf1):
                    pair=[]
                    for target in (W.address(b,'FfHostRead'),program['symbols']['FfCornerHeadRead']):
                        m=clone(seed);m.raw_page(1,3)
                        N.put(m,CurrentBank=3,NmiDisable=255,Player_X_Position=0xb2,
                              Player_PageLoc=8,Player_Y_Position=144,Player_Y_HighPos=1,Player_Y_Speed=255)
                        for a in range(0x300,0x4a0):m[a]=0
                        m[0x37c]=tile;m[at+3],m[at+4],m[at+5]=14,0,y
                        m[at+8],m[at+9]=previous&255,previous>>8
                        m[3],m[4]=85,166
                        before=body(m)
                        c=N.NesMPU(memory=m,pc=target)
                        c.a,c.x,c.y,c.p,c.sp=83,71,y,flags,224;c.stPushWord(0x5aff)
                        def watch(mem,cpu):sample(mem,cpu,(0x5b00,224),'isolated_head_ABI')
                        finish(m,c,(0x5b00,224),watch if target != W.address(b,'FfHostRead') else None)
                        assert (m[3],m[4])==(85,166)
                        assert body(m)[0]==before[0] and bytes(m.ram[3])==bytes(seed.ram[3])
                        pair.append((c,m))
                    c,_=pair[0];d,mem=pair[1]
                    attr=seed[W.address(b,'MTileAttribute')+tile]
                    filtered=previous==2225 and attr&3==1 and tile not in (0xc2,0xc3)
                    expected=0 if filtered else tile
                    expected_p=(c.p & ~0x82)|(0x80 if expected&128 else 0)|(2 if not expected else 0)
                    # Endpoint ADCs have defined V0 for these B1/B2+1/14
                    # and page8 fixtures. RawRead's SBC32 can set V1.
                    # V is not a raw-reader preservation contract; C remains
                    # the native valid-cell result, and real callers follow.
                    if attr&3==1 and tile not in (0xc2,0xc3):
                        expected_p &= ~0x40
                    assert (d.a,d.x,d.y,d.p,d.sp)==(expected,0,y,expected_p,224), (previous,tile,y,hex(flags),regs(c),regs(d),expected,hex(expected_p))
                    rows['all_Y_indices_exact_AXYP_SP_R0_R1_body']+=1
    leaf=program['symbols']['FfNativePipePriority']
    for value in range(256):
        m=clone(seed);m.raw_page(1,3);N.put(m,CurrentBank=3,NmiDisable=255,Player_SprAttrib=value)
        c=N.NesMPU(memory=m,pc=leaf);c.a,c.x,c.y,c.p,c.sp=83,71,37,0x31,224;c.stPushWord(0x5aff)
        finish(m,c,(0x5b00,224),lambda mem,cpu:sample(mem,cpu,(0x5b00,224),'priority_ABI'))
        assert (c.a,c.x,c.y,c.sp)==(value&32,71,37,224)
        assert N.get(m,'Player_SprAttrib')==value&32
        rows['priority_all256_inputs_preserve_only_native20']+=1
    return dict(rows)


def head_callbacks(seed,original,trial,kernel,cookie):
    rows=Counter();at=W.address(seed.bundle,'FfRenderBuffer')
    old_kernel=original[1048592+893*1024:1048592+901*1024]
    old_cookie=original[511774:511790]
    climb=next(i for i in range(256) if seed[W.address(seed.bundle,'MTileAttribute')+i]&2)
    for previous in (2225,2226):
        for tile in (0,0x61,0x23,0xc2,0xc3,climb):
            for py in (150,151,152,153):
                for index in (0,255):
                    pair=[]
                    for raw,code,header in ((original,old_kernel,old_cookie),(trial,kernel,cookie)):
                        m=clone(seed);m.bundle=dict(m.bundle,raw=raw);m.ram[3][:]=code
                        m.ram[3][0x1fe0:0x1ff0]=header
                        for i,tag in enumerate(m.rawtags):
                            if tag&128:m.raw_page(i,tag)
                        for a in range(0x300,0x4a0):m[a]=0
                        m[0x37c]=tile
                        N.put(m,Player_X_Position=0xb2,Player_PageLoc=8,Player_Y_Position=py,
                              Player_Y_HighPos=1,Player_Y_Speed=255,Player_State=1,RgCrouch=0)
                        m[at+2],m[at+8],m[at+9]=160,previous&255,previous>>8
                        m[3],m[4]=85,166
                        c=call(m,'FwHostHead',y=index,p=0xf1)
                        assert (m[3],m[4])==(85,166)
                        assert N.get(m,'Player_State')==1 and N.get(m,'Player_Y_Speed')==255
                        assert N.get(m,'Player_X_Position')==0xb2 and N.get(m,'Player_PageLoc')==8
                        pair.append((c,m))
                    c,a=pair[0];d,b=pair[1]
                    attr=seed[W.address(seed.bundle,'MTileAttribute')+tile]
                    filtered=previous==2225 and attr&3==1 and tile not in (0xc2,0xc3)
                    assert (c.x,c.y,c.sp)==(d.x,d.y,d.sp)==(0,index,224)
                    assert (c.p&~0x82)==(d.p&~0x82), ('real head status ABI',previous,tile,py,index,regs(c),regs(d))
                    if filtered:
                        assert d.a==0 and c.a==tile and N.get(b,'Player_Y_Position')==py
                    else:
                        assert (c.a,c.p)==(d.a,d.p)
                        assert N.get(a,'Player_Y_Position')==N.get(b,'Player_Y_Position')
                    rows['actual_FwHostHead_registers_body_state']+=1
    return dict(rows)


def isr(m,c,kind,resume=None):
    global DEEPEST
    entry=regs(c);W.clear_logs(m)
    fixed=bytes(m[0xe000:0x10000])
    hits=[i for i in range(len(fixed)-8) if fixed[i:i+4]==bytes.fromhex('ad390110') and fixed[i+5:i+8]==bytes.fromhex('ee3a01')]
    site,=hits;delta=fixed[site+4];lag=0xe000+site+5
    regular=lag+(delta if delta<128 else delta-256)
    busy=bool(N.get(m,'NmiDisable')&128)
    skipped=N.get(m,'NmiSkipped');seen=Counter()
    if kind == 'IRQ':
        if c.p&4:
            c.irq();assert regs(c)==entry
            return 'masked'
        c.irq()
        assert c.pc==0x8000 and m.rawtags[0]==254
    else:c.nmi()
    for _ in range(100000):
        if regs(c)==entry:
            if kind=='NMI':
                assert seen['lag']==int(busy) and seen['regular']==int(not busy)
                assert N.get(m,'NmiSkipped')==(skipped+int(busy))&255
                if busy:
                    assert not any(a in (0x2007,0x4014) for a,_ in m.writes)
                else:
                    assert any(a==0x4014 for a,_ in m.writes)
                PATHS['lag_FF' if busy else 'normal_NMI']+=1
            else:
                want=[(0x2006,(N.get(m,'IrqPPUCTRL')&1)<<2),(0x2005,32),
                      (0x2005,N.get(m,'IrqNewScroll')),
                      (0x2006,128|(N.get(m,'IrqNewScroll')>>3))]
                assert m.ppu_log==want, ('actual scanline IRQ PPU transaction',m.ppu_log,want)
                PATHS['scanline_IRQ']+=1
            return 'returned'
        seen['lag']+=int(c.pc==lag);seen['regular']+=int(c.pc==regular)
        if kind=='NMI' and busy and not c.p&4 and resume is not None:
            if DEEPEST is None or c.sp<DEEPEST[1].sp:
                q,d=clone(m,c);DEEPEST=(q,d,entry,resume)
        assert m[c.pc], ('ISR BRK',kind,hex(c.pc),m.rawtags)
        c.step()
    raise AssertionError(('ISR return bound',kind,entry,regs(c)))


def irq_checks(original):
    rows=Counter();origins=Counter()
    for origin,stop,state,cpu in SAMPLES:
        origins[origin]+=1
        for kind in ('NMI','IRQ'):
            m,c=clone(state,cpu);n,d=clone(state,cpu)
            n.bundle=dict(n.bundle,raw=original)
            for i,tag in enumerate(n.rawtags):
                if tag&128:n.raw_page(i,tag)
            # The counterfactual has identical live RAM3 and CPU context;
            # only unchanged native ISR code/cartridge data is substituted.
            before=(regs(c),bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),
                    body(m),tuple(bytes(r) for r in m.ram))
            a,b=isr(m,c,kind,stop),isr(n,d,kind,stop)
            assert a==b
            assert (regs(c),bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),
                    body(m),tuple(bytes(r) for r in m.ram))==before, (origin,kind,hex(cpu.pc),'ISR live state')
            assert (app(m),regs(c),m.vram,m.chr_latches,m.upper,m.ppu_addr,m.toggle,m.ppuctrl,m.writes)==(
                    app(n),regs(d),n.vram,n.chr_latches,n.upper,n.ppu_addr,n.toggle,n.ppuctrl,n.writes), (origin,kind,hex(cpu.pc),'paired ISR')
            if a=='masked':
                rows['actual_SEI_masked_IRQ']+=1;continue
            # Full source continuation is compared with the no-interrupt cut.
            ref,r=clone(state,cpu)
            finish(ref,r,stop);finish(m,c,stop)
            assert (regs(c),body(m),tuple(bytes(z) for z in m.ram),tuple(m.rawtags),bytes(m[0x15a:0x17b])) == (
                    regs(r),body(ref),tuple(bytes(z) for z in ref.ram),tuple(ref.rawtags),bytes(ref[0x15a:0x17b])), (origin,kind,hex(cpu.pc),'foreground resume')
            rows[kind+'_real_RTI_and_foreground_resume']+=1
    assert DEEPEST is not None
    state,cpu,outer,resume=DEEPEST
    m,c=clone(state,cpu);n,d=clone(state,cpu)
    n.bundle=dict(n.bundle,raw=original)
    for i,tag in enumerate(n.rawtags):
        if tag&128:n.raw_page(i,tag)
    before=(regs(c),body(m),tuple(bytes(z) for z in m.ram),bytes(m[3:11]),
            bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]))
    assert isr(m,c,'IRQ')==isr(n,d,'IRQ')=='returned'
    assert (regs(c),body(m),tuple(bytes(z) for z in m.ram),bytes(m[3:11]),
            bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]))==before
    assert (app(m),regs(c),m.vram,m.chr_latches,m.writes)==(app(n),regs(d),n.vram,n.chr_latches,n.writes)
    ref,r=clone(state,cpu)
    finish(m,c,(outer[0],outer[5]));finish(ref,r,(outer[0],outer[5]))
    assert regs(c)==regs(r)==outer
    finish(m,c,resume);finish(ref,r,resume)
    assert (regs(c),body(m),tuple(bytes(z) for z in m.ram),tuple(m.rawtags))==(
            regs(r),body(ref),tuple(bytes(z) for z in ref.ram),tuple(ref.rawtags))
    rows['nested_scanline_IRQ_during_real_CLI_lag_NMI']+=1
    assert rows['NMI_real_RTI_and_foreground_resume'] and rows['IRQ_real_RTI_and_foreground_resume']
    return dict(cases=dict(rows),sample_origins=dict(origins),instruction_seams=len(SAMPLES),
                actual_paired_ISR_path_executions=dict(PATHS),nested_parent_SP=cpu.sp,
                paired_native_ISR_state_and_hardware_exact=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--section',choices=('lifecycle','abi','irq','all'),default='all')
    args=p.parse_args()
    assert sha256(Path(Fix.__file__).read_bytes()).hexdigest()==CHECKER_PIN
    assert sha256(Fix.SOURCE.read_bytes()).hexdigest()==SOURCE_PIN
    original=W.ROM.read_bytes();trial,kernel,cookie,program,_,_=Fix.proposal(original)
    assert sha256(trial).hexdigest()==PIN
    old_kernel=original[1048592+893*1024:1048592+901*1024]
    old_cookie=original[511774:511790]
    old,old_receipt,_=cold_menu(original,0,old_cookie,old_kernel)
    new,receipt,last_cpu=cold_menu(trial,0,cookie,kernel)
    sample(new,last_cpu,(last_cpu.pc,last_cpu.sp),'genuine_idle_normal_NMI','normal')
    report=dict(passed=False,source_CPU_only=True,Mesen_run=False,ROM_written=False,outputs_written=0,
                candidate_SHA256=PIN,kernel_SHA256=sha256(kernel).hexdigest(),cookie=cookie.hex(),
                actual_menu_cold=[old_receipt,receipt])
    if args.section in ('lifecycle','all'):
        report['lifetime']=lifecycle(old,new,original,trial,kernel,cookie)
        print(json.dumps(dict(event='lifetime_pass',result=report['lifetime'])),flush=True)
    if args.section in ('abi','irq','all'):
        report['ABI']=abi(new,program)
        report['native_head_callbacks']=head_callbacks(new,original,trial,kernel,cookie)
        print(json.dumps(dict(event='ABI_pass',result=report['ABI'])),flush=True)
    if args.section in ('irq','all'):
        memory=[0]*65536;memory[0xa000:0xc000]=kernel
        dis=Disassembler(N.NesMPU(memory=memory));expected=set(PATCHED_PCS)
        for start,size in ((0xb620,79),(0xbb47,14),(0xb670,9)):
            pc=start
            while pc<start+size:
                expected.add(pc);pc+=dis.instruction_at(pc)[0]
            assert pc==start+size
        reached={cpu.pc for _,_,_,cpu in SAMPLES if cpu.pc in expected}
        assert reached==expected, ('new instruction cuts missing',sorted(expected-reached))
        report['all_changed_instruction_seams']=len(expected)
        report['real_vectors']=irq_checks(original)
    report['passed']=True
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    main()
