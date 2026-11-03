"""Only active sharedauth, raw41 public row4 and its foreignretire FF cuts."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_mini_current_isr_1103_v23 as S
O=S.O


def image():
    q=json.loads((O/'final-payload-v24.json').read_text())
    for name,digest in q['bindings'].items():assert S.F.P.M.sha((R/name).read_bytes())==digest,name
    b,_=S.F.image();raw=bytearray(S.F.P.M.BASE.read_bytes())
    for row in q['patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(old)]==old
        raw[at:at+len(new)]=new
    assert S.F.P.M.sha(raw)==q['memory_SHA256']
    return dict(b,raw=bytes(raw)),q


def bundle():
    b,q=image();fit=json.loads((O/'owner-fit-v15.json').read_text())
    return dict(b,raw=S.F.P.M.BASE.read_bytes()),b,None,None,q,None,fit['labels'],q['patches'],[]


def source_main():
    text=S.source_main().replace('shared-ISR-v23.json','live-shared-ISR-v25.json').replace('shared-ISR-state-negative-v23.json','live-shared-ISR-state-negative-v25.json')
    a=text.index('    # Each full cold');z=text.index('    result=dict(passed=True,CPU_only=True',a)
    text=text[:a]+'''    for owner in [37,38,39,40,41]:
        seed,_=C.C.cold(b,owner)
        N.put(seed,DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=255,FamilyMainCommit=1)
        C.C.clear(seed)
        run(('live-auth',owner),lambda seed=seed:PUBLIC(seed,nl['CoCheckCode']))
        if owner==41:
            run(('live-public41-row4',owner),lambda seed=seed:PUBLIC(N.fork(seed),0xb098))
            m=N.fork(seed);N.put(m,SelectedCharacter=0);C.C.clear(m)
            run(('live-retire41',owner),lambda m=m:PUBLIC(m,nl['CoRetire']))
    seed=BLANK(b,36);PUBLIC(seed,0xac1d)
    N.put(seed,DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=255,FamilyMainCommit=1)
    C.C.clear(seed)
    run(('live-Sh-index5',36),lambda seed=seed:PUBLIC(seed,0xa800))
'''+text[z:]
    a=text.index("        scope='Mini23");z=text.index('        remaining=',a)
    text=text[:a]+"        scope='Exact frozenhost28/c393 source-backed payload. Only active fullauth37..41/Sh36-index5, actual41publicrow4 and actualforeign41retire. Screenon0/PPUMASK30 permits the genuineFF negativebranchCLI; no forcedblank cold winner is invented. Every reached shared/FarCall instruction context receives actualnative IRQ whenI0 and actualFFNMI forI0/I1. CPU/live stack/private/native/scratch/SMC/maps exact; PPU/audio equal unchanged nativehandler. This does not qualify MiniStep/nativeMain/gameplay or grant menu/install.',\n"+text[z:]
    text=text.replace("O/'payload-manifest-v22.json',O/'five-cold-CPU-v22.json',O/'owner-final-v22.s'","O/'final-payload-v24.json',O/'five-cold-CPU-v22.json',O/'owner-final-v24.s'")
    return text


def environment():
    return dict(S.S.Legacy.__dict__,__file__=__file__,O=O,BUNDLE=bundle,BLANK=S.F.F.blank,
        PUBLIC=lambda m,pc:S.F.I.invoke(m,193,pc,(83,71,109,0x21)),C=S.F.C,F=S.F,LEGACY=S.S.Legacy)


def main():
    b,_=image();S.F.C.C.cold(b,37)
    env=environment();exec(compile(source_main(),__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
