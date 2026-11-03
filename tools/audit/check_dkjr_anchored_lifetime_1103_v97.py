"""Use actual ROM-only Reset19 and virtual37 entry, retaining95/96 oracle negatives."""
import inspect
import json
from pathlib import Path
import check_dkjr_anchored_lifetime_1103_v95 as P


def main():
    text=inspect.getsource(P.main)
    old="                assert z.ram[2][0x8fe]==(1 if service in ['Fresh15','Scene36']else 0)"
    new="""                if service=='Reset19':
                    # Actual B0C5→B100 is the source-owned ROM-only retirement
                    # entry, not the private vector19. It invalidates both
                    # complete headers before any replacement; privateReady2
                    # becomes unreachable, then cold clears it before Fresh.
                    assert z.ram[2][0x8fe]==2
                    for bank in [2,3]:assert z.ram[bank][0x1fe0]==0
                else:assert z.ram[2][0x8fe]==1"""
    assert text.count(old)==1;text=text.replace(old,new)
    old="C.I.invoke(z,193,0xb08c+3*row,(0,0,0,0x21))"
    assert text.count(old)==1
    text=text.replace(old,"C.I.invoke(z,193,0xb029 if row==37 else 0xb08c+3*row,(0,0,0,0x21))")
    text=text.replace('-v95-','-v97-')
    text=text.replace("Path(__file__),Path(P.__file__),Path(E.__file__)","Path(__file__),V95_PATH,Path(P.__file__),Path(E.__file__)")
    text=text.replace("populated_pause_reset_retire_cases=scene,","populated_pause_reset_retire_cases=scene,actual_public_Reset19='65:B0C5 JMPB100 JSRCoRetire; invalidates headers, does not enter privateReset',virtual_contact37_entry=0xb029,")
    env=dict(P.__dict__,__file__=__file__,V95_PATH=Path(P.__file__))
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':
    try:main()
    except Exception as error:
        (P.O/'native-anchored-lifetime-v97-negative.json').write_text(json.dumps(dict(passed=False,error=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
