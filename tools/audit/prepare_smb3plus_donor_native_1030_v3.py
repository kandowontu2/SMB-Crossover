"""Observe the donor after its long native opening sequence."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_smb3plus_donor_native_1030_v1 as P


def main():
    out=P.R/'build/smb3plus-donor-native-1030-v3/discovery'
    assert not out.exists()and P.sha(P.DONOR)==P.EXPECTED
    out.mkdir(parents=True)
    source=P.R/'tools/reference/smb3plus_donor_discovery_1030_v2.lua'
    text=source.read_text()
    text=text.replace('(frame >= 65 and frame <= 68) or (frame >= 180 and frame <= 183)',
        '(frame >= 600 and frame <= 603) or (frame >= 900 and frame <= 903) or (frame >= 1200 and frame <= 1203)')
    text=text.replace('frame == 120 or frame == 240 or frame == 360','frame == 500 or frame == 1100 or frame == 1400')
    text=text.replace('if frame == 360 then','if frame == 1400 then')
    (out/'controller.lua').write_text(text,encoding='utf-8',newline='\n')
    (out/'run.py').write_bytes((P.R/'build/peach-palette-native-1030-v1/peach/run.py').read_bytes())
    own=[Path(__file__),Path(P.__file__),source,P.DONOR,out/'controller.lua',out/'run.py',
         P.R/'tools/run_mesen.py',P.R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]
    d=dict(prepared=True,native=False,ROM=str(P.DONOR),ROM_sha256=P.EXPECTED,host_timeout_seconds=60,
        run_cap_bytes=536870912,max_files=64,max_PNGs=3,no_debug_RAM_writes=True,
        bindings={str(p):P.sha(p)for p in own})
    (out/'ready.json').write_text(P.json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(P.json.dumps(dict(prepared=str(out/'ready.json'),source=P.EXPECTED)))


if __name__=='__main__':main()
