"""Bind the scene36 test to its actual published B0F8 entry, not a fake label."""
import inspect
import json
from pathlib import Path
import check_dkjr_anchored_entrance_1103_v91 as P


def main():
    text=inspect.getsource(P.main)
    text=text.replace("['HuFresh','HuGenericFresh']","['HuFresh','published_B0F8_scene36']")
    old="        z=N.invoke(n,name,a=83,x=0,y=109,p=0x21)"
    new="""        if name=='HuFresh':z=N.invoke(n,name,a=83,x=0,y=109,p=0x21)
        else:
            actual=C.I.invoke(n,193,0xb0f8,(83,0,109,0x21))
            z={'P':actual['regs'][3]}"""
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace('native-entrance-v91-CPU.json','native-entrance-v92-CPU.json')
    text=text.replace("Path(__file__),Path(P.__file__)","Path(__file__),V91_PATH,Path(P.__file__)")
    env=dict(P.__dict__,__file__=__file__,V91_PATH=Path(P.__file__))
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':
    try:main()
    except Exception as error:
        (P.O/'native-entrance-v92-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
