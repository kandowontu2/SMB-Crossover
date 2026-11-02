"""Publish the tested playable successor directly, with no backup."""
import json
from pathlib import Path
import prepare_metal_storm_shots_1101_v35 as P
from nightly_patch_guard_v1 import check

def main():
 rom=P.O/'candidate.nes';digest=P.P.sha(rom)
 cpu=json.loads((P.O/'shot-CPU.json').read_text())
 capture=P.O/'native-shot-tail/capture'
 native=json.loads((capture/'result.json').read_text())
 binding=json.loads((capture/'binding.json').read_text())
 assert cpu['passed'] and native['passed'] and binding['exit_code']==0
 assert cpu['ROM_sha256']==binding['ROM_sha256']==digest
 dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
 previous=P.P.sha(dest)
 assert previous in ['d3759b333cd7c21ecac1862de8c60e35d0b65c4aadf92ff4c94d2a39fe36259a',digest]
 before=check(dest);dest.write_bytes(rom.read_bytes());after=check(dest)
 assert P.P.sha(dest)==digest
 q=dict(installed=True,ROM_sha256=digest,previous_sha256=previous,backup_created=False,before=before,after=after,
        scope='Native cold-selection Goomba shot defeat and progress toX401 with no life loss; source death/respawn successor and Tank walk fix retained. Full1-1 and expanded Metal upgrades remain pending. Downloads launch not rerun while user has that ROM open; reopen ROM to load new bytes.')
 (P.O/'delivery.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(installed=True,sha256=digest,path=str(dest),backup=False)))
if __name__=='__main__':main()
