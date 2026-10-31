"""Freeze the byte-exact SMB2J reference and required campaign work ledger."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
S = R / 'build/smb2j-original-source-1031-v1'
A = R / 'build/smb2j-campaign-audit-1031-v1/source-audit.json'
D = R / 'docs/qa/checkpoints/2026-10-31/smb2j-campaign-reference-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    audit = json.loads(A.read_text())
    for name, digest in audit['bindings'].items():
        assert sha(name) == digest, name
    assert audit['passed'] and audit['assembled_disk_byte_exact'] and len(audit['routes']) == 58
    # These are required work items, not pass claims. References point into the
    # exact rebuilt donor source; stages/rooms and features need native checks.
    work = [
        ('game-choice', 'Character confirm opens SUPER MARIO BROS. / SUPER MARIO BROS 2J. D-pad chooses, A/Start confirms, B returns with the chosen character and alternate retained.', 'Host character_select.s; original GameMenuRoutine/StartGame', 'NOT_IMPLEMENTED'),
        ('complete-levels', 'Preserve original terrain/enemy streams, all pipe intros, bonus rooms, clouds, vines, checkpoints and exits across worlds1-9 andA-D.', 'WorldAddrOffsets/AreaDataAddrs/EnemyDataAddrs in MAIN and DATA4; DATA2/DATA3 overlays', 'SOURCE_REFERENCE_VERIFIED'),
        ('parser-metatiles', 'Translate or extend the host object/metatile protocol for every donor object without changing existing SMB1 levels or brick/contact ownership.', 'DecodeAreaData, AreaParserCore, object handler tables, MetatileGraphics_*', 'NOT_IMPLEMENTED'),
        ('poison-items', 'Visible and hidden poison-mushroom blocks, original emergence/motion and damaging pickup; regular/hidden powerup blocks and life items remain correct for each guest.', 'PoisonMushBlock, BrickQBlockMetatiles, PowerUpObjHandler, HandlePowerUpCollision', 'NOT_IMPLEMENTED'),
        ('wind', 'Original activation/deactivation, external player force, leaves and wind sound across every applicable guest controller.', 'DATA2/DATA4 BlowPlayerAround/SimulateWind/WindOn/WindOff', 'NOT_IMPLEMENTED'),
        ('pipes-plants', 'Upside-down pipes/plants, original red/green plant behavior and timing, native collision/defeat exclusions and graphics.', 'DATA2/DATA4 UpsideDownPipe_High/Low/MoveUpsideDownPiranhaP; MAIN InitPiranhaPlant/MovePiranhaPlant', 'NOT_IMPLEMENTED'),
        ('springs', 'Original red/green spring behavior, tall launch/return and camera rules with every guest, without a stale collision or offscreen softlock.', 'MAIN JumpspringHandler/GreenJS/PlayerPhysicsSub', 'NOT_IMPLEMENTED'),
        ('enemy-rules', 'Original enemy placement, movement/contact differences, underwater actor combinations, Hammer Bros., castle hazards and bosses; preserve guest attacks and Easy/Hard contact policy.', 'MAIN enemy init/movement/BG collision/defeat tables; DATA2/DATA4 additions', 'NOT_IMPLEMENTED'),
        ('warps-loops', 'Forward/backward warps, maze loops, native world/area/checkpoint advancement and timer/life rules.', 'MAIN WarpZoneNumbers, LoopCmdE, AreaDataOfsLoopback, NextArea, HalfwayPageNybbles; DATA4 ChangeHalfwayPages', 'NOT_IMPLEMENTED'),
        ('flagpole-rewards', 'Original flagpole, coin/time-dependent life/firework rewards, score display and stage-end transitions.', 'MAIN FlagpoleRoutine/GameTimerFireworks/PlayerEndLevel', 'NOT_IMPLEMENTED'),
        ('world9', 'Track completion of every required world and original warp eligibility; enter, message and loop world9 under the donor rules.', 'MAIN CompletedWorlds; DATA3 GoToWorld9/FantasyWorld9Msg/EndingDiskRoutines', 'NOT_IMPLEMENTED'),
        ('worldsA-D-save', 'Retain clear-count/star progression and original letter-world unlock behavior, replacing disk-file saving with a validated cartridge save.', 'MAIN GamesBeatenCount/GameMenuRoutine/HardWorldFlag; DATA3 UpdateGamesBeaten; SM2SAVE', 'NOT_IMPLEMENTED'),
        ('mario-luigi', 'Use the donor campaign differences where appropriate for Mario/Luigi while preserving the accepted SMB1 Luigi profile and each other guest controller.', 'MAIN PlayerPhysicsSub and SelectedPlayer paths', 'NOT_IMPLEMENTED'),
        ('presentation-audio', 'Donor level graphics/palettes, HUD world labels, ending/messages and effects. Ending FDS wavetable voice needs an explicit arrangement for available NES/MMC5 audio.', 'SM2CHAR1/2; MAIN graphics/audio; DATA3 ending and waveform driver', 'NOT_IMPLEMENTED'),
        ('options-lifecycle', 'Campaign-aware level-select cheats, reset/new-life/continue/pause/menu return, alternating characters and source cache ownership; no title demo.', 'Host menu/cheats/scene/cache APIs plus donor progression', 'NOT_IMPLEMENTED'),
        ('verification', 'Exercise all numbered stages, entrances/exits, special mechanics and bonus-world progression; validate full character compatibility rather than one Mario-only scene.', 'Exact candidate source and bounded native controller replays', 'NOT_RUN'),
    ]
    ledger = dict(request='Add SMB1 / SMB2J selection after character selection, with all SMB2J levels and additional functions.',
                  status='ACTIVE_INCOMPLETE', installed_campaign=False,
                  choices=['SUPER MARIO BROS.', 'SUPER MARIO BROS 2J'],
                  donor_sha256=audit['donor_sha256'], worlds=13, numbered_stages=52,
                  ordered_area_entries_including_pipe_intros=58,
                  current_host_feature_flag=0,
                  source_flag_limit='The optional host flag contains partial wind/flagpole/skid support, not the complete campaign.',
                  storage='Existing32KiB workRAM and PRG/CHR grants are already occupied. No larger RAM/header, CHR region or resident allocation is adopted by this reference packet.',
                  state_note='Do not allocate a persistent campaign flag at ZP EC: genuine Contra audio uses EC/ED as SOUND_TABLE_PTR. Any menu-bit sharing or new allocation requires source lifetime checks.',
                  required=[dict(id=i, behavior=b, reference=r, status=s) for i, b, r, s in work])
    D.mkdir(parents=True)
    (D / 'requirements.json').write_text(json.dumps(ledger, indent=2) + '\n', encoding='utf-8', newline='\n')
    refs = [Path(__file__), R / 'tools/audit/audit_smb2j_campaign_source_1031_v1.py', A,
            S / 'assemble.json', S / 'link.json', S / 'upstream/layout', S / 'upstream/readme.txt',
            D / 'requirements.json']
    refs += [S / 'original' / name for name in ['fdswrap.asm', 'sm2main.asm', 'sm2data2.asm', 'sm2data3.asm', 'sm2data4.asm']]
    assert all(p.suffix.lower() not in ['.fds', '.nes', '.chr', '.o', '.exe'] for p in refs)
    members = {p.relative_to(R).as_posix(): sha(p) for p in refs}
    with zipfile.ZipFile(D / 'source-reference.zip', 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in refs:
            z.write(p, p.relative_to(R).as_posix())
    with zipfile.ZipFile(D / 'source-reference.zip') as z:
        for name, digest in members.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest
    (D / 'source-members.json').write_text(json.dumps(members, indent=2) + '\n', encoding='utf-8', newline='\n')
    manifest = dict(passed=True, source_reference_only=True, installed=False,
                    donor_sha256=audit['donor_sha256'], rebuilt_sha256=audit['donor_sha256'],
                    byte_comparison=65500, worlds=13, numbered_stages=52, area_entries=58,
                    source_credit=audit['source_credit'], source_repository=audit['upstream'],
                    source_commit=audit['upstream_commit'], requirements_sha256=sha(D / 'requirements.json'),
                    archive_sha256=sha(D / 'source-reference.zip'), archive_members=len(members),
                    archive_bytes=(D / 'source-reference.zip').stat().st_size,
                    bindings={**audit['bindings'], **{str(p.resolve()): sha(p) for p in refs}},
                    goal_complete=False)
    (D / 'handoff.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    (D / 'README.md').write_text(
        '# SMB2J campaign reference\n\n'
        'The unmodified ca65 disassembly reproduces every byte of the local65,500-byte '
        'Japanese FDS disk (ff8afb9a). The table/stream audit inventories13 worlds and58 '
        'ordered area entries, including pipe intros, for52 numbered stages. World9 '
        'retains part of the preceding DATA2 overlay. Source is credited to doppelganger '
        'and threecreepio. The archive contains source, recipes and metadata, without ROMs '
        'or CHR files.\n\n'
        'This is a verified reference and required-work ledger. The game-choice screen, '
        'campaign engine, save conversion, complete bonus-area closure and native checks '
        'are unfinished. No installed build changes are made by this packet.\n',
        encoding='utf-8', newline='\n')
    owned = [str(Path(__file__).relative_to(R)).replace('\\', '/'),
             'tools/audit/audit_smb2j_campaign_source_1031_v1.py',
             'docs/qa/continuation-2026-10-31-ready74-scroll-chr.json']
    owned += [p.relative_to(R).as_posix() for p in D.iterdir() if p.is_file()]
    (D / 'owned-files.json').write_text(json.dumps(dict(files=owned + [str((D / 'owned-files.json').relative_to(R)).replace('\\', '/')]), indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(source_reference=True, installed=False, packet=str(D),
                          handoff_sha256=sha(D / 'handoff.json'), archive_bytes=manifest['archive_bytes'])))


if __name__ == '__main__':
    main()
