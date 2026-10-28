"""Freeze the qualified85af Contra repair without copying raw capture streams."""
from pathlib import Path
import gzip
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
H = '85afad507fa7abac29603c65bf5f7d9cadd224a24fd13ff2fd22f541b65729aa'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    cp = R / 'docs/qa/checkpoints/2026-10-28/bill-hud-inert-adoption'
    source = cp / 'source-adoption.json'
    source_receipt = json.loads(source.read_text())
    assert source_receipt['passed']
    assert sha(R / 'build/smb-crossover-mmc5-expanded.nes') == H
    assert sha(R / 'build/bill-hud-inert-canonical.nes') == H
    assert sha(R / 'build/bill_capsule_hud44204.nes') == H
    for q in source_receipt['changes']:
        assert sha(R / q['path']) == q['after_sha256']
        assert sha(R / q['preimage']) == q['before_sha256']
    native = R / 'build/current-85af-bill-hard-earned-hud-v1'
    n = native / 'native'
    for name in ['component-review.json', 'capsule-hud-native.json',
                 'selected-eight-whole-frames-v3.json']:
        assert json.loads((n / name).read_text())['passed']
    launch = json.loads((native / 'launch.json').read_text())
    assert launch['exit_code'] == 0 and launch['changed_inputs'] == []
    hud = json.loads((n / 'capsule-hud-native.json').read_text())
    assert hud['ROM_sha256'] == H and hud['actual_complete_three_part_counts'] == [420, 380, 278, 287, 419, 423]
    route = R / 'build/verification/compact-85af-bill-hard-v1'
    result = json.loads((route / 'result.json').read_text())
    review = json.loads((route / 'review.json').read_text())
    assert result['ROM_sha256'] == H and result['passed'] and review['passed']
    assert result['zero_deaths'] and result['cheats_off']
    ordinary = {}
    for mapper, want in [('mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                         ('mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        p = R / f'build/bill-hud-inert-ordinary-{mapper}.nes'
        ordinary[mapper] = sha(p)
        assert ordinary[mapper] == want
    dest = cp / 'hud-native'
    assert not dest.exists()
    dest.mkdir()
    for name in ['prepared-not-run.json', 'command.json', 'run.lua', 'launch.json']:
        shutil.copyfile(native / name, dest / name)
    for name in ['capsule-hud-native.json', 'capture-budget.json',
                 'ppu-capture-native-result.json', 'selected-eight-whole-frames.png',
                 'selected-eight-whole-frames.json', 'selected-eight-whole-frames-v2.json',
                 'selected-eight-whole-frames-v3.json']:
        shutil.copyfile(n / name, dest / name)
    for name in ['component-review.json', 'native-bill-gallery.json', 'events.jsonl',
                 'ability-dma-epochs.jsonl', 'actual-ppu-index.csv', 'apu.csv',
                 'bill-cadence.csv', 'captures-index.jsonl']:
        (dest / (name + '.gz')).write_bytes(gzip.compress((n / name).read_bytes(), mtime=0))
    source_dest = cp / 'source-checks'
    source_dest.mkdir()
    for name in ['bill_capsule_hud44204_build.json', 'bill_capsule_hud44204_controls.json',
                 'bill_capsule_hud44204_controls_negatives.json',
                 'bill_capsule_hud44204_irq_bus_addendum.json',
                 'bill_capsule_hud44204_ordinary.json', 'bill_capsule_hud44204_handoff.json']:
        (source_dest / (name + '.gz')).write_bytes(gzip.compress((R / 'build' / name).read_bytes(), mtime=0))
    for name in ['bill-hud-inert-canonical.build.json', 'smb-crossover-mmc5-expanded.build.json',
                 'bill-hud-inert-ordinary-mmc3.build.json', 'bill-hud-inert-ordinary-mmc5.build.json']:
        shutil.copyfile(R / 'build' / name, source_dest / name)
    # Historical source preimages remain separate from the now adopted sources.
    # Frozen source controls must not be relabelled as executions after adoption.
    files = {p.relative_to(cp).as_posix(): sha(p) for p in cp.rglob('*') if p.is_file()}
    (cp / 'manifest.json').write_text(json.dumps(dict(files=files,
        original_capture=dict(path=str(n / 'captures.nesppuv1'), sha256=sha(n / 'captures.nesppuv1'),
                              copied_to_repository=False),
        preimage_resolution='Original canonical-source bindings resolve to the exact source-adoption preimages; all native runs and candidate controls preceded mutation.'), indent=2) + '\n')
    report = dict(status='adopted', goal_complete=False, ROM_sha256=H,
        previous_ROM_sha256=source_receipt['previous_canonical_ROM'],
        changes=['Skip the proved-inert second advanced-weapon scan for Bill/Lance while retaining freeze clocks and foreign contracts.',
                 'Move the complete original selected-gun capsule to the free upper HUD gap, clear of WORLD/TIME and all score/coin digits.'],
        ROM_delta=dict(bytes=51, banks=[6, 61], new_RAM=0, new_CHR=0, new_bank_switches=0),
        sources=source_receipt['changes'], canonical_rebuild_matches_native_candidate=True,
        ordinary_builds_exact=ordinary,
        source_cost='Typed callers save620..680 CPU cycles; sparse advanced admission can cost up to24 more. The HUD gate adds21 cycles to Bill,12 to foreign selected HUD,0 to fixed Samus missiles/no HUD. No whole-frame FPS claim.',
        native_components=dict(passed=True, cases=7, stages=28, frames=4338, Main_updates=3860,
            completed_DMAS=3288, min_SP=200,
            acquisition_scope='Initial Mushroom/PlayerStatus1 is an explicit staged seed. Subsequent guns and Rapid capsules are physical staged-mature pickups with actual autoequip/emission/cadence/enemy/terrain/source-art/SFX/cleanup witnesses. No natural reveal/rise, starting Mushroom collection, Select or energy claim.',
            complete_three_part_HUD_counts=hud['actual_complete_three_part_counts'],
            ROOT_whole_frames_reviewed=8, actual_static_HUD_cells_exact=True,
            negative_pixel_oracles_preserved=['selected-eight-whole-frames.json', 'selected-eight-whole-frames-v2.json']),
        native_route=dict(passed=True, mode='hard', frames=result['frames'],
            Main_updates=result['completed_loops'], PPU_frames=result['full_frames'],
            zero_deaths=True, cheats_off=True, ROOT_whole_frames_reviewed=7,
            report='bill-current85afad-hard-route-2026-10-28.json',
            comparison='Actual85af saved inputs, trace and all5107 decoded PPU buffers exactly match the successful44204 parent replay. Other identities retain actual older-build witnesses.'),
        prior_controller_failure='Original44204 zero-death contact failure remains in the held checkpoint; paired revised real-controller policy passes326942 and44204. Do not erase or claim identical input histories between those different-speed runs.',
        checkpoint=cp.relative_to(R).as_posix(),
        downloads=['C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes',
                   'C:/Users/kando/Downloads/SMB-Crossover-2026-10-28-85afad50-MMC5.nes'],
        limits=['Laser/Flare selected-capsule admission still alternates with their shot graphics family; placement repair does not fix that intermittency.',
                'Octopus body starvation under first-eight sprite limits and other crowded-body issues remain open.',
                'Only Bill has a full route on exact85af so far. Complete latest-ROM roster/modes/shortcuts/graphics/audio/performance work remains active.'],
        bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__).resolve(), cp / 'manifest.json',
            R / 'docs/qa/bill-inert-pool-native-qualified-2026-10-28.json',
            R / 'docs/qa/bill-current85afad-hard-route-2026-10-28.json']})
    target = R / 'docs/qa/bill-hud-inert-adoption-2026-10-28.json'
    assert not target.exists()
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(report=str(target), checkpoint=str(cp), files=len(files),
        checkpoint_bytes=sum(p.stat().st_size for p in cp.rglob('*') if p.is_file()))))


if __name__ == '__main__':
    main()
