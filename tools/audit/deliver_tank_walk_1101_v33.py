from pathlib import Path
import json,re
import prepare_tank_normal_walk_1101_v33 as P
from prepare_selected_native_packet_v1 import prepare,sha
from nightly_patch_guard_v1 import check
DEST=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')

def main():
 rom=P.O/'candidate.nes';q=json.loads((P.O/'verification.json').read_text());assert q['passed'] and sha(rom)==q['ROM_sha256']
 assert sha(DEST) in [sha(P.BASE/'candidate.nes'),sha(rom)]
 before=check(DEST);DEST.write_bytes(rom.read_bytes());after=check(DEST);assert sha(DEST)==sha(rom)
 controller=(P.O/'native/controller.lua').read_text();names=set(re.findall(r"(?:\br\(|\bL\[)'([^']+)'",controller))
 b=P.scoped_load(rom);controller='\n'.join(f'L[{json.dumps(n)}]={P.address(b,n)}' for n in names)+'\n'+controller
 out=P.O/'downloads'
 prepare(out,rom,controller,[Path(__file__),DEST,P.O/'verification.json'],expected=sha(rom),timeout=90,scope='Actual Downloads launch of walking fix, both B modes; explicit powered fixture. Always-on glow deferred to later character review.')
 ready=out/'ready.json';r=json.loads(ready.read_text());r['ROM']=str(DEST);ready.write_text(json.dumps(r,indent=2)+'\n')
 (P.O/'delivery.json').write_text(json.dumps(dict(installed=True,backup_created=False,before=before,after=after,scope=q['scope']),indent=2)+'\n')
 print('Replaced Downloads nightly without backup; Downloads playtest prepared.')
if __name__=='__main__':main()
