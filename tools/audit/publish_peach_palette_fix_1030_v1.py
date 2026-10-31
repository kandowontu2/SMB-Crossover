"""Publish the exact source-built palette correction after native review."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/peach-palette-fix-1030-v1';J=O/'joint'
N=R/'build/peach-palette-native-1030-v1'
D=R/'docs/qa/checkpoints/2026-10-30/peach-palette-correction-native'
OLD='98048319d382e7a5c4e7186704b6e3b939eda4eec9bdd6e098c402cbd30799b6'
NEW='f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert not D.exists()
    h=read(O/'handoff.json');assert h['candidate']==NEW and sha(J/'candidate.nes')==NEW
    for p,s in h['bindings'].items():assert sha(p)==s,p
    outcomes=[];files={Path(__file__),N/'prepared.json'}
    for name,variant in [('toad',5),('peach',6)]:
        p=N/name;d=read(p/'capture/result.json');b=read(p/'capture/binding.json')
        assert d['passed']and d['ROM_sha256']==NEW and b['exit_code']==0 and b['ROM_sha256']==NEW
        for f,s in b['bindings'].items():assert sha(f)==s,f
        assert d['variant']==variant and d['main_updates']==d['source_Main']==d['source_movement']==180
        assert d['jumped']and d['landed']and d['body_P0_source_exact']and d['vector_guards']==360
        assert d['timing']['lag_nmi']==0
        assert len(list((p/'capture').glob('*.png')))==4
        files|={q for q in p.rglob('*')if q.is_file()}
        outcomes.append(dict(identity=name,variant=variant,passed=True,frames=d['frames'],
            controlled_Main_updates=180,vector_guards=360,lag_NMIs=0,root_reviewed_PNGs=4,
            actual_UI_DMA_checks=d['actual_UI_DMA_checks'],result_sha256=sha(p/'capture/result.json')))
    assert all(p.suffix.lower()in['.py','.lua','.json','.csv','.log','.png']for p in files)
    assert sum(p.stat().st_size for p in files)<4*1024*1024
    D.mkdir(parents=True)
    archive=D/'native-results.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    save(D/'manifest.json',dict(candidate=NEW,source_handoff_sha256=sha(O/'handoff.json'),
        source_bindings=len(h['bindings']),native=outcomes,archive_sha256=sha(archive),
        archive_bytes=archive.stat().st_size,members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)}))
    (D/'README.md').write_text('Peach palette correction f56e55cd: two root-run controller-only native smokes pass,180 controlled Main updates and360 real interrupt restore checks each. Root reviewed all8 full-frame PNGs. Actual Peach P0 is163027 on selection/lives/gameplay, matching the genuine donor normalP2 consumer. The earlier98048319 tests passed an incorrect expectedP3 row0F3617; those historical receipts remain unchanged and are superseded on palette authenticity.\n\nOnly3 ROM bytes changed; no entry moved and noCHR changed. This remains a64-character WIP: normal palette correction does not qualify original fire/star/area progression, the full campaign, or every powerup. Both new HUDs still say MARIO. No video or per-frame captures were created.\n',encoding='utf-8',newline='\n')
    downloads=Path.home()/'Downloads'
    latest=downloads/'SMB-Crossover-Latest-WIP-MMC5.nes'
    version=downloads/'SMB-Crossover-2026-10-30-Ready64-Peach-Fix-MMC5.nes'
    backup=downloads/'SMB-Crossover-Before-Peach-Fix-98048319-MMC5.nes'
    assert sha(latest)==OLD and not version.exists()and not backup.exists()
    shutil.copy2(latest,backup);assert sha(backup)==OLD
    shutil.copy2(J/'candidate.nes',version);assert sha(version)==NEW
    shutil.copy2(version,latest);assert sha(latest)==NEW
    receipt=dict(date='2026-10-30',status='INSTALLED_READY64_PEACH_NORMAL_PALETTE_CORRECTION',
        installed=True,ROM_sha256=NEW,previous_sha256=OLD,latest=str(latest),versioned=str(version),backup=str(backup),
        source_handoff_sha256=sha(O/'handoff.json'),verified_source_bindings=len(h['bindings']),
        changed_ROM_bytes=3,changed_offsets=h['delta_offsets'],all_labels_and_CHR_preserved=True,
        playable=64,individual_identities=82,menu_slots=32,normal_palette='163027',
        old_incorrect_palette='0f3617',bounded_native=outcomes,full_campaign_pass=False,
        every_powerup_pass=False,fire_star_area_progression_complete=False,
        native_manifest_sha256=sha(D/'manifest.json'),instruction='Reopen the latest ROM and start fresh.')
    save(R/'docs/qa/functional-roster-ready64-peach-fix-2026-10-30.json',receipt)
    print(json.dumps(dict(installed=str(latest),versioned=str(version),candidate=NEW,
        native_archive_bytes=archive.stat().st_size,native_archive_members=len(files)),indent=2))


if __name__=='__main__':main()
