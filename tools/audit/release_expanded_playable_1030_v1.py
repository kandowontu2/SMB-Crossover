"""Freeze tested rollout sources, retain the prior ROM, and update the WIP."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from checkpoint_roster_progress_1030_v2 import save, sha
from capture_budget import inventory, WORKSPACE_BYTES, WORKSPACE_SCAN_FILES

O = R / 'build/expanded-playable-roster-1030-v1'
ROM = O / 'joint/candidate.nes'
EXPECTED = '18de015564c61cd07d0d52ec26300661627278880d4226f7c589ac95028a0976'
BASE = R / 'build/required-rcr-ink-shared-v3/candidate/candidate.nes'
PREVIOUS = 'ec2f23edac3642c2e28acc1d8b6f17ef35063225375f4b4aa50a5f1ff56d6f46'
V = R / 'build/character-host-union-rollout-verification-v1'
K = R / 'build/unlock-kamikaze-v1-skin-1030-v4/native-1-1-v2'


def add_receipt(bindings, p):
    q = json.loads(p.read_text())
    for name in ['bindings', 'inputs']:
        for f, h in q.get(name, {}).items():
            if not isinstance(h, str):
                continue
            assert sha(f) == h, f
            assert bindings.get(f, h) == h, ('Binding conflict', f)
            bindings[f] = h
    bindings[str(p.resolve())] = sha(p)
    return q


def make_ips(a, b):
    assert len(a) == len(b)
    result = bytearray(b'PATCH')
    i = 0
    while i < len(a):
        if a[i] == b[i]:
            i += 1
            continue
        start = i
        while i < len(a) and a[i] != b[i] and i - start < 65535:
            i += 1
        result += start.to_bytes(3, 'big') + (i - start).to_bytes(2, 'big') + b[start:i]
    return result + b'EOF'


def main():
    assert sha(ROM) == EXPECTED and sha(BASE) == PREVIOUS
    report_file = R / 'docs/qa/expanded-playable-roster-2026-10-30.json'
    assert not report_file.exists()
    bindings = {}
    source = add_receipt(bindings, O / 'joint/source-closure.json')
    controls = add_receipt(bindings, O / 'kamikaze-controls.json')
    menu = add_receipt(bindings, V / 'menu80/result.json')
    rogue = add_receipt(bindings, V / 'rogue-cold/result.json')
    for kind in ['menu80', 'rogue-cold']:
        add_receipt(bindings, V / kind / 'binding.json')
        add_receipt(bindings, V / kind / 'ready.json')
        add_receipt(bindings, V / kind / 'capture-budget.json')
    art = add_receipt(bindings, R / 'build/dk-cf-roster-menu-qualified-v1/handoff.json')
    native = add_receipt(bindings, K / 'result.json')
    reviewed = add_receipt(bindings, K / 'review.json')
    add_receipt(bindings, K / 'ready.json')
    assert all(q['passed'] for q in [source, controls, menu, rogue, art, native, reviewed])
    assert source['ROM_sha256'] == controls['ROM_sha256'] == menu['ROM_sha256'] == rogue['ROM_sha256'] == EXPECTED
    assert (menu['alternates'], menu['slots'], menu['playable'], menu['pending']) == (80, 32, 52, 28)
    assert menu['late_enables'] == menu['visible_ppu_writes'] == 0
    assert native['zero_deaths'] and native['real_1_2_control_updates'] == 25
    assert native['ROM_sha256'] == '92768c16c8f898df97526276bf426ad35fccb163fc7b206371cfc41d7cbe1d32'
    assert rogue['source_fresh_calls'] == 1 and rogue['main_updates'] == rogue['source_control_steps'] == 256
    assert controls['complete_native_Main_pairs'] == 288
    for p in [Path(__file__), R / 'tools/prepare_kamikaze_v1_skin_1030_v1.py',
              R / 'tools/audit/build_kamikaze_v1_native_skin_1030_v1.py',
              R / 'tools/audit/build_kamikaze_v1_native_skin_1030_v2.py',
              R / 'tools/audit/materialize_playable_menu_parent_1030_v1.py',
              R / 'tools/audit/kamikaze_v1_native_skin_controls_1030_v1.py',
              K / 'selected-whole-frames.png', K / 'flower-whole-frame.png',
              K / 'flower-frame-review-source.json']:
        bindings[str(p.resolve())] = sha(p)
    for p in (V / 'menu80').glob('*.png'):
        bindings[str(p.resolve())] = sha(p)
    for p in (V / 'rogue-cold').glob('*.png'):
        bindings[str(p.resolve())] = sha(p)
    checks = [dict(name=n, passed=True) for n in [
        'Exact source-linked final MMC5 image', 'All80menu52ready28pending controller checks',
        'Zero visible-display uploads or late enables', 'Current Rogue cold selection and healthy gameplay',
        'Authentic DK and four Contra Force gameplay previews with palette retirement',
        'Kamikaze V1 original tiles and288nativeMario complete Main comparisons',
        'Kamikaze native ancestor1-1zero-death clear and25controlled1-2updates',
        'Root viewed eight final whole menu frames and eight selected Kamikaze gameplay frames'
    ]]
    limits = [
        'WIP release:28 menu identities remain Coming Soon, including FF and Arthur.',
        'Rogue final-image test is cold selection/walk/jump/land, not a current-image1-1clear or constant60Hz claim;173lag NMIs/301gameframes remain.',
        'Kamikaze1-1native replay is exact92768c16source ancestor; final18de adds separately checked menu-onlyDK/CF art. Final288Main comparisons and actualcoldmenu checks also pass.',
        'Bill joint source retains335extra CPU/Main against earlier753parent; broad performance and every-character/every-upgrade work remain active.'
    ]
    save('expanded-playable-roster', dict(status='SOURCE_AND_FINAL_MENU_NATIVE_PASS_BEFORE_WIP_INSTALL',
        ROM_sha256=EXPECTED, playable=52, pending=28,
        newly_unlocked=['Super Maaa', 'Rogue Dawn', 'Goku', 'Gimmick', 'Donkey Kong'],
        final_menu=menu, final_Rogue=rogue, Kamikaze_native=native,
        root_visual_review='All8finalmenuPNG and7Kama wholeframes+additionalflowerPNG viewed: originalbodies/colors readable, world/HUD coherent. Existingbluepreviewpanel retained.',
        checks=checks, limits=limits), bindings)
    patch = O / 'from-ec2f23ed-expanded-playable.ips'
    patch.write_bytes(make_ips(BASE.read_bytes(), ROM.read_bytes()))
    manifest = O / 'release-manifest.json'
    receipt = O / 'release-verification.json'
    manifest.write_text(json.dumps(dict(output_sha256=EXPECTED, base_sha256=PREVIOUS), indent=2) + '\n')
    receipt.write_text(json.dumps(dict(rom_sha256=EXPECTED, checks=checks, passed=True, limits=limits), indent=2) + '\n')
    checker = runpy.run_path('C:/Users/kando/.codex/skills/mario-porting/scripts/check_release.py')['check_release']
    verified = checker(ROM, manifest, receipt, base=BASE, ips=patch)
    (O / 'release-consistency.json').write_text(json.dumps(verified, indent=2) + '\n')
    downloads = Path('C:/Users/kando/Downloads')
    version = downloads / 'SMB-Crossover-2026-10-30-Expanded-Playable-MMC5.nes'
    latest = downloads / 'SMB-Crossover-Latest-WIP-MMC5.nes'
    backup = downloads / 'SMB-Crossover-Before-Expanded-Playable-ec2f23ed-MMC5.nes'
    if version.exists():
        assert sha(version) == EXPECTED
    else:
        shutil.copy2(ROM, version)
    if not backup.exists():
        shutil.copy2(BASE, backup)
    assert sha(backup) == PREVIOUS
    previous = sha(latest)
    if previous == PREVIOUS:
        temp = downloads / 'SMB-Crossover-Latest-WIP-MMC5.new-18de0155.nes'
        assert not temp.exists()
        shutil.copy2(ROM, temp)
        assert sha(temp) == EXPECTED
        temp.replace(latest)
    updated = sha(latest) == EXPECTED
    if updated:
        verified = checker(ROM, manifest, receipt, base=BASE, ips=patch, installed=latest)
        (O / 'installed-consistency.json').write_text(json.dumps(verified, indent=2) + '\n')
    usage = inventory(R, WORKSPACE_BYTES, WORKSPACE_SCAN_FILES)
    assert usage.complete and usage.bytes < 70_000_000_000
    result = dict(date='2026-10-30', passed=True, installed=updated, ROM_sha256=EXPECTED,
        latest=str(latest) if updated else None, versioned=str(version), backup=str(backup),
        previous_latest_sha256=previous, slots=32, identities=80, ready=52, pending=28,
        newly_unlocked=['Super Maaa', 'Rogue Dawn', 'Goku', 'Gimmick', 'Donkey Kong'],
        changes=['Kamikaze V1 original sprites as nativeMario visual skin and unchanged nativepalette.',
                 'Wider originalDK preview; all4CF previews use original gameplay sprites/colors.',
                 'Rogue genuine freshhealth, recursive area-reset and menu/lives finaldraw fixes.',
                 'Preserves Alex/Ryan requiredink and previously qualified denseParodius graphics.'],
        checks=checks, limits=limits, workspace_bytes=usage.bytes, workspace_files=usage.files,
        source_checkpoint='docs/qa/checkpoints/2026-10-30/expanded-playable-roster/')
    report_file.write_text(json.dumps(result, indent=2) + '\n')
    progress_file = R / 'docs/qa/host-integration-progress-2026-10-30.json'
    progress = json.loads(progress_file.read_text())
    if updated:
        progress['installed_download'] = dict(path=str(latest), sha256=EXPECTED, slots=32,
                                              identities=80, ready=52, pending=28)
    progress['active_work']['playable_rollout'] = '18de0155 WIP installed:52ready/28pending, final80menu and genuineRogue cold checks passed; Kamikaze V1 source288Main parity and nativeancestor1-1clear. Fullroster1-1/everyupgrade/performance remain open.'
    progress['active_work']['Rogue_Dawn'] = 'Playable in18de0155; genuine fresh/area/reset/finalmenu/livesportrait fixed; coldnativehealthywalk/jump/land passes. Broader1-1/everyitem/performance work remains.'
    progress['measured_workspace_bytes'], progress['measured_workspace_files'] = usage.bytes, usage.files
    progress_file.write_text(json.dumps(progress, indent=2) + '\n')
    print(json.dumps(dict(installed=updated, sha256=EXPECTED, path=str(version), ready=52,
                         pending=28, workspace_bytes=usage.bytes)))


if __name__ == '__main__':
    main()
