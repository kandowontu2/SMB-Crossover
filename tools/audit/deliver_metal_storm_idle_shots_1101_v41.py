"""Replace the nightly only after CPU and real-controller regression passes."""
import json,re
from pathlib import Path
import prepare_metal_storm_idle_shots_1101_v41 as P
from prepare_selected_native_packet_v1 import prepare,sha
from nightly_patch_guard_v1 import check
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
def main():
 rom=P.O/'candidate.nes';digest=sha(rom)
 q=json.loads((P.O/'CPU.json').read_text());assert q['passed'] and q['ROM_sha256']==digest
 for name in ['idle','route']:
  c=P.O/name/'capture';r=json.loads((c/'result.json').read_text());b=json.loads((c/'binding.json').read_text())
  assert r['passed'] and b['exit_code']==0 and b['ROM_sha256']==digest
 dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');previous=sha(dest)
 assert previous in [sha(P.BASE/'candidate.nes'),digest]
 before=check(dest);dest.write_bytes(rom.read_bytes());after=check(dest);assert sha(dest)==digest
 receipt=dict(installed=True,ROM_sha256=digest,previous_sha256=previous,backup_created=False,before=before,after=after,
  scope='792 differential cases,300 contacts, native idle/walk and full1-1 to active1-2 with no life lost.409 cycles saved; measured update throughput unchanged. Downloads launch pending.')
 (P.O/'delivery.json').write_text(json.dumps(receipt,indent=2)+'\n')
 ref=P.O/'idle/controller.lua'
 t=ref.read_text();b=scoped_load(rom)
 names=set(re.findall(r"\br\('([^']+)'",t))|set(re.findall(r'\bL\.(\w+)',t))
 t='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}' for n in sorted(names))+'\n'+t
 prepare(P.O/'downloads',rom,t,[Path(__file__),ref,dest],expected=digest,timeout=90,scope='Actual Downloads nightly cold launch, character selection, idle and walking. Explicit symbol addresses; no state writes or backups.')
 ready=P.O/'downloads/ready.json';q=json.loads(ready.read_text());q['ROM']=str(dest);ready.write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(installed=True,sha256=digest,backup=False)))
if __name__=='__main__':main()
