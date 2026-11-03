"""Actual changed fifth-owner/cold/auth seams under IRQ and genuine FF NMI."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_mini_five_cold_1103_v20 as F
import check_bub_shared_auth_interrupts_1103_v79 as Legacy
O=F.O


def bundle():
    b,q=F.image();fit=json.loads((O/'owner-fit-v15.json').read_text())
    return dict(b,raw=F.P.M.BASE.read_bytes()),b,None,None,q,None,fit['labels'],q['patches'],[]


def source_main():
    source=inspect.getsource(Legacy.main)
    source=source.replace("O/'shared-auth-v79-ISR.json'","O/'shared-ISR-v21.json'")
    source=source.replace("O/'shared-auth-v79-initial-state-negative.json'","O/'shared-ISR-state-negative-v21.json'")
    source=source.replace('P.P.P.build()','BUNDLE()').replace('P.P.C.clear(m)','C.C.clear(m)')
    source=source.replace('0xab72<=pc<0xabce','0xab72<=pc<0xabd4')
    source=source.replace('            watched=watched or 0x15a<=pc<0x17b','            watched=watched or tag==251 and 0xb9d6<=pc<0xba00\n            watched=watched or tag==2 and 0xd25e<=pc<0xd2cf\n            watched=watched or 0x15a<=pc<0x17b')
    a=source.index('    for owner in [36,37,38,39,40]:');z=source.index('    result=dict(passed=True,CPU_only=True',a)
    source=source[:a]+'''    # Each full cold reaches genuineI0 then actualSEI/I1. No filter omitsI1FF.
    for owner in [37,38,39,40,41]:
        seed=BLANK(b,owner);C.C.clear(seed)
        run(('cold',owner),lambda seed=seed:PUBLIC(seed,0xae00))
        m=N.fork(seed);N.put(m,SelectedCharacter=0,NmiDisable=255,FamilyMainCommit=1)
        C.C.clear(m)
        run(('retire',owner),lambda m=m:PUBLIC(m,nl['CoRetire']))
        m=N.fork(seed);N.put(m,NmiDisable=255,FamilyMainCommit=1)
        C.C.clear(m)
        run(('auth',owner),lambda m=m:PUBLIC(m,nl['CoCheckCode']))
    seed=BLANK(b,36);C.C.clear(seed)
    run(('Sh-cold',36),lambda seed=seed:PUBLIC(seed,0xac1d))
    C.C.clear(seed)
    run(('Sh-index5',36),lambda seed=seed:PUBLIC(seed,0xa800))
'''+source[z:]
    a=source.index('        bindings={p.relative_to(R).as_posix():sha(p)for p in [')
    z=source.index(']})',a)+4
    source=source[:a]+'''        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(LEGACY.__file__),Path(F.__file__),
            O/'payload-manifest-v19.json',O/'five-cold-CPU-v20.json',O/'owner-final-v19.s',O/'owner-v15.s',O/'selector-v15.s',O/'common-v15.s',O/'cold-v19.s',R/'src/reset.s',R/'src/music_drivers/vanilla_sfx.s']})
'''+source[z:]
    source=source.replace("remaining=['Deepest actual lag-handler nestedIRQ replay across all retained contexts.','Complete external caller/reference closure and pending combined-owner source rebind.']","remaining=['Deepest actual handler nestedIRQ replay and source-derived external imports/deadA/upper-latch closure.','Root finalkernel/native ingress and scene/frontend composition remain separate.']")
    source=source.replace("scope='Genuine full native IRQ", "scope='Mini21 reuses the exact native79 IRQ/FF state machine but supplies actual current five-owner cold/retire/auth plus Sh cold/index5. Changed common map and Mini D25E copier PCs are watched. No source Main or finalfrontend/native readiness claim. Genuine full native IRQ")
    return source


def main():
    # Initialize the exact existing bus class, without retaining cold logs.
    b,_=F.image();F.C.C.cold(b,37)
    env=dict(Legacy.__dict__,__file__=__file__,O=O,BUNDLE=bundle,BLANK=F.blank,
             PUBLIC=lambda m,pc:F.I.invoke(m,193,pc,(83,71,109,0x21)),C=F.C,F=F,LEGACY=Legacy)
    exec(compile(source_main(),__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
