"""Successor to the retained discovery fixture with the Lua parse error."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_smb3plus_donor_native_1030_v1 as P


def main():
    P.O=P.R/'build/smb3plus-donor-native-1030-v2/discovery'
    assert not P.O.exists() and P.sha(P.DONOR)==P.EXPECTED
    P.O.mkdir(parents=True)
    source=P.R/'tools/reference/smb3plus_donor_discovery_1030_v2.lua'
    (P.O/'controller.lua').write_bytes(source.read_bytes())
    (P.O/'run.py').write_bytes((P.R/'build/peach-palette-native-1030-v1/peach/run.py').read_bytes())
    own=[Path(__file__),Path(P.__file__),source,P.DONOR,P.O/'controller.lua',P.O/'run.py',
         P.R/'tools/run_mesen.py',P.R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]
    d=dict(prepared=True,native=False,ROM=str(P.DONOR),ROM_sha256=P.EXPECTED,host_timeout_seconds=45,
        run_cap_bytes=536870912,max_files=64,max_PNGs=3,no_debug_RAM_writes=True,
        bindings={str(p):P.sha(p)for p in own})
    (P.O/'ready.json').write_text(P.json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(P.json.dumps(dict(prepared=str(P.O/'ready.json'),source=P.EXPECTED)))


if __name__=='__main__':main()
