"""Offline, explicitly preloaded FF RAM3 ABI controls. No loader or game edit."""
from pathlib import Path
import copy, hashlib, itertools, json, sys, traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU
from arthur_cache_host_controls_v1 import OverlayMemory

P = R/'build/final-fantasy-current-component-v2/linked'
K = R/'build/final-fantasy-ram3-kernel-v1'
O = R/'build/final-fantasy-execution-audit-v1'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(bytes(v)).hexdigest()


def put(m, **values):
    for n, v in values.items(): m[address(m.bundle, n)] = v


def get(m, n): return m[address(m.bundle, n)]


def make(b, raw=False, old_a=0xd7, old_c=0xd8):
    m = OverlayMemory(b)
    m.ram[3][:] = (K/'ram3.bin').read_bytes()  # Explicit fixture preload only.
    # Distinct non-owner RAM banks make accidental aliases visible.
    for i in range(3): m.ram[i][:] = bytes(((j*13+i*37+5)&255) for j in range(8192))
    for i in range(0x6000, 0x8000): list.__setitem__(m, i, (i*13+7)&255)
    for slot, value in [(1, old_a), (2, old_c)]: m.raw_page(slot, value)
    put(m, CurrentBank=old_a, CurrentBankC=old_c, SelectedCharacter=22,
        NumberofLives=2, AreaType=1, AreaAddrsLOffset=0, WorldNumber=0,
        Player_Y_Position=160, Player_Y_HighPos=1, Player_X_Position=120,
        Player_PageLoc=0, PlayerFacingDir=1, PlayerOutlinesOff=1,
        GameEngineSubroutine=8, OperMode=1, DisableScreenFlag=1,
        Mirror_PPUMASK=0, Mirror_PPUCTRL=0xa0, NmiDisable=255,
        VRAM_Buffer_AddrCtrl=0, VRAM_Buffer1_Offset=0, VRAM_Buffer2_Offset=0,
        GuestAudioCharacter=0, FfReady=0, FfVariant=0)
    m.ppuctrl = 0xa0
    m.writes.clear(); m.ram_writes.clear()
    return m


def start(m, name, raw=False, a=0, x=0, y=0, p=0x30, sp=224):
    b=m.bundle
    # Genuine caller setup, genuine executable 33-byte FarCallCommon block.
    m[address(b,'SafecallA_SMC')+1] = a
    pc=address(b,name)
    m[address(b,'FarcallJmpTarget_SMC')+1] = pc&255
    m[address(b,'FarcallJmpTarget_SMC')+2] = pc>>8
    c=NesMPU(memory=m,pc=address(b,'FarCallCommon'))
    c.a=3 if raw else 0xbe; c.x=x; c.y=y; c.p=p; c.sp=sp
    c.stPushWord(0x5aff)
    return c


def run(m, name, raw=False, hook=None, **kwargs):
    old=m.rawtags[:]; c=start(m,name,raw,**kwargs)
    live=bytes(m[0x101+kwargs.get('sp',224):0x200]); low=c.sp; trace=[]
    for step in range(50000):
        if c.pc==0x5b00: break
        if hook: hook(m,c,step)
        tag=m.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        trace.append((c.pc,tag)); low=min(low,c.sp)
        assert m[c.pc]!=0,('actual BRK',name,hex(c.pc),m.rawtags)
        c.step()
    else: raise AssertionError(('bounded source timeout',name,hex(c.pc),m.rawtags))
    assert c.sp==kwargs.get('sp',224)
    assert bytes(m[0x101+c.sp:0x200])==live,('live caller page1',name)
    assert m.rawtags[1]==old[1] and get(m,'CurrentBank')==old[1]
    assert m.rawtags[2]==get(m,'CurrentBankC')
    assert m.rawtags[0]==old[0] and m.rawtags[3]==old[3]
    return c,trace,low


def app(m):
    exclude=set(range(0x100,0x200))|set(range(0x5114,0x5118))
    return bytes(m[i] for i in range(0x8000) if i not in exclude)


def ordered(m):
    return [(a,v) for a,v in m.writes if not 0x100<=a<0x200 and not 0x5114<=a<=0x5117]


