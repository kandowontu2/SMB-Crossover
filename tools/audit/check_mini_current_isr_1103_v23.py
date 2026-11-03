"""Finalv26 source-backed fifth-owner shared IRQ/FF corpus."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_mini_current_cold_1103_v22 as F
import check_mini_shared_isr_1103_v21 as S
O=F.O


def bundle():
    b,q=F.image();fit=json.loads((O/'owner-fit-v15.json').read_text())
    return dict(b,raw=F.P.M.BASE.read_bytes()),b,None,None,q,None,fit['labels'],q['patches'],[]


def source_main():
    text=S.source_main().replace('shared-ISR-v21.json','shared-ISR-v23.json').replace('shared-ISR-state-negative-v21.json','shared-ISR-state-negative-v23.json')
    text=text.replace('payload-manifest-v19.json','payload-manifest-v22.json').replace('five-cold-CPU-v20.json','five-cold-CPU-v22.json').replace('owner-final-v19.s','owner-final-v22.s')
    text=text.replace('Mini21 reuses','Mini23 finalv26 reuses')
    return text


def main():
    b,_=F.image();F.C.C.cold(b,37)
    env=dict(S.Legacy.__dict__,__file__=__file__,O=O,BUNDLE=bundle,BLANK=F.F.blank,
        PUBLIC=lambda m,pc:F.I.invoke(m,193,pc,(83,71,109,0x21)),C=F.C,F=F,LEGACY=S.Legacy)
    exec(compile(source_main(),__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
