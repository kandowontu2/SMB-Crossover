"""Bind leftward rounding to genuine original D6E1 fractional subtraction."""
import inspect
import json
from pathlib import Path
import check_dkjr_current_main_1103_v85 as V85
import check_dkjr_current_main_1103_v83 as P
import check_dkjr_native_lifecycle_1102_v31 as D


def main():
    oracle=D.D.Bus();oracle[0x56]=0;oracle[0x213]=112
    for _ in range(60):
        c=D.D.T.NesMPU(memory=oracle,pc=0xd6e1);c.sp=224;c.stPushWord(0x5ffe)
        for _ in range(100):
            if c.pc==0x5fff:break
            c.step()
        else:raise AssertionError('Original left fraction bound')
        oracle[0x213]=c.a
    assert oracle[0x213]==74 and oracle[0x56]==128
    text=inspect.getsource(V85.main)
    text=text.replace("text=inspect.getsource(P.main)","text=inspect.getsource(P.main).replace(\"delta==-37\",\"delta==-38\")")
    text=text.replace('native-current-main-v85-CPU.json','native-current-main-v86-CPU.json')
    env=dict(V85.__dict__,__file__=__file__)
    exec(compile(text,__file__,'exec'),env);env['main']()
    path=P.O/'native-current-main-v86-CPU.json';q=json.loads(path.read_text())
    q['original_left_fraction_control']=dict(original_PC=0xd6e1,updates=60,start_fraction=0,end_fraction=128,deltaX=-38,reason='Exact original SEC/SBC#$A0 and byte borrow; negative37.5 rounds down to minus38.')
    q['bindings'].update({p.relative_to(P.R).as_posix():P.A.sha(p.read_bytes())for p in [Path(V85.__file__),Path(D.__file__)]})
    path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
    try:main()
    except Exception as error:
        (P.O/'native-current-main-v86-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