def paired(b):
    """Whole same-PC source routes; scratch outputs are compared, not restored."""
    rows=[]
    for variant,face,wet,keys,p in itertools.product(range(4),[1,2],[0,1],
                                                    [0,1,2,64,128,129], [0x30,0x71]):
        pair=[]
        for raw in [False,True]:
            m=make(b,raw);put(m,FfVariant=variant,SwimmingFlag=wet,PlayerFacingDir=face)
            run(m,'FfEnsure',raw)
            put(m,SavedJoypadBits=keys)
            costs=[]
            for tick in range(12):
                c,tr,low=run(m,'FfMovement',raw,p=p)
                run(m,'FfWeapons',raw,p=p)
                costs.append(c.processorCycles)
            pair.append((app(m),ordered(m),(c.a,c.x,c.y,c.p,c.sp),costs,m.rawtags[:]))
        assert pair[0]==pair[1],('source state/AXYP/ordered stores/map parity',variant,face,wet,keys,p)
        rows.append([variant,face,wet,keys,p,min(pair[0][3]),max(pair[0][3])])
    # Entire 32-page physical arithmetic, all four legitimate FF windows.
    publications=[]
    for page,window in itertools.product(range(32),range(4)):
        pair=[]
        for raw in [False,True]:
            m=make(b,raw);put(m,FfRenderPage=page,FfTemp2=window)
            c,tr,low=run(m,'FfPublishChunk',raw,p=0x71)
            assert (0xa275,3 if raw else 0xbe) in tr
            physical=m[address(b,'CurrentCHRBank')+window]+256*(m[address(b,'X5ChrMode')+window]&3)
            assert physical==756+page
            pair.append((app(m),ordered(m),(c.a,c.x,c.y,c.p,c.sp),c.processorCycles))
        assert pair[0]==pair[1],('same-PC publisher',page,window)
        publications.append([page,window,pair[0][3]])
    # RenderChunk intentionally returns pointers and leaves actual ROM93 C.
    renders=[]
    for entry,chunk,window,face in itertools.product([0,35,36,71,72,107,108,143,144,157],
                                                  [0,1],range(4),[1,2]):
        pair=[]
        for raw in [False,True]:
            m=make(b,raw,old_c=2);put(m,FfSlot=face)
            c,tr,low=run(m,'FfRenderChunk',raw,a=entry,x=chunk,y=window,p=0x71)
            assert m.rawtags[2]==0xdd and get(m,'CurrentBankC')==0xdd
            pair.append((app(m),ordered(m),(c.a,c.x,c.y,c.p,c.sp),c.processorCycles))
        assert pair[0]==pair[1],('render outputs R0/R1 and rawC contract',entry,chunk,window,face)
        renders.append([entry,chunk,window,face,pair[0][3]])
    return dict(source_movement_weapon_pairs=len(rows),source_movement_updates=len(rows)*12,
                physical_publisher_pairs=len(publications),source_render_pairs=len(renders),
                source_rows=rows,publisher_rows=publications,render_rows=renders,
                AXYP_SP_and_all_application_bytes_and_ordered_writes_exact=True,
                same_virtual_PC_cycles_exact=True,render_C_output='rawDD ROM93; caller must restore saved rawC',
                R0_R1='Genuine source outputs retained and compared; no blanket preservation wrapper')


def cpu_state(c): return (c.pc,c.a,c.x,c.y,c.p,c.sp)


def interrupt(m,c,kind):
    """Real vector to RTI; no fabricated handler or mapper normalization."""
    b=m.bundle;live_zp=(kind=='IRQ' or get(m,'NmiDisable')!=0);before=(cpu_state(c),m.rawtags[:],get(m,'CurrentBank'),get(m,'CurrentBankC'),
                       bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),bytes(m[:256]),
                       [bytes(x) for x in m.ram])
    expected=m.rawtags[:]
    # NMI's real source restores a pending shadow->hardware write. IRQ leaves
    # that seam intact. Preserve this documented native ABI explicitly.
    for slot,name,op in [(1,'CurrentBank',b'\x8d\x15\x51'),(2,'CurrentBankC',b'\x8d\x16\x51')]:
        if kind=='NMI' and expected[slot]!=get(m,name):
            assert bytes(m[c.pc:c.pc+3])==op,('unclassified pending hardware store',hex(c.pc))
            expected[slot]=get(m,name)
    oldcycles=c.processorCycles;low=c.sp
    if kind=='NMI': c.nmi()
    else:
        assert not c.p&c.INTERRUPT
        c.irq()
    for steps in range(100000):
        if cpu_state(c)==before[0]: break
        low=min(low,c.sp)
        assert m[c.pc]!=0,('real ISR BRK',kind,hex(c.pc),m.rawtags)
        c.step()
    else: raise AssertionError(('real ISR did not RTI',kind,cpu_state(c),before[0]))
    assert m.rawtags==expected and [get(m,'CurrentBank'),get(m,'CurrentBankC')]==list(before[2:4])
    assert bytes(m[0x15a:0x17b])==before[4],('all33SMC',kind)
    assert bytes(m[0x101+c.sp:0x200])==before[5],('live page1',kind)
    assert bytes(m[3:5])==before[6][3:5] and bytes(m[9:11])==before[6][9:11],('actual borrowed pairs',kind)
    if live_zp:
        changed=[i for i,(a,z) in enumerate(zip(before[6],m[:256])) if a!=z]
        audio=range(address(b,'XgAudioPtr'),address(b,'XgAudioZeroPageEnd'))
        assert all(kind=='NMI' and i in audio for i in changed),('live foreground ZP',kind,changed)
    assert [bytes(x) for x in m.ram]==before[7],('ISR wrote RAM0..3 payload banks',kind)
    return dict(kind=kind,CPU=c.processorCycles-oldcycles,minimum_SP=low,
                raw_maps=m.rawtags[:],AXYP_SP_SMC33_page1_R0_R1_R6_R7_exact=True)


