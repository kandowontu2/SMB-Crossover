"""Install exact64 WIP after the two bounded Benj native checks."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
J=R/'build/benj-menu-unlocked-1030-v3/joint'
H=J.parent/'handoff.json'
N=R/'build/benj-native-1030-v1'
D=R/'docs/qa/checkpoints/2026-10-30/ready64-native-unlocks'
RECEIPT=R/'docs/qa/functional-roster-ready64-2026-10-30.json'
NEW='98048319d382e7a5c4e7186704b6e3b939eda4eec9bdd6e098c402cbd30799b6'
OLD='dfdb194ac73438ae8deb05b5fc93f241b1109d45a84b3ad333d0e632008d7fc7'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
 assert not D.exists()and not RECEIPT.exists()
 assert sha(H)=='4c3ae5f151776f374494fb9f553bc0a2d3b7491e66ff0c1ef65d8926cf3741ed'
 h=read(H);assert h['source']and h['candidate']==NEW and len(h['bindings'])==1316
 for p,s in h['bindings'].items():assert sha(p)==s,p
 assert sha(J/'candidate.nes')==NEW
 menu=read(J.parent/'all-menu-controls.json');assert menu['passed']and menu['current_profiles']==83
 paths={Path(__file__).resolve(),N/'prepared.json'};outcomes=[]
 for name,variant,frames,ready in [('toad',5,548,'ff975a0e117fc2e94be5ac14d07dec1e464eae1dfba7e41d6b9f17b8897b000e'),('peach',6,569,'3693ad3848287bf93ea3a2b1ee4d4b3b55754b72c35358d6cf212f52b1ceb329')]:
  p=N/name;assert sha(p/'ready.json')==ready
  d=read(p/'capture/result.json');b=read(p/'capture/binding.json')
  assert b['exit_code']==0 and b['ROM_sha256']==NEW and d['ROM_sha256']==NEW and d['passed']
  for f,s in b['bindings'].items():assert sha(f)==s,f
  assert d['variant']==variant and d['frames']==frames and d['main_updates']==180
  assert d['source_Main']==d['source_movement']==180 and d['source_fresh']==1
  assert d['jumped']and d['landed']and d['vector_guards']==360 and d['body_P0_source_exact']
  assert len(list((p/'capture').glob('*.png')))==4
  assert len(list(p.rglob('*')))<=64
  paths|={f for f in p.rglob('*')if f.is_file()}
  outcomes.append(dict(identity='SMB1 '+name,variant=variant,passed=True,physical_frames=frames,
     controlled_Main_updates=180,actual_UI_DMA_checks=d['actual_UI_DMA_checks'],
     walked=d['walked'],rise=d['rise'],jumped=True,landed=True,vector_guards=360,
     lag_NMIs=d['timing']['lag_nmi'],root_reviewed_PPU_PNGs=4,result_sha256=sha(p/'capture/result.json')))
 assert all(f.suffix.lower()in['.py','.lua','.json','.csv','.log','.png']for f in paths)
 assert sum(p.stat().st_size for p in paths)<4*1024*1024
 D.mkdir(parents=True)
 archive=D/'native-results.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(paths):z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(archive)as z:
  for p in paths:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
 save(D/'manifest.json',dict(candidate=NEW,source_handoff_sha256=sha(H),native=outcomes,
      archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
      members={p.relative_to(R).as_posix():sha(p)for p in sorted(paths)},
      scope='Two exact-hash cold/menu/lives/basic movement smokes. No full1-1, every-powerup or global FPS claim.'))
 (D/'README.md').write_text('Exact98048319 passes both root-executed bounded native runs, with8 whole PPU PNGs visually reviewed. Each run includes180 controlled Main updates, original source body palette roles, actual DMA/physicalCHR/visible pixels, jumping/landing and360 real NMI/IRQ vector restores. No debug RAM writes, cheats, video or per-frame capture forest. The inherited result field named health is PlayerStatus for these native Mario alternates; zero denotes small form, not zero HP.\n\nThe earlier1316-binding source checkpoint and its native-pending statements are preserved unchanged. This later result qualifies a labelled64-character unlock WIP, not complete campaign/powerup coverage. Both new HUDs still say MARIO. Special donor float enemy/ceiling/platform consumers and fire/star/area palette progression remain incomplete. Earlier FF shadows/damage/render-timing issues remain open. The user explicitly prioritized playable unlocks over polish.\n',encoding='utf-8',newline='\n')
 downloads=Path.home()/'Downloads'
 latest=downloads/'SMB-Crossover-Latest-WIP-MMC5.nes'
 version=downloads/'SMB-Crossover-2026-10-30-Ready64-WIP-MMC5.nes'
 backup=downloads/'SMB-Crossover-Before-Ready64-dfdb194a-MMC5.nes'
 assert sha(latest)==OLD and not version.exists()and not backup.exists()
 shutil.copy2(latest,backup);assert sha(backup)==OLD
 shutil.copy2(J/'candidate.nes',version);assert sha(version)==NEW
 shutil.copy2(version,latest);assert sha(latest)==NEW
 receipt=dict(date='2026-10-30',status='INSTALLED_UNLOCK64_WIP_WITH_KNOWN_BUGS',installed=True,
     ROM_sha256=NEW,source_handoff_sha256=sha(H),verified_source_bindings=1316,
     latest=str(latest),versioned=str(version),backup=str(backup),previous_sha256=OLD,
     menu_slots=32,individual_identities=82,playable=64,pending_individual_identities=18,
     generic_pending_family_placeholders=['Battletoads'],newly_unlocked=['SMB1 Toad','SMB1 Peach'],
     menu_access='Select on Mario; cycle Mario/Luigi/Toad/Peach/Super Maaa/Kamikaze/Celeste.',
     bounded_native=outcomes,source_all_existing_profiles_preserved=81,source_current_profiles=83,
     source_Start_A_cases=664,full_campaign_pass=False,every_powerup_pass=False,constant_60Hz_qualified=False,
     known_open=['Both Benj HUDs still say MARIO.','Donor float contact refinements and fire/star/area-specific palette progression partial.',
                 'Earlier FF shadow/damage and retained Fighter render-timing failure remain unfixed.',
                 'Remaining character integrations and broad campaign/powerup coverage remain.'],
     instruction='Reopen this ROM and start fresh; do not load older code/state snapshots.',
     native_manifest_sha256=sha(D/'manifest.json'))
 save(RECEIPT,receipt)
 shutil.copy2(N/'toad/capture/selected.png',R/'docs/images/character-select.png')
 print(json.dumps(dict(installed=str(latest),versioned=str(version),candidate=NEW,playable=64,
       native_archive_bytes=archive.stat().st_size,native_archive_members=len(paths),receipt=str(RECEIPT)),indent=2))


if __name__=='__main__':main()
