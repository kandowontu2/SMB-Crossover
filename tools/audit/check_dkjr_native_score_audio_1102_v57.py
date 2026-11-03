"""Every nested IRQ-in-lag position in four real score/hit lifetime cohorts."""
import inspect
from pathlib import Path
import check_dkjr_native_score_tail_irq_1102_v56 as P


def main():
    text=inspect.getsource(P.main)
    old="ap.add_argument('--phase',choices=['deep','direct','nested'],default='deep')"
    assert text.count(old)==1
    text=text.replace(old,"ap.add_argument('--phase',choices=['nested'],default='nested')")
    old='for epoch,(seed,ref,expected)in cohorts.items():'
    assert text.count(old)==1
    text=text.replace(old,old+"\n                if epoch not in [1,2,61,62]:continue")
    text=text.replace('native-scoretail-v56-','native-scoretail-v57-')
    text=text.replace("for p in[Path(__file__),Path(I.__file__)","for p in[Path(__file__),V56_PATH,Path(I.__file__)")
    text=text.replace("phase=args.phase,genuine_NmiDisable=255,", "phase=args.phase,genuine_NmiDisable=255,lifetime_cohorts=[1,2,61,62],")
    text=text.replace("No latestowner/cold/native/menu/admission claim.", "Four cohorts: capture/400score1, firstD1AEhit2, terminalD1AE/800score61, normal-thaw62; all reached unmasked lag/audio positions in each. No latestowner/cold/native/menu/admission claim.")
    env=dict(P.__dict__);env.update(__name__='dk_full_nested_audio',__file__=__file__,V56_PATH=Path(P.__file__))
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