def interrupt_controls(b):
    rows=[]; negative=[]
    # Cut every actual SFC/importer/publisher instruction, plus selected source
    # render instructions and the real C shadow->hardware transition.
    for name,args in [('FfPublishChunk',dict()),('FfRenderChunk',dict(a=72,x=0,y=3))]:
        m=make(b,True);put(m,FfRenderPage=31,FfTemp2=3,FfSlot=1)
        c=start(m,name,True,**args);cuts=[]
        for step in range(5000):
            if c.pc==0x5b00:break
            if (c.pc<0x200 or 0xa275<=c.pc<0xa289 or step%13==0 or
                bytes(m[c.pc:c.pc+3])in[b'\x8d\x15\x51',b'\x8d\x16\x51']):cuts.append((step,c.pc))
            c.step()
        else:raise AssertionError('cut discovery bounded')
        for step,pc in cuts:
            for old_a,old_c in [(0xd7,0xd8),(3,2),(0x83,0x82)]:
                for lag,kind in itertools.product([0,255],['NMI','IRQ']):
                    q=make(b,True,old_a,old_c);put(q,FfRenderPage=31,FfTemp2=3,FfSlot=1,NmiDisable=lag)
                    d=start(q,name,True,**args)
                    for _ in range(step):d.step()
                    assert d.pc==pc
                    if kind=='IRQ' and d.p&d.INTERRUPT:continue
                    proof=interrupt(q,d,kind)
                    for _ in range(5000):
                        if d.pc==0x5b00:break
                        d.step()
                    else:raise AssertionError('postISR bounded return')
                    assert q.rawtags[1]==old_a and get(q,'CurrentBank')==old_a
                    assert q.rawtags[2]==(0xdd if name=='FfRenderChunk' else old_c)
                    rows.append(dict(entry=name,step=step,PC=pc,oldA=old_a,oldC=old_c,lag=lag,**proof))
    return dict(real_interrupt_cases=len(rows),rows=rows,normal_and_lag_NMI=True,
                real_IRQ=True,raw3_vs_ROM83_and_raw2_vs_ROM82_distinct=True,
                source_contract='These are source leaf ABI interruptions, not complete FF Main/admission or a loader test.')


def main():
    assert not (O/'cpu-controls-v2.json').exists()
    O.mkdir(exist_ok=True)
    proof=dict(passed=False,native=False,explicit_RAM3_fixture_preload=True,
               allocation=False,header_change=False,shared_edits=False,checks={})
    try:
        kernel=json.loads((K/'build-proof.json').read_text())
        assert kernel['image_sha256']=='9f8a0a9034232dd110670e02285dec3bf5c1fdcebb6a6851362fa60a862ecc51'
        for path,digest_ in kernel['bindings'].items():assert sha(path)==digest_,path
        b=qualified(P/'candidate.nes')
        proof['checks']['same_PC_source_pairs']=paired(b)
        print('FF genuine ROM62/rawRAM3 source/render/publication pairs PASS',flush=True)
        proof['checks']['actual_vectors']=interrupt_controls(b)
        proof['passed']=True
    except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc())
    proof['bindings']={str(p.resolve()):sha(p) for p in [Path(__file__),P/'candidate.nes',P/'candidate.dbg',
        K/'ram3.bin',K/'build-proof.json',R/'tools/audit/arthur_cache_host_controls_v1.py',
        R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py']}
    target=O/('cpu-controls-v2.json' if proof['passed'] else 'cpu-controls-negative-v2.json')
    assert not target.exists();target.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=proof['passed'],error=proof.get('error'),output=str(target))))
    assert proof['passed']


if __name__=='__main__': main()
