"""Current public Sonic admission and safe native rejection; RAM/stdout only."""
from hashlib import sha256
from collections import Counter
import argparse
import json
import sys

import check_sonic_native_effects_aligned_1110 as A
import check_sonic_shared_audio_1110 as Audio
import check_sonic_shared_feet_1110 as Feet

W,N,L=Feet.W,Feet.N,Feet.L
sys.path.insert(0,str(W.R/'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as Asm

SOURCE=W.R/'tools/reference/sonic_public_admission_1110.s'
off=Feet.off
LAYOUT={'SELECTOR':(65,0xa743,130),'SH_AUTH':(65,0xa800,23),
        'REJECT':(65,0xab4f,9),'NATIVE_REJECT':(9,0xbc54,86)}


def proposal(raw):
    original=W.ROM.read_bytes();assert sha256(original).hexdigest()==W.PIN
    # The current selector's four explicit source NOPs precede the fixed DK
    # cookie. Mini's five-byte A7D5 fast-check and all cookie/data stay exact.
    assert raw[off(65,0xa743):off(65,0xa7c5)]==original[off(65,0xa743):off(65,0xa7c5)]
    old=bytearray(original[off(65,0xa800):off(65,0xa817)])
    assert old[13:15]==bytes((0xa2,6));old[14]=7
    assert raw[off(65,0xa800):off(65,0xa817)]==old
    assert raw[off(65,0xab4f):off(65,0xab58)]==bytes.fromhex('babd0a0129fe9d0a01')
    assert raw[off(65,0xb01b):off(65,0xb01f)]==bytes.fromhex('c9069043')
    # Complete retired demo source/caller closure was originally funded here;
    # Sonic uses only its separate fixed18B cookie. This native86B still exact.
    baseline=W.Symbols.bundle();baseline['raw']=original
    _,retired=A.E.S.Funding.retired_demo(baseline)
    assert retired['switchable']==dict(bank=9,start=0xbc54,end=0xbcaa,bytes=86)
    assert raw[off(9,0xbc54):off(9,0xbcaa)]==original[off(9,0xbc54):off(9,0xbcaa)]
    # Sole real same-bank auth consumers: the common saved frame and Sh's
    # independently saved AXYP/SMC frame. No published FarCall targets A800.
    bank=raw[off(65,0xa000):off(65,0xa000)+8192]
    refs=[0xa000+i for i in range(8190)if bank[i:i+3]==bytes.fromhex('2000a8')]
    assert refs==[0xa7a7,0xa8dd,0xabdb,0xac8d],refs
    assert bytes.fromhex('a9008d6c01a9a88d6d01a9c1')not in raw[16:1048592]
    p=Asm.assemble(SOURCE.read_text(),{name:(pc,size)for name,(_,pc,size)in LAYOUT.items()})
    assert p['symbols']['PrOdd']==0xa75a
    assert p['symbols']['RejectCall']==0xa7bf and p['symbols']['RejectHigh']==0xa80e
    assert len(p['images']['SELECTOR'])==130 and len(p['images']['SH_AUTH'])==23
    image=bytearray(raw);patches=[]
    for name,(bank,pc,size)in LAYOUT.items():
        data=p['images'][name];assert len(data)<=size
        data=data.ljust(size,b'\xea')
        at=off(bank,pc);image[at:at+size]=data
        patches.append(dict(section=name,bank=bank,pc=pc,bytes=size,used=len(p['images'][name])))
    image[off(65,0xb01b)+1]=7
    assert image[off(65,0xa7c5):off(65,0xa800)]==raw[off(65,0xa7c5):off(65,0xa800)]
    return bytes(image),dict(parent_SHA256=sha256(raw).hexdigest(),image_SHA256=sha256(image).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),patches=patches,
        source_funding='Duplicate saved Sh-auth frames/selected guard plus exact4 selector NOPs and source-retired demo86B',
        auth_imports=refs,raw_range=[37,43],Sonic_table=0xd100,private_headers_both16_unchanged=True)


def combined():
    raw,program,p=A.proposal();raw,_=Audio.proposal(raw);raw,_=Feet.proposal(raw)
    image,record=proposal(raw)
    return image,program,p,record


def public(m,row,y=0,flags=0x31,observe=None,a=85,x=71):
    pc=0xb08c+3*row;m[0x16a]=a;m[0x16c]=pc&255;m[0x16d]=pc>>8
    c=N.NesMPU(memory=m,pc=0x15a);c.a,c.x,c.y,c.p,c.sp=193,x,y,flags,224;c.stPushWord(0x5aff)
    W.clear_logs(m);L.finish(m,c,(0x5b00,224),observe);return c


def getters(image,program,p):
    T=A.T;S=T.S
    seed=T.install(A.C.Current.W.bundle(image),p,program);S.scene(seed)
    T.invoke(seed,p['service']['symbols']['SonicHostFresh'],watch=False)
    T.invoke(seed,p['service']['symbols']['SonicServices'],watch=False)
    S.set_native(seed,DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=255)
    counts=Counter();samples={}
    for kind,row,dy in(('head',10,4),('side',14,8),('feet',35,32)):
        for grounded in(False,True):
            for tile in(0,0x54,0x10,0x11,0x23,0xc2,0xc3,0x24,0x25,0x6c,0x1f):
                a=T.clone(seed,p);a[0xc030]=128 if grounded else 0;S.set_native(a,PlayerSize=0)
                a[T.pointer(40,176+dy)]=tile;b=T.clone(a,p)
                y=3 if kind=='side'else 0
                direct,_=T.invoke(a,p['service']['symbols']['SonicServices']+3*row,y=y,watch=False)
                def observe(mem,cpu):
                    if cpu.pc>=0x8000:
                        tag=mem.rawtags[(cpu.pc-0x8000)//8192]
                        own=(tag==193 and(0xa743<=cpu.pc<0xa7c5 or 0xa800<=cpu.pc<0xa817 or 0xab4f<=cpu.pc<0xab58))or(tag==137 and 0xbc54<=cpu.pc<0xbc77)
                        if own and(kind,cpu.pc)not in samples:samples[kind,cpu.pc]=L.clone(mem,cpu)
                actual=public(b,row,y,observe=observe)
                assert(direct.a,direct.x,direct.y,direct.p&0xef)==(actual.a,actual.x,actual.y,actual.p&0xef),(kind,grounded,hex(tile),L.regs(direct),L.regs(actual))
                assert bytes(a[3:11])==bytes(b[3:11]) and L.body(a)==L.body(b),(kind,'native outputs')
                assert a.ram==b.ram and a.rawtags==b.rawtags,(kind,'full private/map')
                counts[kind+'_public_vs_frozen_private']+=1
    faults=Counter()
    for bank in(2,3):
        for at in range(16):
            for bit in range(8):
                for row,y in((10,0),(14,3),(35,0),(35,1)):
                    m=T.clone(seed,p);m.ram[bank][0x1fe0+at]^=1<<bit
                    before=L.body(m),tuple(bytes(q)for q in m.ram);entered=[]
                    def observe(mem,cpu):
                        if 0xd000<=cpu.pc<0xd300 and mem.rawtags[2]==2:entered.append(cpu.pc)
                        if cpu.pc>=0x8000:
                            tag=mem.rawtags[(cpu.pc-0x8000)//8192]
                            own=(tag==193 and(0xa743<=cpu.pc<0xa7c5 or 0xa800<=cpu.pc<0xa817 or 0xab4f<=cpu.pc<0xab58))or(tag==137 and 0xbc54<=cpu.pc<0xbc77)
                            key=('fault'+str(row),cpu.pc)
                            if own and key not in samples:samples[key]=L.clone(mem,cpu)
                    c=public(m,row,y,observe=observe)
                    assert(c.a,c.x,c.y,c.p&0x83)==(0,0,y+int(row==35),2),(bank,at,bit,row,L.regs(c))
                    assert not entered and before==(L.body(m),tuple(bytes(q)for q in m.ram)),(bank,at,bit,row,'bad-header private execution/state')
                    faults['all32_header_bytes_all8_bits_each_native_getter']+=1
    for flags in range(256):
        for row,y in((10,0),(14,3),(35,0),(35,1)):
            m=T.clone(seed,p);m.ram[2][0x1fe0]^=1
            c=public(m,row,y,flags)
            assert(c.a,c.x,c.y,c.p&0xcf)==(0,0,y+int(row==35),(flags&0x4c)|2),(flags,row,L.regs(c))
            faults['all256_saved_P_safe_native_rejections']+=1
    # Existing source fixture includes the actual native PlayerHeadCollision
    # and verifies that its authored block is hit only on the cached contact.
    head=T.bounds_and_head_contact(seed,p)
    head.update(global_native_getters(seed,p))
    return dict(cases=dict(counts),faults=dict(faults),actual_native_head=head,
        ready_seed=seed,samples=samples)


def counterfactual(image):
    original=W.ROM.read_bytes();raw=bytearray(image)
    for name,(bank,pc,size)in LAYOUT.items():
        data=bytearray(original[off(bank,pc):off(bank,pc)+size])
        if name=='SH_AUTH':data[14]=7
        raw[off(bank,pc):off(bank,pc)+size]=data
    raw[off(65,0xb01b)+1]=6
    return bytes(raw)


def legacy(image,program):
    old=counterfactual(image);bundles=[A.C.Current.W.bundle(q)for q in(old,image)];counts=Counter()
    for owner in range(37,43):
        seeds=[]
        for bundle in bundles:
            m=A.O.blank(bundle);A.C.cold(m,owner,program['new']);seeds.append(m)
        assert seeds[0].ram==seeds[1].ram and A.O.headers(seeds[0])==A.O.headers(seeds[1])
        counts['old_owner_cold_pairs']+=1
        for row in range(37):
            assert old[off(65,0xb08c+3*row)]==0x4c
            for flags in(0x31,0xf9):
                pair=[]
                for seed in seeds:
                    m=L.clone(seed);c=public(m,row,3 if row==14 else 0,flags,a=0,x=0)
                    pair.append((L.regs(c),L.app(m)))
                assert pair[0]==pair[1],(owner,row,hex(flags),'old owner typed callback')
                counts['old_owner_all37_published_callback_pairs']+=1
        for bank in(2,3):
            for byte in range(16):
                for row in(0,10,14,35):
                    pair=[]
                    for seed in seeds:
                        m=L.clone(seed);m.ram[bank][0x1fe0+byte]^=1
                        c=public(m,row,109,0xf9,a=83,x=71);pair.append((L.regs(c),L.app(m)))
                    assert pair[0]==pair[1],(owner,bank,byte,row,'old owner full header rejection')
                    counts['old_owner_all32_header_reject_pairs']+=1
    return dict(cases=dict(counts),all_six_old_owners=[37,38,39,40,41,42],
        Getsu42_original_fail_policy_exact=True,
        scope='Directed typed callbacks after each actual common cold worker, valid player/actor0 inputs. No natural route/powerup claim.')


def native(m,pc,a=83,x=71,y=109,flags=0xf9,bank=193):
    m[0x16a]=a;m[0x16c]=pc&255;m[0x16d]=pc>>8
    c=N.NesMPU(memory=m,pc=0x15a);c.a,c.x,c.y,c.p,c.sp=bank,x,y,flags,224;c.stPushWord(0x5aff)
    W.clear_logs(m);L.finish(m,c,(0x5b00,224));return c


def global_native_getters(seed,p):
    T=A.T;S=T.S;counts=Counter();headpc=W.address(W.Symbols.bundle(),'CrossoverHeadProbe')
    for pc,bank,row,y,dy in((headpc,255,10,0,4),(0x90e4,254,14,3,8),(0xe46a,255,35,0,32)):
        m=T.clone(seed,p);m[0xc030]=128;m[T.pointer(40,176+dy)]=0x24
        ref=T.clone(m,p);wanted=public(ref,row,y,flags=0x31,a=0,x=0)
        c=native(m,pc,a=0,x=0,y=y,flags=0x31,bank=bank)
        assert(c.a,c.x,c.y,c.p&0x83)==(wanted.a,wanted.x,wanted.y,wanted.p&0x83),(hex(pc),L.regs(c),L.regs(wanted))
        counts['full_native_head_side_feet_to_public_getter']+=1
        for broken in(2,3):
            m=T.clone(seed,p);m.ram[broken][0x1fe0+15]^=128
            c=native(m,pc,a=0,x=0,y=y,flags=0x31,bank=bank)
            assert(c.a,c.x,c.y,c.p&0x83)==(0,0,y+int(row==35),2),(broken,hex(pc),L.regs(c))
            counts['bad_header_full_native_getter_nonblocking']+=1
    # Cached real source ceiling, queried through the actual fixed head
    # dispatcher before the native head-effect caller receives the result.
    m=T.clone(seed,p);S.scene(m,64,176);T.invoke(m,p['service']['symbols']['SonicHostFresh'],watch=False)
    T.invoke(m,p['service']['symbols']['SonicServices'],watch=False)
    S.set_native(m,FrameCounter=1,SavedJoypadBits=0);T.invoke(m,p['service']['symbols']['SonicServices'],watch=False)
    m[T.pointer(76,160)]=0x61;S.set_native(m,FrameCounter=2,SavedJoypadBits=129)
    T.invoke(m,p['service']['symbols']['SonicServices'],watch=False)
    assert m[p['context']['HeadPending']]==1
    before=S.private(m),S.native(m,'Player_Y_Position')
    c=native(m,headpc,a=0,x=0,y=0,flags=0x31,bank=255)
    assert(c.a,c.x,c.y)==(0x61,0,0)and m[p['context']['HeadPending']]==0
    N.invoke(m,'PlayerHeadCollision',a=c.a,x=c.x,y=c.y,p=c.p)
    assert before==(S.private(m),S.native(m,'Player_Y_Position'))
    counts['cached_source_ceiling_via_fixed_head_then_native_head_effect']+=1
    return dict(counts)


def shinobi(image):
    old=counterfactual(image);bundles=[];seeds=[];counts=Counter()
    for raw in(old,image):
        b=W.Symbols.bundle();b['raw']=raw;bundles.append(b)
    row=next(r for r in Feet.Parent.C.Starts.C.inventory(image)['rows']if r['raw']==36)
    for b in bundles:
        _,m=Feet.Parent.C.cold(b,row);seeds.append(m)
    assert L.app(seeds[0])==L.app(seeds[1]),'Actual Shinobi menu/cold/60-update stage'
    counts['genuine_Shinobi_menu_cold_and60_update_pair']+=1
    bank=old[off(65,0xa000):off(65,0xa000)+8192]
    candidates=[0xa000+i for i in range(0x849,0x8dd)if bank[i:i+6]==bytes.fromhex('08488a489848')]
    assert candidates==[0xa87f];load=candidates[0]
    assert bank[0xa97]==0x4c;injury=int.from_bytes(bank[0xa98:0xa9a],'little');assert injury==0xac79
    # All four actual callers save the outer AXYP before their auth call.
    assert old[off(65,0xaaf7):off(65,0xaaf7)+6]==bytes.fromhex('08488a489848')
    for pc in(load,injury,0xabd5):assert old[off(65,pc):off(65,pc)+6]==bytes.fromhex('08488a489848')
    assert bytes.fromhex('4c00a8')not in old[off(65,0xa000):off(65,0xa000)+8192]
    for target,name in((load,'warm_loader'),(0xabd5,'CHR_publication'),(injury,'native_injury')):
        for flags in(0x20,0x21,0xf9,0xe5):
            for saved in(0,2,3,255):
                pair=[]
                for seed in seeds:
                    m=L.clone(seed);m.raw_page(2,saved);N.put(m,CurrentBankC=saved)
                    if target==load:N.put(m,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
                    c=native(m,target,flags=flags);pair.append((L.regs(c),L.app(m),m.vram,m.chr_latches,m.ppu_log))
                assert pair[0]==pair[1],(name,flags,saved,'Sh outer caller exact')
                counts[name+'_saved_flags_and_C_mapping_pairs']+=1
    # Explicit original-health-zero fixture exercises the genuine death
    # initializer in addition to the real cold-health injury case above.
    pair=[]
    for seed in seeds:
        m=L.clone(seed);m.ram[2][0x539]=0
        c=native(m,injury);pair.append((L.regs(c),L.app(m)))
    assert pair[0]==pair[1];counts['directed_original_zero_health_death_pair']+=1
    for bank in(2,3):
        for byte in range(16):
            for target,name in((0xabd5,'CHR_reject'),(injury,'injury_reject')):
                pair=[]
                for seed in seeds:
                    m=L.clone(seed);m.ram[bank][0x1fe0+byte]^=1
                    c=native(m,target);pair.append((L.regs(c),L.app(m)))
                assert pair[0]==pair[1],(bank,byte,name)
                counts['all32_Shinobi_header_reject_pairs']+=1
    # One reached thin-auth cut under each actual importing frame; compare
    # the original native ISR on an identical live stack, then resume new code.
    native_vectors=Counter()
    for target in(load,0xabd5,injury):
        m=L.clone(seeds[1]);N.put(m,NmiDisable=255)
        if target==load:N.put(m,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0)
        m[0x16a]=83;m[0x16c]=target&255;m[0x16d]=target>>8
        c=N.NesMPU(memory=m,pc=0x15a);c.a,c.x,c.y,c.p,c.sp=193,71,109,0x31,224;c.stPushWord(0x5aff)
        for _ in range(500000):
            if c.pc==0xa809 and m.rawtags[1]==193:break
            assert c.pc!=0x5b00 and m[c.pc],('Thin Sh auth sampler passed return',hex(target),hex(c.pc))
            c.step()
        else:raise AssertionError(('Thin Sh auth cut not reached',hex(target)))
        for kind in('NMI','IRQ'):
            a,ca=L.clone(m,c);b,cb=L.clone(m,c);b.bundle=dict(b.bundle,raw=old)
            for page,tag in enumerate(b.rawtags):
                if tag&128:b.raw_page(page,tag)
            before=L.regs(ca),bytes(a[3:11]),bytes(a[0x15a:0x17b]),bytes(a[0x101+ca.sp:0x200])
            left=L.isr(a,ca,kind);right=L.isr(b,cb,kind)
            assert left==right and before==(L.regs(ca),bytes(a[3:11]),bytes(a[0x15a:0x17b]),bytes(a[0x101+ca.sp:0x200]))
            snap=lambda q,z:(L.regs(z),L.app(q),q.vram,q.chr_latches,q.ppu_log,q.writes)
            assert snap(a,ca)==snap(b,cb)
            b.bundle=dict(b.bundle,raw=image)
            for page,tag in enumerate(b.rawtags):
                if tag&128:b.raw_page(page,tag)
            L.finish(a,ca,(0x5b00,224));L.finish(b,cb,(0x5b00,224))
            assert(L.regs(ca),L.app(a))==(L.regs(cb),L.app(b))
            native_vectors[kind+'_'+left]+=1
    return dict(cases=dict(counts),auth_actual_callers=[0xa7a7,0xa8dd,0xabdb,0xac8d],
        actual_importing_frame_ISR_pairs=dict(native_vectors),
        scope='Actual menu/cold stage plus directed original CHR/loader/injury/death callers; private auth helper itself becomes C-only, while every actual caller preserves its outer contract.')


def lifecycle(image,program,p):
    T=A.T;S=T.S;seed=T.install(A.C.Current.W.bundle(image),p,program);counts=Counter();cold_reads=[]
    m=T.clone(seed,p);warm=A.C.cold(m,43,program['new']);assert warm['PPU_reads']==0
    counts['full_cookie_warm0_PPU']+=1
    for bank in(2,3):
        m=T.clone(seed,p);m.ram[bank][0x1fe0+15]^=128
        before=m.ppu_reads
        # Actual native-scene wrapper, at the legal forced-blank boundary.
        A.O.scene(m,43);c=native(m,0xb013,a=0,x=0,y=0,flags=0x31)
        assert A.O.headers(m)==(p['packet']['cookie'],)*2 and m.ppu_reads>before
        A.E.owned(m,p['packet']);assert not m[p['service']['fields']['Ready']]
        cold_reads.append(m.ppu_reads-before);S.scene(m,48,176)
        public(m,0,a=0,x=0);assert m[p['service']['fields']['Ready']]==1 and m[0xc092]==1
        assert not m[T.B.Host.Payload.Frame.STATUS]
        counts['actual_native_scene_reload_then_public_original_frame']+=1
    # Strict unsigned bounds: no accidental owner44+ or underflow admission.
    for owner in range(256):
        for pc,owned,foreign in((0xa74a,0xa75a,0xa754),(0xb015,0xb062,0xb01f)):
            m=T.clone(seed,p);m.raw_page(1,193);N.put(m,CurrentBank=193,SelectedCharacter=owner)
            c=N.NesMPU(memory=m,pc=pc);c.p=0x31
            for _ in range(10):
                if c.pc in(owned,foreign):break
                c.step()
            assert(c.pc==owned)==(37<=owner<=43),(owner,hex(pc),hex(c.pc))
            counts['public_and_scene_all256_strict_owner_bounds']+=1
    # Existing forced-blank contextual guards must still reject without
    # changing any private bytes or issuing a PPU read.
    for fields in(dict(SelectedCharacter=44),dict(OperMode=0),dict(FamilyMainCommit=0),
                  dict(DisableScreenFlag=0),dict(Mirror_PPUMASK=24),dict(NmiDisable=0)):
        m=A.O.blank(A.C.Current.W.bundle(image));A.O.scene(m,43);N.put(m,**fields)
        before=tuple(bytes(q)for q in m.ram),m.ppu_reads
        c=native(m,0xae00)
        assert not c.p&1 and before==(tuple(bytes(q)for q in m.ram),m.ppu_reads),fields
        counts['existing_cold_context_guards']+=1
    S.scene(m:=T.clone(seed,p));public(m,0,a=0,x=0)
    before=S.private(m);tick=m[0xc092]
    S.set_native(m,GamePauseStatus=1,FrameCounter=1);public(m,0,a=0,x=0)
    assert m[0xc092]==tick and S.private(m)==before
    S.set_native(m,GamePauseStatus=0,FrameCounter=2);public(m,0,a=0,x=0)
    assert m[0xc092]==(tick+1)&255
    counts['public_Main_pause_and_resume']+=1
    return dict(cases=dict(counts),reload_PPU_reads=cold_reads,
        scope='Directed forced-blank native scene/reload and public Main fixture; genuine title/menu ordinaryMain campaign is independently controller-qualified.')


def vectors(image,program,p):
    q=getters(image,program,p);samples=q.pop('samples');q.pop('ready_seed')
    L.SAMPLES.clear();L.SAMPLE_KEYS.clear();L.PATHS.clear();L.DEEPEST=None
    for key,(m,c)in samples.items():L.SAMPLES.append((str(key),(0x5b00,224),m,c))
    result=L.irq_checks(counterfactual(image))
    return dict(getter_header_basis=q,actual_public_instruction_vectors=result)


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--section',choices=('build','getters','legacy','shinobi','lifecycle','vectors','all'),default='build');args=cli.parse_args()
    image,program,p,record=combined()
    tests=None
    if args.section=='getters':
        tests=getters(image,program,p);tests.pop('ready_seed');tests.pop('samples')
    if args.section=='legacy':tests=legacy(image,program)
    if args.section=='shinobi':tests=shinobi(image)
    if args.section=='lifecycle':tests=lifecycle(image,program,p)
    if args.section=='vectors':tests=vectors(image,program,p)
    if args.section=='all':
        tests={}
        for name,check in(('legacy',lambda:legacy(image,program)),('Shinobi',lambda:shinobi(image)),
                           ('lifecycle',lambda:lifecycle(image,program,p)),('vectors',lambda:vectors(image,program,p))):
            tests[name]=check();print(json.dumps(dict(event=name+'_PASS')),flush=True)
        tests['vectors']['actual_public_instruction_vectors'].pop('sample_origins')
    print(json.dumps(dict(passed=True,source_only=True,ROM_written=False,output_files=0,record=record,
        qualification=tests,scope='Explicit directed source CPU qualifications only. Actual controller ordinaryMain is separately pinned; no ROM, Mesen or broad roster completion claim.')),flush=True)


if __name__=='__main__':main()
