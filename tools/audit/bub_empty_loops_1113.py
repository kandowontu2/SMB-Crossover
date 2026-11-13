"""Private source-owned empty-loop equivalence/cost probe; zero files.

No physics or active actor routine changes. This is not native-qualified and
must not be installed. All new instructions use the delivered 528-byte gap.
"""
from hashlib import sha256
import json
from pathlib import Path

import check_bub_current_budget_1113 as B
from check_ff_head_lifetime_irq_1110 import clone


START, END = 0xb32a, 0xb53a
OLD_COOKIE=bytes.fromhex('a72701f3691d419fd9ae7473840ce393')
COOKIE=16+65*8192+0xfea
NEGATIVE='b6393502f17d8ff501d2e3a436d70b5bcf40b98741d24b36a84792debe691d47'
CANDIDATE='a77a71cf9b22837cb58d639b7653f527c7de2376cc1cffb1d1199a9f7081cd38'
word=lambda n:int(n).to_bytes(2,'little')
ins=lambda op,n:bytes((op,))+word(n)


def _build(raw,legacy_entry_hooks=False):
    assert sha256(raw).hexdigest()==B.PIN
    metadata=B.R/'build/bub-upgrades-root-1102-v48/proposal.json'
    assert sha256(metadata.read_bytes()).hexdigest()=='f342a3c646851d3e098f0a45dc4ee77c78596318d687c9abfea48a96c5059818'
    q,_,_=B.bindings(raw);lab=q['labels']
    origin=16+65*8192
    cookie_pc=raw[origin+0xbb1]+256*raw[origin+0xbb9]
    assert COOKIE==origin+cookie_pc-0xa000
    old=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024] for p in B.PAGES)
    assert old[START-0xa000:END-0xa000]==b'\xff'*(END-START)
    image=bytearray(old);cursor=START;blocks=[]
    def add(name,hook,stolen,guard,fast,resume,old_entry=None):
        nonlocal cursor
        assert image[hook-0xa000:hook-0xa000+len(stolen)]==stolen,(name,'hook')
        # All nonempty cases restore incoming A and replay the original
        # instructions before entering the unchanged body at its old PC.
        check=ins(0xad,guard[0])+b''.join(ins(0x0d,a) for a in guard[1:])
        branch=len(fast)+1  # PLA plus complete fast path; local BNE fallback.
        assert branch<128
        fallback=ins(0x4c,old_entry) if old_entry is not None else stolen+ins(0x4c,hook+len(stolen))
        code=b'\x48'+check+bytes((0xd0,branch))+b'\x68'+fast+b'\x68'+fallback
        assert cursor+len(code)<=END
        image[cursor-0xa000:cursor-0xa000+len(code)]=code
        image[hook-0xa000:hook-0xa000+len(stolen)]=ins(stolen[0] if old_entry is not None else 0x4c,cursor)+b'\xea'*(len(stolen)-3)
        blocks.append(dict(name=name,hook=hook,leaf=cursor,bytes=len(code),guard=list(guard),
            original_resume=hook+len(stolen),empty_stop=resume,
            old_entry=old_entry if old_entry is not None else hook,
            new_entry=cursor if old_entry is not None else hook,
            default_stop=0x5b00 if old_entry is not None else hook+len(stolen)))
        cursor+=len(code)
    assoc=tuple(0xc320+i*16 for i in range(6))
    # Original Observe's all-inactive path leaves A0/X6/Y80, C1/Z1/N0,
    # preserves V/D/I, and writes only final metadata C3C0=5/C3C5=80.
    observe=b'\xa9\x05'+ins(0x8d,0xc3c0)+b'\xa9\x50'+ins(0x8d,0xc3c5)+b'\xa8\xa9\x00\xa2\x06\xe0\x06\x60'
    def whole_wrapper(name,entry,guard,fast,call,opcode):
        if legacy_entry_hooks:
            stolen=old[entry-0xa000:entry-0xa000+5]
            assert stolen[:2]==b'\xa2\x00' and stolen[2]==0x20
            add(name,entry,stolen,guard,fast,0x5b00)
        else:
            needle=ins(opcode,entry)
            assert old.count(needle)==1,(name,'unique current caller')
            assert call==old.index(needle)+0xa000,(name,'compiled/source caller binding')
            add(name,call,needle,guard,fast,0x5b00,old_entry=entry)
            assert image[entry-0xa000:entry-0xa000+5]==old[entry-0xa000:entry-0xa000+5]
    whole_wrapper('observe',lab['BbNativeObserve'],assoc,observe,lab['BbNativeShiftCamera'],0x20)
    # Empty native slots clear the same six source actors and last indices;
    # Y survives and the original ADC-based index helper leaves V clear.
    actors=tuple(0xc068+i*4 for i in range(6))
    incoming=b'\xa9\x00'+b''.join(ins(0x8d,a)for a in actors)
    for value,dest in ((5,0xc3c0),(0x7c,0xc3c1),(0x38,0xc3c2)):
        incoming+=bytes((0xa9,value))+ins(0x8d,dest)
    incoming+=b'\xa9\x00\xa2\x06\xb8\xe0\x06\x60'
    b=B.W.Symbols.bundle();b['raw']=raw
    flags=B.W.address(b,'Enemy_Flag')
    # Delivered swept-head clear tail is JMP ProxiesIn, not an obsolete JSR
    # in NativeUpdate. Keep that clear and both original loop entries intact.
    assert old[0x12b5:0x12ba]==bytes.fromhex('a9008defc3')
    whole_wrapper('proxies-in',lab['BbNativeProxiesIn'],tuple(flags+i for i in range(6)),incoming,0xb2ba,0x4c)
    # D887's fifteen empty bubbles with no pending shot only increment X/Y.
    # Its exact exit is A0/XC4/Y0, C1/Z1/N0/V0. Timers and the remainder of
    # the original D8BA..D8FD routine still execute, including all actor work.
    bubbles=tuple(0xc088+i*4 for i in range(15))
    resume=lab['BbOriginal_D8BA']
    empty=b'\xa9\x00\xa2\xc4\xa0\x00\xb8\x38'+ins(0x4c,resume)
    add('original-empty-bubbles',lab['BbBubbleStep'],b'\xa2\x88\xa0\x88',bubbles+(0xc264,),empty,resume)
    assert lab['BbOriginal_D88B']==lab['BbBubbleStep']+4
    # The draw-only scan has no writes when all six proxy and fifteen bubble
    # states are zero. Keep the original player draw and common queue tail.
    at=lab['BbNativeDrawBubbles']
    begin=lab['BbNativeDrawAdvance']-0xa000
    tail=old.index(bytes.fromhex('a9008de106a9e18d066b'),begin)+0xa000
    empty=b'\xa9\x00\xa2\xc4\xa0\x00\xb8\x38'+ins(0x4c,tail)
    add('empty-draw-scan',at,b'\xa2\x68\xa0\x10',actors+bubbles,empty,tail)
    assert lab['BbNativeDrawLoop']==at+4
    art=raw[1048592+441*1024:1048592+442*1024]
    cookie=bytes((167,39,2))+sha256(image+art).digest()[:13]
    out=bytearray(raw)
    assert out[COOKIE:COOKIE+16]==OLD_COOKIE
    for i,p in enumerate(B.PAGES):out[1048592+p*1024:1048592+(p+1)*1024]=image[i*1024:(i+1)*1024]
    out[COOKIE:COOKIE+16]=cookie
    expected=NEGATIVE if legacy_entry_hooks else CANDIDATE
    if expected:assert sha256(out).hexdigest()==expected
    return bytes(out),dict(parent=B.PIN,candidate=sha256(out).hexdigest(),
        code_bytes=cursor-START,capacity=END-START,remaining=END-cursor,blocks=blocks,
        cookie=cookie.hex(),private_probe=True,native_qualified=False,installed=False)


