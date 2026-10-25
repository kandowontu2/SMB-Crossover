"""One-shot private adoption; retain all release/every-item limitations."""
from pathlib import Path
import datetime,gzip,hashlib,json,shutil
from archive_workspace_hz import inventory
ROOT=Path(__file__).resolve().parents[2]
EXTERNAL=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-vram-status-ps')
LIVE=EXTERNAL/'candidate-v4';PACKET=EXTERNAL/'source-packet-final-v4c'
PARENT=ROOT/'build/checkpoints/grant-grip-pm'
FINAL=ROOT/'build/checkpoints/contact-pause-ps';QA=ROOT/'build/verification/contact-pause-ps'
EXPECTED='646baef6cbcbe9ebc3c0a57c182592b3e777970c13b9c89eda6765f446915bb6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def main():
    assert not FINAL.exists() and not (QA/'proof.json').exists(),'Never repeat a successful adoption'
    QA.mkdir(parents=True,exist_ok=True);checks={}
    def check(relative):
        path=EXTERNAL/relative;q=json.loads(path.read_text())
        assert q['passed'] and q['ROM_sha256']==EXPECTED,relative
        checks[relative]=record(path);return q
    assert sha(LIVE/'candidate.nes')==EXPECTED
    cpu=check('cpu-v4/proof.json');assert cpu['numeric_cases']==9216 and cpu['unchanged_valid_cases']==1844
    path=EXTERNAL/'contact-cpu-v4/proof.json';contact=json.loads(path.read_text())
    assert contact['passed'] and contact['components']['candidate']['ROM_sha256']==EXPECTED
    assert contact['components']['candidate']['origin_cases']==97280
    assert all(contact['components']['candidate'][n]==0 for n in ['origin_wrong','inhale_body_wrong','ground_enemy_displaced','mike_head_wrong'])
    checks['contact-cpu-v4/proof.json']=record(path)
    cache=check('hud-cache-v4/proof.json');assert cache['native_packet_unchanged'] and cache['delayed_field_refreshes']==5
    rpg=check('rpg-cpu-v4/proof.json');assert rpg['threshold_sets']==3584 and rpg['cancel_boundary_cases']==17920
    qualification=check('qualification-final-v4.json')
    assert qualification['complete'] and len(qualification['routes'])==10 and all(r['passed']for r in qualification['routes'])
    total_frames=0
    for row in qualification['routes']:
        key=row['identity']+'-'+row['mode'];folder=Path(row['replay_folder']).relative_to(EXTERNAL).as_posix()
        replay=check(folder+'/proof.json')
        assert replay['complete'] and replay['selected_cases']==1
        capture=check(folder+'/direct-'+key+'/proof.json')
        review=check(folder+'/review-'+key+'/proof.json')
        assert capture['fixed_inputs_and_trace_exact'] and capture['actual_PPU_frame_ids_complete'] and capture['raw_gzip_roundtrip_exact']
        assert capture['result']['cleared'] and capture['result']['deaths']==0
        assert review['strict_route']['visible_scroll_scanline31_only']
        assert review['strict_route']['body_chr_mismatches']==0
        total_frames+=capture['direct_frames']
    entries_path=EXTERNAL/'qualification-v4/entries/results.json';entries=json.loads(entries_path.read_text())
    assert entries['rom_sha256']==EXPECTED and entries['identities']==len(entries['results'])==37
    assert all(r['exit']==0 for r in entries['results'].values());checks['entries']=record(entries_path)
    for name,row in entries['results'].items():
        out=EXTERNAL/'qualification-v4/entries'/name.lower().replace(' ','-')
        assert sha(out/'entry.lua')==row['script_sha256']
        q=json.loads((out/'build/verification/proof.json').read_text())
        assert q['passed'] and q['name']==name and q['visibleFrames']>60
        checks['entry-'+name]=record(out/'build/verification/proof.json')
    heads=check('head-matrix-v4/progress.json')
    assert heads['complete'] and len(heads['runs'])==66 and len(heads['excluded'])==4 and all(r['exit']==0 for r in heads['runs'])
    guards=check('pause-guards-v4-valid-camera/progress.json');assert guards['complete'] and len(guards['cases'])==3
    assert all(r['interrupts']['observed_minimum_NMI_SP']>=122 for r in guards['cases'])
    native_contacts=json.loads((EXTERNAL/'qualification-v4/contacts/results.json').read_text())
    assert set(native_contacts)=={'kirby','mike','sypha'}
    assert all(v['exit']==0 and v['ROM_sha256']==EXPECTED for v in native_contacts.values())
    for name in native_contacts:
        path=EXTERNAL/'qualification-v4/contacts'/name/'proof.json';assert json.loads(path.read_text())['passed'];checks['native-'+name]=record(path)
    pause=EXTERNAL/'qualification-v4/pause/proof.json';q=json.loads(pause.read_text())
    assert q['passed'] and q['opens']==q['exact_world_restores']==4;checks['pause']=record(pause)
    visual=check('visual-review-v4.json');assert visual['root_agent_visual_review']
    assert all(sha(Path(n))==h for n,h in visual['reviewed_images'].items())
    packet=json.loads((PACKET/'packet.json').read_text())
    assert packet['passed'] and packet['ROM_sha256']==EXPECTED and packet['source_only_roundtrip_exact']
    assert sha(PACKET/'source.zip')==packet['source_zip_sha256'] and sha(PACKET/'expanded.nes')==EXPECTED
    assert gzip.decompress((PACKET/'candidate.dbg.gz').read_bytes())==(LIVE/'candidate.dbg').read_bytes()
    parent=json.loads((PARENT/'manifest.json').read_text());previous=json.loads((ROOT/'build/verification/grant-grip-pm/proof.json').read_text())
    assert sha(PARENT/'candidate.nes')==parent['rom_sha256']==packet['parent_ROM_sha256']
    assert sha(PARENT/'source.zip')==parent['source_zip_sha256']
    changes,hashes=packet['changes'],packet['source_files']
    for n,h in hashes.items():
        assert sha(PACKET/'source'/n)==h
        if n in changes:
            before=changes[n]['before'];assert not (ROOT/n).exists() if before is None else sha(ROOT/n)==before,n
        else:assert sha(ROOT/n)==h,n
    public={n:sha(ROOT/'build'/n)for n in previous['unchanged_public_ROMs']}
    assert public==previous['unchanged_public_ROMs']
    assert {m:packet['builds'][m]for m in ['mmc3','mmc5']}==previous['ordinary_flag_off_hashes']
    required=sum((PACKET/n).stat().st_size for n in ['source.zip','candidate.dbg.gz'])
    required+=sum((LIVE/('candidate'+ext)).stat().st_size for ext in ['.nes','.lbl','.map'])+1_000_000
    assert sum(n for _,n,_ in inventory(ROOT,skip_reparse=True))+required<30_000_000_000
    (QA/'adoption-plan.json').write_text(json.dumps(dict(ROM_sha256=EXPECTED,changes=changes,checks=checks,planned_checkpoint_bytes_with_margin=required),indent=2)+'\n')
    shutil.copy2(Path(__file__),QA/'adoption-driver.py')
    for n,row in changes.items():
        if row['before']is not None:
            backup=QA/'before'/n;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,backup);assert sha(backup)==row['before']
        (ROOT/n).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PACKET/'source'/n,ROOT/n);assert sha(ROOT/n)==row['after']
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    limits=[
      'Private combined contact, HUD-buffer and Zelda II pause repair; full goal remains active.',
      'Ten current-hash strict independent playthrough pairs cover Kirby, Meta Knight, Mike, Sypha and Zelda II Link in both modes. Other identities have entry/head coverage here, not new full-route certification.',
      'Seeded native interactions, CPU boundaries, source RPG prices, NMI/SMC guards and sampled real PPU images qualify this repair. Human whole-route/every-frame inspection remains open.',
      'Measured linked unchanged Zelda II HUD drops1777to138cycles; native route lag remains and constant60Hz is not established.',
      'Every-character/every-powerup emergence, collection, graphics, SFX, use and expiry, remaining roster routes/source music/art and oversizedMMC3 parity remain open.',
      'Ordinary flag-off targets, published ROMs and player guide remain unchanged. Start a fresh game with the private candidate; old states can contain incompatible RAM/code.'
    ]
    proof=dict(passed=True,goal_complete=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),ROM_SHA256=EXPECTED,parent='grant-grip-pm',
      game_changes=changes,checks=checks,source_packet=record(PACKET/'packet.json'),source_only_rebuild_exact=True,
      ordinary_flag_off_hashes={m:packet['builds'][m]for m in ['mmc3','mmc5']},unchanged_public_ROMs=public,
      current_strict_pairs=10,current_retained_physical_frames=total_frames,cold_entries=37,native_head_cases=66,
      driver_sha256=sha(QA/'adoption-driver.py'),limitations=limits)
    (QA/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');FINAL.mkdir()
    for n in ['source.zip','candidate.dbg.gz']:shutil.copy2(PACKET/n,FINAL/n)
    for ext in ['.nes','.lbl','.map']:shutil.copy2(LIVE/('candidate'+ext),FINAL/('candidate'+ext))
    manifest=dict(utc=proof['utc'],status='PRIVATE_CONTACT_PAUSE_VRAM_REPAIR_WITH_OPEN_ROSTER_WORK',identities=37,parent_checkpoint='grant-grip-pm',
      rom_sha256=EXPECTED,source_files=hashes,source_zip_sha256=sha(FINAL/'source.zip'),source_bundle_rebuild=dict(exact=True,stage=str(PACKET)),
      evidence=record(QA/'proof.json'),limitations=limits,goal_complete=False)
    (FINAL/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    assert all(sha(ROOT/'build'/n)==h for n,h in public.items())
    used=sum(n for _,n,_ in inventory(ROOT,skip_reparse=True));assert used<30_000_000_000
    result=dict(checkpoint=str(FINAL),ROM_SHA256=EXPECTED,source_zip_sha256=manifest['source_zip_sha256'],source_files=len(hashes),workspace_bytes=used,goal_complete=False)
    (QA/'checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
