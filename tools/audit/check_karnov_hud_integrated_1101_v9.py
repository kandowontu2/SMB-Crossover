"""Actual owning-link HUD lifecycle, resource, queue and interrupt checks."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_karnov_options_integrated_1101_v8 as I
import check_karnov_combat_main_1101_v6 as T
import check_karnov_options_host_component_1101_v8 as Q
import check_karnov_loader_funding_1101_v6 as F
from check_tmnt_render_oa import address,location
from prepare_karnov_hud_host_1101_v9 import GRANT,GRANT_SHA
J=T.BASE;O=R/'build/karnov-hud-native-1101-v9'
PIN='99bf88c8d971f1305f965a21833703c7a11aafa6a24febd9f3bfb7c87ba4bbda'
PARENT='1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def owners(b):
    assert sha(GRANT)==GRANT_SHA
    g=json.loads(GRANT.read_text());assert g['passed']and g['old_owner_font_resource_granted']and g['conditional_cache6B_granted']
    p=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');assert sha(p)==PARENT
    old=p.read_bytes();new=b['raw'];assert len(old)==len(new)
    allowed=[(location(b,'KrResidentBegin'),location(b,'KrResidentLimit')),
             (1048592+399*1024,1048592+407*1024),(1048592+1019*1024,1048592+1024*1024)]
    v=location(b,'KrServiceVeneers')
    for row in range(37):
        at=v+3*row;assert old[at]==new[at]==76
        assert new[at+1]|new[at+2]<<8==address(b,'KrDispatch')
        allowed.append((at+1,at+3))
    for n,offset in [('InitScreen',12),('FmResolve::Native',4),('FmStartFlags',4)]:
        at=location(b,n)+offset-1;assert old[at]==new[at]==169 and old[at+2:at+15]==new[at+2:at+15]
        allowed.append((at+1,at+2))
    changed=[i for i,(a,z)in enumerate(zip(old,new))if a!=z]
    outside=[i for i in changed if not any(l<=i<h for l,h in allowed)]
    assert not outside,('Foreign owner changed',outside[:20])
    at=1048592+1023*1024;assert new[at:at+1024]==(J/'kr-hud-font.chr').read_bytes()
    return dict(passed=True,parent_ROM_sha256=PARENT,grant_sha256=GRANT_SHA,unchanged_other_owners=True,allowed_intervals=allowed,changed_bytes=len(changed))


def snapshot(m):
    fields=['InvHudActive','InvHudPhysical','X5HudChrUpper','X5WideChrActive','ReloadCHRBank','VRAM_Buffer1_Offset','VRAM_Buffer_AddrCtrl']
    at=address(m.bundle,'VRAM_Buffer1')
    return T.foreground(m),[T.H.get(m,n)for n in fields],bytes(m[at:at+80])


def hud(b):
    seed,setup=T.boot(b);rows=[];minimum=255
    for option,index,stock in [(0,0,0xbd),(3,1,0xbe),(7,2,0xbf),(255,3,0)]:
        m=T.C.fork(seed);m.ram[2][0x8e]=option;m.ram[2][0x8f]=137
        for p in [0xbd,0xbe,0xbf]:m.ram[2][p]=2
        T.H.put(m,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,InvHudActive=0)
        m[address(b,'VRAM_Buffer1')]=0
        T.keys(m);origin=T.C.fork(m);trace=[]
        lo,hi=address(b,'KrHudTick'),address(b,'KrHudMasks')
        def observer(mem,c,i):
            bank=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None
            if bank==2 and lo<=c.pc<hi:trace.append((i,c.pc,c.sp,mem[c.pc]))
        c,low=T.P.call(m,'GameLoop',observer=observer)
        assert trace and T.H.get(m,'InvHudActive')==233
        assert [T.H.get(m,n)for n in ['InvHudPhysical','X5HudChrUpper','X5WideChrActive']]==[255,3,1]
        assert m.ram[2][0x87a]==index and m.ram[2][0x87b]==(2 if index<3 else 0)
        at=address(b,'VRAM_Buffer1');packet=bytes(m[at:at+36]);assert packet[35]==0
        assert packet[3:12]==bytes(36 if z==' 'else ord(z)-55 for z in ['BOOTS    ','BOOMERANG','WINGS    ','FIRE     '][index])
        if index<3:assert [packet[i]for i in [28,29,33,34]]==list(range(0x30+4*index,0x34+4*index))
        # Cover the first instruction, deepest Main point, both queue loops,
        # all6 context writes and native font-release store seams.
        cuts={trace[0][0],min(trace,key=lambda z:z[2])[0]}
        for name in ['KrHudCopy','KrHudLease','KrHudSave','KrHudCacheCommit']:
            pc=address(b,name);cuts.add(next(z[0]for z in trace if z[1]==pc))
        cuts.update(i for i,pc,sp,op in trace if op in [0x8d,0x9d]and
                    (int.from_bytes(m.ram[2][pc-0xc000+1:pc-0xc000+3],'little')in [address(b,n)for n in ['InvHudActive','InvHudPhysical','X5HudChrUpper','X5WideChrActive','ReloadCHRBank','VRAM_Buffer1_Offset']]or 0xc87a<=int.from_bytes(m.ram[2][pc-0xc000+1:pc-0xc000+3],'little')<0xc880))
        interrupts=[]
        for cut,kind in itertools.product(sorted(cuts),['IRQ','NMI']):
            z=T.C.fork(origin);events=[]
            def inject(mem,c,i):
                if i==cut:events.append(F.V.interrupt(mem,c,kind))
            cc,ll=T.P.call(z,'GameLoop',observer=inject)
            assert len(events)==1 and(cc.a,cc.x,cc.y,cc.p,cc.sp)==(c.a,c.x,c.y,c.p,c.sp)and snapshot(z)==snapshot(m),('HUD Main interruption',option,cut,kind)
            minimum=min(minimum,events[0]['minimum_SP']);interrupts.append(dict(cut=cut,**events[0]))
        # Real native constructor must cancel its derived font on a same-life
        # area seam even if selection/stock remain unchanged.
        seam=T.C.fork(m);T.H.put(seam,AreaAddrsLOffset=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,FamilyMainCommit=1)
        T.C.invoke(seam,'InitScreen')
        assert T.H.get(seam,'InvHudActive')==0 and seam.ram[2][0x8e]==option
        retired=T.C.fork(m);T.C.invoke(retired,'KrRetire')
        assert T.H.get(retired,'InvHudActive')==0 and T.H.get(retired,'ReloadCHRBank')==1
        assert retired.ram[2][0x1fe0]==retired.ram[3][0x1fe0]==0
        rows.append(dict(option=option,index=index,packet=list(packet),minimum_Main_SP=low,interrupts=interrupts,area_cancel=True,ROM_retirement_cancel=True))
    return dict(passed=minimum>=135,setup_Main=setup,minimum_ISR_SP=minimum,cases=rows)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--part',choices=['hud','regression'],required=True);ap.add_argument('--reuse-loader',action='store_true');args=ap.parse_args()
    O.mkdir(exist_ok=True);assert not(O/'binding.json').exists()and sha(J/'candidate.nes')==PIN
    if args.part=='hud':
        previous=O/'hud-controls.json';negative=O/'hud-fixture-negative.json'
        if previous.exists()and not negative.exists()and not json.loads(previous.read_text())['passed']:negative.write_bytes(previous.read_bytes())
    stage=json.loads((J/'terrain-assembly.json').read_text());assert stage['passed']and stage['equipment_hud']
    for p,h in stage['bindings'].items():assert sha(p)==h,p
    T.INTEGRATED=True;T.EXPECTED=PIN;b=T.bundle();assert (J/'kr-cookie.bin').read_bytes()[3]==16
    q=dict(passed=False,ROM_sha256=PIN,no_executable_overlay=True,native_emulator=False,installed=False)
    try:
        q['owners']=owners(b)
        if args.part=='hud':q['HUD_Main']=hud(b);q['passed']=q['HUD_Main']['passed']
        else:
            if args.reuse_loader:
                previous=O/'regression-controls.json';negative=O/'regression-payload-negative.json'
                old=json.loads(previous.read_text());assert old['ROM_sha256']==PIN and old['loader']['passed']
                # The first run completed all loader/header/coldMain checks,
                # then rejected the intentionally extended options carrier
                # against the obsolete pre-HUD component fixture. Reuse only
                # that passed loader, with its exact unchanged dependencies.
                exceptions={str(Path(__file__).resolve()),str(Path(Q.__file__).resolve())}
                for p,h in old['bindings'].items():
                    if p not in exceptions:assert sha(p)==h,p
                if not negative.exists():negative.write_bytes(previous.read_bytes())
                assert sha(negative)==sha(previous)
                q['loader']=old['loader'];q['loader_reuse']=dict(passed=True,negative_receipt_sha256=sha(negative),fixture_only_changes=sorted(exceptions),loader_source_and_actual_ROM_unchanged=True)
            else:q['loader']=I.loader(b)
            Q.model=lambda:(b,dict(actual_owning_link=True,ROM_sha256=PIN))
            q['equipment_Main']=Q.checks(expected_options=(J/'kr-options.bin').read_bytes());q['combat_Main']=T.main_checks()
            q['passed']=q['equipment_Main']['passed']and q['combat_Main']['passed']
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(I.__file__),Path(Q.__file__),Path(T.__file__),Path(F.__file__),GRANT,J/'terrain-assembly.json',J/'candidate.nes',J/'candidate.dbg',J/'kr-kernel.bin',J/'kr-options.bin',J/'kr-combat.bin',J/'kr-hud-font.chr']}
    (O/(args.part+'-controls.json')).write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=q['passed'],part=args.part,error=q.get('error'),minimum_ISR=q.get('HUD_Main',{}).get('minimum_ISR_SP'))))
    assert q['passed'],q.get('error','HUD/Main reserve')


if __name__=='__main__':main()
