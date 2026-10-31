"""Prepare a tiny controller-only original-donor discovery run."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
O=R/'build/smb3plus-donor-native-1030-v1/discovery'
DONOR=Path('C:/NES/the stash/Super Mario Bros. 3+.nes')
EXPECTED='be750155f9005314d6ba79874c4de5b979cad0526b6cb348194d2bd4f3b90c56'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 assert not O.exists()and sha(DONOR)==EXPECTED
 O.mkdir(parents=True)
 source=R/'tools/reference/smb3plus_donor_discovery_1030_v1.lua'
 (O/'controller.lua').write_bytes(source.read_bytes())
 (O/'run.py').write_bytes((R/'build/peach-palette-native-1030-v1/peach/run.py').read_bytes())
 own=[Path(__file__),source,DONOR,O/'controller.lua',O/'run.py',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]
 d=dict(prepared=True,native=False,ROM=str(DONOR),ROM_sha256=EXPECTED,host_timeout_seconds=45,
   run_cap_bytes=536870912,max_files=64,max_PNGs=3,no_debug_RAM_writes=True,
   bindings={str(p):sha(p)for p in own})
 (O/'ready.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps(dict(prepared=str(O/'ready.json'),source=EXPECTED)))


if __name__=='__main__':main()
