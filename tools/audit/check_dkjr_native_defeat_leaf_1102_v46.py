"""Full earned Main after typed native defeat, plus exact service parity."""
import contextlib,io,itertools,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W


def main():
    path=R/'tools/audit/check_dkjr_native_service_packets_1102_v43.py'
    text=path.read_text().replace('native-packets','native-defeat').replace('v42','v45').replace('v43','v46')
    insertion="    source=source.replace(\"    class Trace(old):\",\"    points[q['typed_native_defeat']['genuine_native_target'],254]='NativeDefeatContinuation'\\n    class Trace(old):\")\n"
    insertion+="    source=source.replace(\"counts['ShellOrBlockDefeat']\",\"counts['NativeDefeatContinuation']\")\n"
    insertion+="    source=source.replace(\"capture=epoch;assert epoch==1\",\"capture=epoch;assert N.get(m,'Enemy_State')&0x20;assert epoch==1\")\n"
    marker="    env={'__name__':'dk_repaired_earned_main'"
    assert text.count(marker)==1;text=text.replace(marker,insertion+marker)
    env={'__name__':'dk_defeat_Main_successor','__file__':str(path)}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(text,str(path),'exec'),env);env['main']()
    actual=json.loads((O/'native-defeat-v46-CPU.json').read_text());assert actual['passed']
    fixture=R/'tools/audit/check_dkjr_native_lifecycle_1102_v31.py'
    text=fixture.read_text().replace('native-lifecycle-v30','native-defeat-v45').replace('native-lifecycle-','native-defeat-').replace('-v30.bin','-v45.bin')
    env={'__name__':'dk_defeat_service_fixture','__file__':str(fixture)};exec(compile(text,str(fixture),'exec'),env);b,seed,L,q=env['fixture']()
    cases=0
    for slot,ident,mode,flags in itertools.product(range(6),[0,3,5,6,7,13,14,20],[0,1],[0x30,0xf1]):
        m=N.fork(seed);N.put(m,SelectedCharacter=40,CrossoverBehaviorVersion=mode,ObjectOffset=slot)
        for name,value in [('Enemy_Flag',1),('Enemy_ID',ident),('Enemy_State',0),('Enemy_X_Position',80),('Enemy_PageLoc',0),('Enemy_Y_Position',184),('Enemy_Y_HighPos',1)]:m[W.address(b,name)+slot]=value
        ref=N.fork(m);a=N.invoke(ref,'ShellOrBlockDefeat',a=85,x=slot,y=91,p=flags)
        # Same native public farcall frame, different private port target.
        name='DkTypedDefeat';seg='DkTypedDefeatSegment';pc=L['NativeVictimDefeat'];b['segs'][seg]=dict(start=str(pc),ooffs=str(16+3*8192+pc-0xa000));b['syms'][name]=dict(val=str(pc),seg=seg)
        # Direct private call retains RAM3 mapping; its fixed continuation
        # requires no ROM map change. Compare full nonstack application state.
        c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,slot,91,flags,224;c.stPushWord(0x5ffe)
        for _ in range(100000):
            if c.pc==0x5fff:break
            assert m[c.pc]!=0;c.step()
        else:raise AssertionError('typed defeat bound')
        assert(c.a,c.x,c.y,c.p&0xef)==(a['A'],a['X'],a['Y'],a['P']&0xef),(slot,ident,mode,flags,a,(c.a,c.x,c.y,c.p))
        left=list.__getitem__(ref,slice(0,32768));right=list.__getitem__(m,slice(0,32768))
        diff=[(i,x,y)for i,(x,y)in enumerate(zip(left,right))if x!=y and not 0x100<=i<0x200 and not 0x2000<=i<0x5c00]
        assert not diff,(slot,ident,mode,flags,diff[:12])
        assert ref.rawtags==m.rawtags and ref.ram==m.ram
        cases+=1
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,exact_native_defeat_service_cases=cases,
        full_native_Main=actual['full_native_Main'],body_bytes=q['body_bytes'],header_spare=q['header_spare'],
        scope='Full actual native defeat service AXYP/all nonstack application RAM/maps/private arrays matches original for all declared enemy/slot/mode controls. Real wholeMain earned fruit/score/60D1AE/thaw passes exact retained negative fixture. NativeSMC is caller-owned and restored by the enclosing packet; direct service itself avoids the pointless lower-fixed farcall mapping. IRQ and final current-owner rebind remain pending.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),path,fixture,O/'native-defeat-v45-layout.json',O/'native-defeat-v45.bin',O/'native-defeat-v46-Main-CPU.json',O/'native-drop-boundary-v44.json']})
    (O/'native-defeat-v46-qualified.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,exact_native_defeat_service_cases=cases,minimum_CPU_SP=out['full_native_Main']['minimum_CPU_SP'],original_hit_updates=out['full_native_Main']['original_hit_updates'])))


if __name__=='__main__':main()
