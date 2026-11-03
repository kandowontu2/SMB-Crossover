"""Measure higher original support by waiting for observed rising-bubble height."""
from pathlib import Path
import check_bub_powered_bubble_1103_v92 as P


def main():
    text=Path(P.__file__).read_text()
    before="""keys=1 if bubble and bubble['gap']>20 else 0
                    if bubble and bubble['kind']==2 and 10<=bubble['gap']<=28:
                        phase='align';keys=128"""
    after="""keys=1 if bubble and bubble['gap']>34 else 0
                    if bubble and bubble['kind']==2 and 30<=bubble['gap']<=36 and bubble['dy']<=-16:
                        phase='forward';keys=129"""
    assert text.count(before)==1
    text=text.replace(before,after).replace("'powered-bubble-CPU.json'","'powered-bubble-CPU-v94.json'")
    text=text.replace('for identity in[0,1]:','for scenario in range(8):\n        identity=scenario//4')
    before="m=earn_shoes(b,route,identity);actor=0x42 if identity else 0x2e"
    after=before+"\n        for pad in range(scenario%4):\n            N.put(m,FrameCounter=pad,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0)\n            N.invoke(m,'GameCoreRoutine',x=0,y=0)"
    assert text.count(before)==1;text=text.replace(before,after)
    text=text.replace('row=dict(identity=identity,events=events,','row=dict(identity=identity,neutral_prefix=scenario%4,events=events,')
    text=text.replace("Path(__file__),ROM,","Path(__file__),Path(Parent.__file__),ROM,")
    text=text.replace("samples=[v for v in trace if v['update']%10==0]","neutral_prefix=scenario%4,samples=[]")
    text=text.replace("all(any(e['support']&127 for e in row['events'])for row in rows)","all(any(e['support']&127 for e in row['events'])and row['minimum_native_y']<=96 for row in rows)")
    env=dict(P.__dict__,Parent=P,__file__=__file__,__name__='powered94')
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
