import json
from pathlib import Path
import prepare_metal_storm_decline_1101_v40 as P
from nightly_patch_guard_v1 import check

def main():
 rom=P.O/'candidate.nes';digest=P.P.sha(rom)
 q=json.loads((P.O/'CPU.json').read_text());assert q['passed'] and q['ROM_sha256']==digest
 for name in ['idle','route']:
  c=P.O/name/'capture';result=json.loads((c/'result.json').read_text());binding=json.loads((c/'binding.json').read_text())
  assert result['passed'] and binding['exit_code']==0 and binding['ROM_sha256']==digest
 dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
 previous=P.P.sha(dest);assert previous in [P.P.sha(P.BASE/'candidate.nes'),digest]
 before=check(dest);dest.write_bytes(rom.read_bytes());after=check(dest);assert P.P.sha(dest)==digest
 receipt=dict(installed=True,ROM_sha256=digest,previous_sha256=previous,backup_created=False,before=before,after=after,scope='1584 equivalence cases; unchanged native idle/walk and full1-1-to-active1-2 controller pass. CPU cost reduced about7%; update throughput still around40fps. Actual Downloads launch context not retested by this delivery.')
 (P.O/'delivery.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(installed=True,sha256=digest,backup=False)))
if __name__=='__main__':main()
