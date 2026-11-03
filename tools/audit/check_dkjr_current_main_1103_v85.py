"""Use legal native viewport bounds and constructor-owned anchor transport.

84 located83's first wrong write at native KeepOnscr (129:AA59): its missing
right bound was zero. The source actor stayed atX40 throughout. A scripted
left-control start must also run Fresh, rather than move nativeX alone.
"""
import inspect
import json
from pathlib import Path
import check_dkjr_current_main_1103_v83 as P


def main():
    text=inspect.getsource(P.main)
    old='        AreaParserTaskNum=7,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0,DisableIntermediate=1)'
    new='''        AreaParserTaskNum=7,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0,DisableIntermediate=1,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0)'''
    assert text.count(old)==1;text=text.replace(old,new)
    old='''                N.put(m,Player_X_Position=120)
                # Legal world transport of the already constructed actor;
                # genuine Main performs all subsequent source movement.'''
    new='''                N.put(m,Player_X_Position=120,DisableScreenFlag=1,Mirror_PPUMASK=0)
                fresh=N.invoke(m,'HuFresh',a=83,x=0,y=109,p=0x21)
                assert fresh['P']&1
                N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30)'''
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace('native-current-main-v83-CPU.json','native-current-main-v85-CPU.json')
    text=text.replace("Path(__file__),Path(P.__file__)","Path(__file__),V83_PATH,Path(P.__file__)")
    env=dict(P.__dict__,__file__=__file__,V83_PATH=Path(P.__file__))
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':
    try:main()
    except Exception as error:
        (P.O/'native-current-main-v85-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
