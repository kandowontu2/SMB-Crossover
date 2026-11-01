"""Source-linked12-row loader and equipment in actual native Main.

The parent ROM is immutable. A declared in-memory ROM image supplies the
separately compiled proposal, before an actual owning-object build. No native
ROM, emulator, nightly or hardware admission claim is made.
"""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import build_karnov_options_host_component_1101_v8 as A
import check_karnov_combat_main_1101_v6 as T
import check_karnov_loader_funding_1101_v6 as F
from check_tmnt_render_oa import address

O=A.O;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def model():
    stage=json.loads((O/'assembly.json').read_text());assert stage['passed']
    for p,h in stage['bindings'].items():assert sha(p)==h,p
    b=T.H.C.qualified(A.B/'candidate.nes');F.O=O
    fragments={p.name:p.read_text()for p in O.glob('*.inc')}
    b,assembly=F.assemble(b,'resident-v8',(O/'resident-proposal.inc').read_text(),fragments,set())
    for line in(O/'component.lbl').read_text().splitlines():
        z=line.split()
        if len(z)!=3:continue
        name=z[2].lstrip('.');value=int(z[1],16)
        if name.startswith('NativeBase'):continue
        b['syms'][name]={**b['syms'].get(name,{}),'val':hex(value)}
    raw=bytearray(b['raw'])
    for page,name in [(399,'kernel.bin'),(1019,'combat.bin'),(1021,'options.bin')]:
        data=(O/name).read_bytes();at=1048592+page*1024;raw[at:at+len(data)]=data
    b['raw']=bytes(raw)
    return b,assembly


def step(m,keys=0,observer=None):
    for name in ['writes','ram_writes','ppu_log']:
        if hasattr(m,name):getattr(m,name).clear()
    T.keys(m,keys);c,low=T.P.call(m,'GameLoop',observer=observer);T.C.consume(m);return c,low


def lifetime(m,option):
    """Sustained native updates after an explicitly fixture-earned activation."""
    T.C.consume(m)
    for _ in range(4):step(m)
    if option==0:
        base=T.H.get(m,'Player_Y_Position');peak=base
        for n in range(80):
            step(m,128 if n<22 else 0)
            peak=min(peak,T.H.get(m,'Player_Y_Position'))
        rise=base-peak
        assert rise==88,('Original boots jump',rise)
        expired=None
        for n in range(720):
            step(m)
            if not m.ram[2][0x65]&128:expired=n+85;break
        assert expired is not None,'Boots did not expire'
        return dict(original_jump_rise=rise,expiry_accepted_updates=expired)
    if option==3:
        fired=None;returned=None
        for n in range(340):
            step(m,64 if n%24==0 else 0)
            if m.ram[2][0x6e]&128 and fired is None:fired=n
            if fired is not None and m.ram[2][0x65]&15==2:
                returned=n;break
        assert fired is not None and returned is not None,('Boomerang flight/return',fired,returned)
        return dict(fired_update=fired,returned_update=returned,restored_flame_tier=m.ram[2][0x65]&15)
    base=T.H.get(m,'Player_Y_Position')
    for _ in range(20):step(m,8)
    up=T.H.get(m,'Player_Y_Position')
    for _ in range(20):step(m,4)
    down=T.H.get(m,'Player_Y_Position')
    assert up<base and down>up,('Original wings vertical controls',base,up,down)
    expired=None
    for n in range(1100):
        step(m)
        if m.ram[2][0x62]&31 not in [15,16]:expired=n+45;break
    assert expired is not None,'Wings did not expire'
    return dict(initial_Y=base,after_Up_Y=up,after_Down_Y=down,expiry_accepted_updates=expired)


def checks():
    b,assembly=model();T.INTEGRATED=True
    seed,setup=T.boot(b)
    assert bytes(seed.ram[2][0x1600:0x1e00])==(O/'options.bin').read_bytes()
    assert seed.ram[2][0x8e]==255
    # Deliberate earned-equipment state fixture, no object collection claim.
    seed.ram[2][0x65]=2;seed.ram[2][0x8f]=255
    for p in [0xbd,0xbe,0xbf]:seed.ram[2][p]=1
    rows=[];minimum_ISR=255
    for option,presses,stock in [(0,1,0xbd),(3,2,0xbe),(7,3,0xbf)]:
        m=T.C.fork(seed)
        for _ in range(presses):step(m,32);step(m)
        assert m.ram[2][0x8e]==option
        T.keys(m,68);origin=T.C.fork(m);trace=[];events=[]
        points={address(b,n):n for n in ['KrOptionsControls','KrOptionsNative','Kr_C5A0','KrOptionsTick','Kr_ADA8']}
        def observe(mem,c,i):
            bank=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None
            trace.append((c.pc,c.sp,bank))
            if bank==2 and c.pc in points:events.append((points[c.pc],i,c.sp))
        c,low=T.P.call(m,'GameLoop',observer=observe)
        assert m.ram[2][stock]==0,(option,'Original stock not consumed')
        if option==0:assert m.ram[2][0x65]&128
        if option==3:assert m.ram[2][0x65]&15==8
        if option==7:assert m.ram[2][0x62]&31 in [15,16]
        cuts={next(i for i,z in enumerate(trace)if z[1]==low)}|{e[1]for e in events}
        interrupts=[]
        for cut,kind in itertools.product(sorted(cuts),['IRQ','NMI']):
            z=T.C.fork(origin);hits=[]
            def inject(mem,c,i):
                if i==cut:hits.append(F.V.interrupt(mem,c,kind))
            try:
                cc,ll=T.P.call(z,'GameLoop',observer=inject)
                assert len(hits)==1 and(cc.a,cc.x,cc.y,cc.p,cc.sp)==(c.a,c.x,c.y,c.p,c.sp)
                assert T.foreground(z)==T.foreground(m)
            except Exception as e:
                interrupts.append(dict(passed=False,kind=kind,cut=cut,PC=trace[cut][0],SP=trace[cut][1],error=repr(e)))
                continue
            minimum_ISR=min(minimum_ISR,hits[0]['minimum_SP']);interrupts.append(dict(passed=True,cut=cut,**hits[0]))
        row=dict(option=option,stock_after=m.ram[2][stock],minimum_Main_SP=low,source65=m.ram[2][0x65],source62=m.ram[2][0x62],events=events,interrupts=interrupts)
        row['sustained_effect']=lifetime(m,option);rows.append(row)
    return dict(passed=minimum_ISR>=135 and all(z['passed']for r in rows for z in r['interrupts']),
                setup_Main=setup,minimum_Main_ISR_SP=minimum_ISR,cases=rows,resident=assembly)


def main():
    prior=O/'Main-controls.json';negative=O/'Main-input-negative.json'
    if prior.exists()and not negative.exists()and not json.loads(prior.read_text())['passed']:negative.write_bytes(prior.read_bytes())
    q=dict(passed=False,parent_ROM_sha256=A.PIN,in_memory_ROM_source_model=True,installed=False,native=False)
    try:q['Main']=checks();q['passed']=q['Main']['passed']
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(A.__file__),A.B/'candidate.nes',A.B/'candidate.dbg',O/'assembly.json',O/'kernel.bin',O/'options.bin']}
    (O/'Main-controls.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=q['passed'],error=q.get('error'),minimum_ISR=q.get('Main',{}).get('minimum_Main_ISR_SP'),cases=[dict(option=r['option'],SP=r['minimum_Main_SP'],failures=[z for z in r['interrupts']if not z['passed']])for r in q.get('Main',{}).get('cases',[])])))
    assert q['passed'],q.get('error','Main/ISR reserve')


if __name__=='__main__':main()
