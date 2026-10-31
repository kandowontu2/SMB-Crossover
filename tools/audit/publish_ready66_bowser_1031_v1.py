"""Install the exact source-built, natively reviewed Bowser WIP successor."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/bowser-playable-jump-v1';J=O/'joint'
N=R/'build/bowser-playable-native-1031-v1'
S=R/'docs/qa/checkpoints/2026-10-31/bowser-playable-contact-jump-source'
D=R/'docs/qa/checkpoints/2026-10-31/bowser-playable-native'
OLD='f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78'
NEW='c6635815711a624a02c4337cd9f1830ca9c43b14a824f2ea51963f796ad98c2a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert not D.exists() and sha(J/'candidate.nes')==NEW
    h=read(O/'handoff.json')
    assert sha(O/'handoff.json')=='95ec180970aa29e654694c7b19f0531cd1e4f1fa060cf070edb80379af8ab544'
    assert h['candidate']==NEW and len(h['bindings'])==4599
    for p,digest in h['bindings'].items():assert sha(p)==digest,p
    with zipfile.ZipFile(S/'source-only.zip') as z:
        assert len(z.namelist())==4260
        for name in z.namelist():
            assert hashlib.sha256(z.read(name)).hexdigest()==h['bindings'][str(R/name)],name
    freeze=read(S/'freeze-proof.json');assert freeze['passed'] and freeze['candidate']==NEW
    for entry in freeze['controls']:
        assert sha(entry['path'])==entry['sha256']
        assert read(entry['path'])['passed']
    route=read(S/'source-route-summary.json')
    assert route['route_clear'] and route['source_CPU'] and not route['native']
    assert route['updates']==4326 and route['HP']==2 and route['next_area_Main']==25
    native=[];files={Path(__file__),N/'prepared.json'}
    for name,variant,rise in [('smb3',0,99),('smb1',8,80)]:
        p=N/name;result=read(p/'capture/result.json');bound=read(p/'capture/binding.json')
        assert result['passed'] and result['ROM_sha256']==bound['ROM_sha256']==NEW
        assert bound['exit_code']==0
        for f,digest in bound['bindings'].items():assert sha(f)==digest,f
        assert result['variant']==variant and result['rise']==rise
        assert result['main_updates']==result['source_Main']==result['source_movement']==result['source_EndFrame']==148
        assert result['vector_guards']==444 and result['source_fire_calls']>=1
        assert result['jumped'] and result['landed'] and result['body_P0_source_exact']
        pngs=sorted((p/'capture').glob('*.png'));assert len(pngs)==5
        files.update(q for q in p.rglob('*') if q.is_file())
        native.append(dict(identity=name,variant=variant,passed=True,complete_Main=148,
            physical_gameplay_frames=222,vector_restores=444,source_fire_calls=result['source_fire_calls'],
            rise=rise,HP=result['HP'],timing=result['timing'],
            root_reviewed_PNGs={q.name:sha(q) for q in pngs},result_sha256=sha(p/'capture/result.json')))
    assert all(p.suffix.lower() in ['.py','.lua','.json','.csv','.log','.png'] for p in files)
    assert sum(p.stat().st_size for p in files)<8*1024*1024
    D.mkdir(parents=True)
    archive=D/'native-results.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    manifest=dict(output_sha256=NEW,base_sha256=OLD,source_handoff_sha256=sha(O/'handoff.json'),
        source_bindings=4599,native_runs=native,native=True,
        archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        members={p.relative_to(R).as_posix():sha(p) for p in sorted(files)})
    save(D/'manifest.json',manifest)
    (D/'README.md').write_text(
        'Bowser WIP admission c6635815: both SMB3 and SMB1 versions pass root-run, controller-only '
        'cold/menu/lives/native movement and breath checks. Each completes148 Main updates in222 '
        'physical gameplay frames and444 actual interrupt restore checks. Root reviewed all10 PNGs; '
        'the two entered PNGs are early black transitions, while fire/endpoint show the rendered player. '
        'Actual source palettes, full body DMA parts and physical CHR are checked. Lives portraits now '
        'clear WORLD1-1 text. No videos or per-frame image forests were created.\n\n'
        'The real tier0-to-KillPlayer error is fixed: service6 returns HP, allowing native ForceInjury '
        'to call the owned injury handler. Protection uses native8 intervals and expires naturally '
        'after149 measured Main updates. SMB1 Bowser has an explicit playable jump adapter (-3 '
        'instead of the NPC original -2), retaining the original falling/gravity/fraction code. Its '
        'source CPU route clears actual32/48/64/64px pipes, all gaps/stairs and enters1-2 withHP2. '
        'That is a CPU route, not a native full-level claim. The old failures remain preserved.\n\n'
        'This installs a66-identity playable WIP, not a full-campaign/every-powerup/60Hz qualification. '
        'Lag remains; extended boss moves and original SMB3 audio remain incomplete. The inherited '
        'FF419 rendering deadline remains open. Peach normal colors remain163027. Reopen the ROM '
        'and start fresh.\n',encoding='utf-8',newline='\n')
    downloads=Path.home()/'Downloads'
    latest=downloads/'SMB-Crossover-Latest-WIP-MMC5.nes'
    version=downloads/'SMB-Crossover-2026-10-31-Ready66-Bowser-MMC5.nes'
    backup=downloads/'SMB-Crossover-Before-Bowser-f56e55cd-MMC5.nes'
    assert sha(latest)==OLD and not version.exists() and not backup.exists()
    shutil.copy2(latest,backup);assert sha(backup)==OLD
    shutil.copy2(J/'candidate.nes',version);assert sha(version)==NEW
    shutil.copy2(version,latest);assert sha(latest)==NEW
    receipt=dict(date='2026-10-31',status='INSTALLED_READY66_BOWSER_PLAYABLE_WIP',
        installed=True,passed=True,rom_sha256=NEW,ROM_sha256=NEW,previous_sha256=OLD,
        latest=str(latest),versioned=str(version),backup=str(backup),
        playable=66,individual_identities=82,menu_slots=32,
        source_handoff_sha256=sha(O/'handoff.json'),verified_source_bindings=4599,
        checks=[dict(name='source closure and4260-member archive match exact candidate',passed=True),
                dict(name='actual injury caller, natural protection expiry, source fire and lifecycle controls',passed=True),
                dict(name='SMB1 Bowser source CPU1-1 to1-2 route with actual pipes',passed=True),
                dict(name='both exact-hash bounded native cold/menu/lives/movement/fire smokes',passed=True),
                dict(name='all10 selected native PNGs visually reviewed',passed=True),
                dict(name='backup and both installed copies match SHA256',passed=True)],
        bounded_native=native,source_CPU_route=route,
        native_full1_1=False,full_campaign_pass=False,every_powerup_pass=False,constant60Hz=False,
        incomplete=['Lag','Extended boss attacks/original SMB3 audio','Inherited FF419 render deadline',
                    'Whole roster1-1 and every-powerup audit'],
        native_manifest_sha256=sha(D/'manifest.json'),instruction='Reopen the latest ROM and start fresh.')
    save(R/'docs/qa/functional-roster-ready66-bowser-2026-10-31.json',receipt)
    print(json.dumps(dict(installed=str(latest),versioned=str(version),candidate=NEW,
        playable=66,native_archive_bytes=archive.stat().st_size,native_members=len(files)),indent=2))


if __name__=='__main__':main()
