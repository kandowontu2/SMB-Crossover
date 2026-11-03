"""Measure the powered Right-latched interception from first mature bubble."""
from pathlib import Path
import check_bub_powered_bubble_1103_v92 as P


def main():
    text=Path(P.__file__).read_text()
    before="""keys=1 if bubble and bubble['gap']>20 else 0
                    if bubble and bubble['kind']==2 and 10<=bubble['gap']<=28:
                        phase='align';keys=128"""
    after="""keys=1
                    if bubble and bubble['kind']==2 and 30<=bubble['gap']<=48:
                        phase='forward';keys=129"""
    assert text.count(before)==1
    text=text.replace(before,after).replace("'powered-bubble-CPU.json'","'powered-bubble-CPU-v93.json'")
    text=text.replace("Path(__file__),ROM,","Path(__file__),Path(Parent.__file__),ROM,")
    text=text.replace("samples=[v for v in trace if v['update']%10==0]","samples=[v for v in trace if v['update']%10==0 and v['update']<100]")
    env=dict(P.__dict__,Parent=P,__file__=__file__,__name__='powered93')
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