def proposal(raw):return _build(raw)


def negative_proposal(raw):
    """Reproduce the rejected interior-loop-hook image; never native-ready."""
    return _build(raw,True)


def reverse(raw):
    parent=bytearray(raw)
    old=(B.R/'build/bub-initial-tier-1103-v87/private-image.bin').read_bytes()
    assert sha256(old).hexdigest()=='1eecc22950713c0d19cb4fbccdbc517b848e39c5afc4bd1d1a553f44cbc509d0'
    for i,p in enumerate(B.PAGES):parent[1048592+p*1024:1048592+(p+1)*1024]=old[i*1024:(i+1)*1024]
    parent[COOKIE:COOKIE+16]=OLD_COOKIE
    parent=bytes(parent)
    assert sha256(parent).hexdigest()==B.PIN and proposal(parent)[0]==raw
    return parent


inverse=reverse


def direct(m,pc,stop,flags,observe=None):
    m.raw_page(1,3);m.raw_page(2,2)
    B.N.put(m,CurrentBank=3,CurrentBankC=2)
    c=B.N.NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp=83,71,37,flags,224;c.stPushWord(0x5aff)
    for _ in range(20000):
        if c.pc==stop:return c
        if observe:observe(m,c)
        assert m[c.pc],('BRK',hex(c.pc));c.step()
    raise AssertionError(('bounded prefix',hex(pc),hex(c.pc)))


