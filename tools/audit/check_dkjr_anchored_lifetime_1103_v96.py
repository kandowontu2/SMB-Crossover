"""Diagnose actual public lifecycle admission in retained95 fixture."""
import inspect
import json
from pathlib import Path
import check_dkjr_anchored_lifetime_1103_v95 as P


def main():
    text=inspect.getsource(P.main)
    old="assert z.ram[2][0x8fe]==(1 if service in ['Fresh15','Scene36']else 0)"
    assert text.count(old)==1
    text=text.replace(old,old+",(service,context,z.ram[2][0x8fe],call)")
    text=text.replace('-v95-','-v96-')
    env=dict(P.__dict__,__file__=__file__)
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':
    try:main()
    except Exception as error:
        (P.O/'native-anchored-lifetime-v96-negative.json').write_text(json.dumps(dict(passed=False,error=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
