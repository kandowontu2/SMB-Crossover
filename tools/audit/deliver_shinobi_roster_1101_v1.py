"""Install the full-route-qualified Shinobi successor without backup copies."""
import json,re
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from nightly_patch_guard_v1 import check
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
O=R/'build/roster-combined-1101-v1'
def main(arthur=False):
 global O
 if arthur:O=R/'build/roster-combined-1101-v3'
 rom=O/'candidate.nes';digest=sha(rom)
 expected='c3dd03031faaef7faf12f865b7a5cdfd363835e2179eca22fe2eef8180553157' if arthur else '933c0650ea5c1db0e613836be7ba9d07c67a25142276fe4efa6874f1063e04df'
 assert digest==expected
 jobs=['arthur-route','arthur-pit','shinobi-smoke','metal-idle'] if arthur else ['native','shinobi-full','metal-route']
 for name in jobs:
  c=O/name/'capture';r=json.loads((c/'result.json').read_text());b=json.loads((c/'binding.json').read_text())
  assert r['passed']and b['exit_code']==0 and b['ROM_sha256']==digest,(name,r)
 dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');previous=sha(dest)
 prior='933c0650ea5c1db0e613836be7ba9d07c67a25142276fe4efa6874f1063e04df' if arthur else '27dee145eead745dfe94cc6e4734a88fdd03811c7f7c3c9d1ee55e54d3057318'
 assert previous in [prior,digest]
 before=check(dest);dest.write_bytes(rom.read_bytes());after=check(dest);assert sha(dest)==digest
 q=dict(installed=True,ROM_sha256=digest,previous_sha256=previous,backup_created=False,before=before,after=after,downloads_launch_verified=False,
  scope=('Arthur authentication cost reduced, scrolling contract repaired, pit death reaches next life. Exact cumulative candidate full1-1→active1-2 lives2→2/nohelpers, realpitdeath2→1/resumedcontrol, Shinobi smoke/OAM and Metalidle/walk pass. Previously qualified Shinobi/Metal changes preserved byte-for-byte. ' if arthur else 'Shinobi source projectile visible-body contacts and OAM reservation repaired; controller-only1-1 throughactive1-2 no life lost/no helpers. Existing Metal Storm1-1 regression passed. Arthur private fixes excluded. ')+'Original Shinobi body hitbox/audio/melee/magic followup remains. No all-roster or all-powerup completion claim.')
 (O/'delivery.json').write_text(json.dumps(q,indent=2)+'\n')
 ref=O/('shinobi-smoke' if arthur else 'native')/'controller.lua';t=ref.read_text();b=scoped_load(rom)
 names=set(re.findall(r"\br\('([^']+)'",t))|set(re.findall(r'\bL\.(\w+)',t))|{'RgOamFirst','RgOamUsed','RgOamRotation','CurrentOAMOffset'}
 # Iterated names in the read-only graphics dump also need explicit addresses
 # because the actual Downloads path has no adjacent debugger symbols.
 names|={'CurrentCHRBank','X5ChrMode','SsChrActive','X5WideChrActive','ReloadCHRBank','Mirror_PPUCTRL','CurrentBank','CurrentBankC'}
 t='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}'for n in sorted(names))+'\n'+t
 prepare(O/'downloads',rom,t,[Path(__file__),ref,dest],expected=digest,timeout=90,scope='Actual Downloads cold Shinobi Select/Start/idle/walk with every native OAM-count/rotation write aligned; explicitsymboladdresses, three screenshots, no RAM writes or backup.')
 p=O/'downloads/ready.json';q=json.loads(p.read_text());q['ROM']=str(dest);p.write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(installed=True,ROM_sha256=digest,backup=False,downloads_launch_pending=True)))
if __name__=='__main__':
 import sys
 main('--arthur' in sys.argv)
