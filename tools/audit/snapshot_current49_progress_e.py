"""Snapshot source-exact G and separate nonshipping ownership repair build."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'build/verification/root-current49-progress-e.json'
    assert not out.exists()
    prior = ROOT / 'build/verification/root-current49-progress-d.json'
    report = json.loads(prior.read_text())
    refs = {
        'RyuG_C_passive_all9_prefix_receipt': 'build/verification/ryu49g-grapple-c-passive-a/actual-attempt-receipt.json',
        'RyuG_C_passive_manifest': 'build/roster-through-2-2/root49g-ryu-grapple-passive-c-a-10-v0-mmc3/manifest.json',
        'SamusF_E_actual_defeats_and_later_injury': 'build/verification/agent49f-samus-late-paratroopa-controller-f/actual-e-receipt.json',
        'SamusF_F_clears_2_1_water_negative': 'build/roster-through-2-2/root49f-samus-late-paratroopa-live-f-2-v0-mmc3/manifest.json',
        'MM_ownerC_frozen_source_repair': 'build/verification/mm48-native-owner-transfer-proposal-c/frozen.json',
        'MM_ownerC_actual_isolated_build': 'build/verification/root-mm48-owner-transfer-build-a/report.json',
    }
    optional = {'SamusF_E_actual_defeats_and_later_injury'}
    missing = []
    for key, name in refs.items():
        path = ROOT / name
        if key in optional and not path.is_file():
            missing.append(name)
            continue
        assert path.is_file(), name
        report['references'][key] = dict(path=name, sha256=sha(path))
    catalog = json.loads((ROOT / 'build/verification/root49g-multirow-applied-a/applied-source-hashes.json').read_text())
    assert len(catalog) == 404 and all(sha(ROOT / name) == digest for name, digest in catalog.items())
    private = ROOT / 'build/verification/root-mm48-owner-transfer-build-a'
    build = json.loads((private / 'report.json').read_text())
    assert build['status'] == 'PASS-build-only-not-shipping'
    assert len(build['source404_hashes']) == 404
    assert all(sha(private / 'source' / name) == digest for name, digest in build['source404_hashes'].items())
    total = sum((Path(parent) / name).stat().st_size
                for parent, _, names in os.walk(ROOT) for name in names)
    assert total < 30_000_000_000, total
    report.update(
        utc=datetime.now(timezone.utc).isoformat(), workspace_bytes=total,
        previous_progress=dict(path=str(prior.relative_to(ROOT)), sha256=sha(prior)),
        optional_classification_paths_not_found=missing,
        root_native_jobs_running=[],
        agents={
            'megaman_bass': 'Host-only compiled ownerC strict verifier preparation; build completed, no ownerC CPU/native calls yet',
            'link_simon_ryu': 'Host-only actual lowergrapple correction proposal/independent fixtures, conservative near-platform qualification remains open',
            'pit_rygar_sophia': 'Host-only actual F2-1 defeat/2-2 injury review and pending source Samus crouch HRect check',
        },
    )
    report['limits'] += [
        'OwnerC is a separate isolated48 source repair: MMC3 wholeROM equals48; actual MMC5 45e64c1d1796d5a8538398c8660a7bcd05ecb33777f0366fd58e250c8d850b4e matches full independently predicted ROM and bank0b/29 templates. No ownerC CPU/native/performance qualification yet, no shared audio edits.',
        'Whole bank29 has multiple segments. Initial segment-local free-space assumption failed a host guard before build; optional GUEST_AUDIO_TAIL after CHAR_SELECT preserves all old segment addresses and uses236 of533 free bytes. Old negative retained.',
        'Passive C9605 diagnostic preserves all9 original CSV prefixes exactly. Agent reports actual lowergrapple admission atY160+3FFB lacks source FOUR integer-pixel raise to156+3FFB; exact static-grid/other-ground classification and runtime proposal pending.',
        'Samus F now clears2-1 and enters2-2 at21990, dies23789 inwater; allsix stages entered but notcleared. Pending injury review and independent crouch-body source geometry concern are not declared ROM defects or resolved.',
    ]
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(path=str(out.relative_to(ROOT)), sha256=sha(out), workspace_bytes=total)))


if __name__ == '__main__':
    main()