def controller(raw,identity=0, *, costs=False):
    """Strict successor, exact reverse7ef; frozen baseline policy unchanged."""
    import profile_bub_empty_native_1113 as Native
    parent=reverse(raw);rebuilt,info=proposal(parent)
    assert raw==rebuilt and sha256(raw).hexdigest()==CANDIDATE
    text=(Native.cost_controller if costs else Native.controller)(parent,identity)
    assert text.count(B.PIN)==1 and text.count(OLD_COOKIE.hex())==1
    text=text.replace(B.PIN,CANDIDATE).replace(OLD_COOKIE.hex(),info['cookie'])
    image=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024] for p in B.PAGES)
    spans=[(v['hook'],image[v['hook']-0xa000:v['original_resume']-0xa000]) for v in info['blocks']]
    spans.append((START,image[START-0xa000:START-0xa000+info['code_bytes']]))
    checks='\n'
    for at,data in spans:
        checks+=f' local code="{data.hex()}";for k=1,#code,2 do assert(work(3,{at}+(k-1)//2)==tonumber(code:sub(k,k+1),16),"Exact new empty-loop runtime")end\n'
    marker=" game=true;phase='settle'"
    assert text.count(marker)==1
    text=text.replace(marker,checks+marker)
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    assert not any(v in text for v in ('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def source_controller(raw):
    import profile_bub_empty_native_1113 as Native
    candidate,info=proposal(raw)
    rows=[Native.source_check(candidate,i,controller_text=controller(candidate,i),expected=CANDIDATE)for i in range(2)]
    return dict(passed=True,candidate=CANDIDATE,controllers=rows,output_files=0)


def interrupts(raw):
    """New-code/entry cuts, actual IRQ and rendered busy-NMI, in memory."""
    import check_bub_head_interrupts_1102_v57 as I
    candidate,info=proposal(raw)
    counts={'IRQ':0,'busyNMI':0};seen=set();minimum=255;pcs=set()
    hooks={v['hook'] for v in info['blocks']}
    for identity in range(2):
        seed,_=B.cold(candidate,identity)
        seed.controller_pad=0;B.frame(seed)
        def cut(m,c,expected=None,reference=None, *, label='Main'):
            nonlocal minimum
            pc=c.pc
            if pc not in hooks and not START<=pc<START+info['code_bytes']:return
            if m.rawtags[1]!=3:return
            key=(identity,label,pc,c.sp,c.p&4)
            if key in seen:return
            seen.add(key);pcs.add(pc)
            assert B.N.get(m,'NmiDisable')==255,('genuine busy cut',hex(pc))
            for kind in ('IRQ','busyNMI'):
                if kind=='IRQ' and c.p&4:continue
                q,d=clone(m,c)
                regs=(d.pc,d.a,d.x,d.y,d.p&0xef,d.sp)
                state=I.state(q);live=bytes(q[0x101+d.sp:0x200]);maps=q.rawtags[:]
                skipped=B.N.get(q,'NmiSkipped');lag,regular=I.I.path(q)
                d.irq() if kind=='IRQ' else d.nmi()
                lh=rh=0
                for _ in range(200000):
                    minimum=min(minimum,d.sp)
                    if(d.pc,d.sp)==(regs[0],regs[5]):break
                    lh+=d.pc==lag;rh+=d.pc==regular
                    assert q[d.pc],('ISR BRK',kind,hex(d.pc));d.step()
                else:raise AssertionError('new-code ISR bound')
                assert(regs==(d.pc,d.a,d.x,d.y,d.p&0xef,d.sp) and I.state(q)==state
                       and live==bytes(q[0x101+d.sp:0x200]) and q.rawtags==maps),(kind,label,hex(pc),'ISR state')
                assert(lh,rh)==((1,0)if kind=='busyNMI'else(0,0))
                assert B.N.get(q,'NmiSkipped')==(skipped+(kind=='busyNMI'))&255
                if expected is not None:
                    idle=B.W.address(q.bundle,'IdleLoop')
                    for _ in range(500000):
                        if(d.pc,d.sp)==(idle+12,252):break
                        assert q[d.pc],('resume BRK',hex(d.pc));d.step()
                    else:raise AssertionError('resumed Main bound')
                    assert I.state(q)==expected,(kind,label,hex(pc),'resumed Main state')
                    assert (d.a,d.x,d.y,d.p&0xef,d.sp)==reference,(kind,label,hex(pc),'resumed AXYP/SP')
                counts[kind]+=1
        # Actual uninterrupted cold/menu and subsequent ordinary controls.
        # A normal and fresh-B suffix reaches both empty and active bubbles.
        for pad in [0]*2+[64]*16+[0]*4:
            expected=clone(seed);expected.controller_pad=pad;last=[]
            B.frame(expected,lambda _m,c:last.__setitem__(slice(None),[c]))
            r=last[0];ref=(r.a,r.x,r.y,r.p&0xef,r.sp);state=I.state(expected)
            seed.controller_pad=pad
            B.frame(seed,lambda m,c:cut(m,c,state,ref))
            assert I.state(seed)==state
        # Guard-fallback cut fixtures, explicitly not natural enemy/trap claims.
        for block in info['blocks'][:2]:
            m=clone(seed);at=block['guard'][0]
            if at>=0xc000:m.ram[2][at&8191]=1
            else:m[at]=1
            B.N.put(m,NmiDisable=255)
            direct(m,block['new_entry'],block['default_stop'],0x21,
                   lambda m,c:cut(m,c,label='declared guard fallback'))
    assert minimum>=0x7b,('SMC stack floor',minimum)
    from py65.disassembler import Disassembler
    memory=[0]*65536
    image=b''.join(candidate[1048592+p*1024:1048592+(p+1)*1024]for p in B.PAGES)
    memory[0xa000:0xc000]=image
    decoder=Disassembler(B.N.NesMPU(memory=memory));expected_pcs=set(hooks)
    for block in info['blocks']:
        pc=block['leaf'];end=pc+block['bytes']
        while pc<end:
            expected_pcs.add(pc);size,text=decoder.instruction_at(pc)
            assert not text.startswith('???'),(hex(pc),text)
            pc+=size
        assert pc==end
    assert pcs==expected_pcs,dict(missing=sorted(expected_pcs-pcs),extra=sorted(pcs-expected_pcs))
    return dict(passed=True,candidate=CANDIDATE,unique_cut_contexts=len(seen),new_and_hook_PCs=len(pcs),
        interrupts=counts,minimum_ISR_SP=minimum,output_files=0,
        scope='Actual new/hook instruction IRQ and rendered NmiDisableFF cuts; genuine Main resumes exactly. Two guard-fallback prefix fixtures are declared. Cold faults/fullstage/native qualification remain separate.')


def minimal(raw):
    irqs=interrupts(raw)
    donor=donor_check(raw)
    controls=source_controller(raw)
    candidate,info=proposal(raw)
    return dict(passed=True,candidate=CANDIDATE,inverse_exact=reverse(candidate)==raw,
        resource=info,ISR=irqs,donor=donor,source_controls=controls,output_files=0,
        native_qualified=False,installed=False)


def same(a,z,c,d):
    assert (c.a,c.x,c.y,c.p&0xef,c.sp)==(d.a,d.x,d.y,d.p&0xef,d.sp),('registers',hex(c.pc),hex(d.pc),c.a,d.a,c.x,d.x,c.y,d.y,c.p,d.p)
    assert bytes(a.ram[2][:0x1fe0])==bytes(z.ram[2][:0x1fe0]),'source data/helper'
    assert a.rawtags==z.rawtags
    assert bytes(a[0x15a:0x17b])==bytes(z[0x15a:0x17b]),'SMC'
    assert bytes(a[:0x100])==bytes(z[:0x100]) and bytes(a[0x200:0x8000])==bytes(z[0x200:0x8000]),'native RAM'
    assert bytes(a[0x100+c.sp+1:0x200])==bytes(z[0x100+d.sp+1:0x200]),'live stack'


def donor_check(raw):
    """Independent bank7 D887..D8BA inactive-prefix oracle, all flags."""
    donor=Path('C:/NES/Bubble Bobble (USA).nes').read_bytes()
    assert sha256(donor).hexdigest()=='e34901acf6917495890ef79ddb33e4641ea309a803d777a27a198e8802c9b4a0'
    candidate,info=proposal(raw)
    assert reverse(candidate)==raw
    seed,_=B.cold(candidate,0)
    seed.controller_pad=0;B.frame(seed)
    block=next(v for v in info['blocks'] if v['name']=='original-empty-bubbles')
    for flags in range(256):
        m=clone(seed)
        c=direct(m,block['hook'],block['empty_stop'],flags)
        memory=[0]*65536
        memory[0xc000:]=donor[16+7*16384:16+8*16384]
        memory[:256]=seed.ram[2][:256]
        memory[0x200:0x300]=seed.ram[2][0x100:0x200]
        memory[0x400:0x500]=seed.ram[2][0x200:0x300]
        d=B.N.NesMPU(memory=memory,pc=0xd887)
        d.a,d.x,d.y,d.p,d.sp=83,71,37,flags,224;d.stPushWord(0x5aff)
        for _ in range(10000):
            if d.pc==0xd8ba:break
            assert memory[d.pc];d.step()
        else:raise AssertionError('donor inactive-prefix bound')
        assert (c.a,c.x,c.y,c.p&0xef,c.sp)==(d.a,d.x,d.y,d.p&0xef,d.sp)
        assert memory[:256]==list(m.ram[2][:256])
        assert memory[0x200:0x300]==list(m.ram[2][0x100:0x200])
        assert memory[0x400:0x500]==list(m.ram[2][0x200:0x300])
    return dict(passed=True,candidate=info['candidate'],original_cartridge_flags=256,
                source='actual donor bank7 D887 through D8BA, RAM rebound by the existing port map',output_files=0)


def check(raw):
    candidate,info=proposal(raw)
    assert reverse(candidate)==raw
    cases=0;mixed=0;savings={}
    for identity in range(2):
        seeds=[B.cold(image,identity)[0]for image in (raw,candidate)]
        for m in seeds:m.controller_pad=0;B.frame(m)
        for block in info['blocks']:
            values=[]
            for flags in range(256):
                a,z=map(clone,seeds)
                assert all(a[at]==z[at]==0 for at in block['guard']),(block,'cold guard')
                c=direct(a,block['old_entry'],block['empty_stop'],flags)
                d=direct(z,block['new_entry'],block['empty_stop'],flags)
                same(a,z,c,d);values.append(c.processorCycles-d.processorCycles);cases+=1
            savings[f'{identity}:{block["name"]}']=[min(values),max(values)]
            # Declared one-byte guard rejection fixtures: only the original
            # stolen prefix executes, stopping before the remaining body.
            for at in block['guard']:
                for value in (1,128,255):
                    a,z=map(clone,seeds)
                    for m in (a,z):
                        if at>=0xc000:m.ram[2][at&8191]=value
                        else:m[at]=value
                    c=direct(a,block['old_entry'],block['default_stop'],0xf1)
                    try:d=direct(z,block['new_entry'],block['default_stop'],0xf1)
                    except AssertionError as error:raise AssertionError((block['name'],hex(at),value,error)) from error
                    same(a,z,c,d);cases+=1
            if block['name'] in ('observe','proxies-in'):
                for mask in range(64):
                    a,z=map(clone,seeds)
                    for m in (a,z):
                        for slot in range(6):
                            active=bool(mask&(1<<slot))
                            for field,value in (('Enemy_Flag',((128|slot) if block['name']=='observe' else 1) if active else 0),
                                ('Enemy_ID',6),('Enemy_State',0),('Enemy_Y_HighPos',1),
                                ('Enemy_X_Position',64+slot*20),('Enemy_PageLoc',0),('Enemy_Y_Position',176)):
                                m[B.W.address(m.bundle,field)+slot]=value
                            if block['name']=='observe':
                                m.ram[2][0x320+slot*16]=int(active)
                                m.ram[2][0x321+slot*16]=6
                    c=direct(a,block['old_entry'],0x5b00,0xf1)
                    d=direct(z,block['new_entry'],0x5b00,0xf1)
                    same(a,z,c,d);cases+=1;mixed+=1
        # Actual ordinary Main/NMI, including real B-generated source bubbles.
        total=[]
        for pad in [0]*12+[1]*20+[64]*16+[0]*8+[129]*16+[0]*16:
            outputs=[]
            for m in seeds:
                m.controller_pad=pad;outputs.append(B.frame(m))
            a,z=seeds
            assert bytes(a.ram[2][:0x1fe0])==bytes(z.ram[2][:0x1fe0]),('Main source',identity,pad)
            assert bytes(a[:0x100])==bytes(z[:0x100]) and bytes(a[0x200:0x8000])==bytes(z[0x200:0x8000]),('Main native',identity,pad)
            assert a.rawtags==z.rawtags and bytes(a[0x15a:0x17b])==bytes(z[0x15a:0x17b])
            total.append(outputs[0]-outputs[1])
        savings[f'{identity}:Main']=[min(total),max(total),sum(total)/len(total)]
    return dict(passed=True,**info,prefix_cases=cases,complete_mixed_slot_cases=mixed,savings=savings,
        source_CPU_only=True,output_files=0,ROM_written=False,
        scope='Full-empty-prefix/all-flags fixtures; complete multi-iteration Observe/ProxiesIn for every mixed six-slot mask and one-byte guard rejections; bubble/draw nonempty prefixes and88 paired ordinary Main/NMI per identity. No cold faults/native cadence/fullstage claim.')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();m=p.add_mutually_exclusive_group()
    m.add_argument('--donor-only',action='store_true');m.add_argument('--interrupts',action='store_true')
    m.add_argument('--controller',action='store_true');a=p.parse_args()
    method=donor_check if a.donor_only else interrupts if a.interrupts else source_controller if a.controller else check
    print(json.dumps(method(B.ROM.read_bytes()),sort_keys=True),flush=True)
