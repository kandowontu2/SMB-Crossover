"""Bind the corrected CF farcall expression; retain the first source negative."""
from pathlib import Path
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B


def main():
    prior = R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-experimental-resources/native-restore-factor-grant-v1.json'
    proposal = R/'build/contra-force-p1-native-restore-proposal-v2/proposal.json'
    source = R/'tools/reference/contra_force_p1_native_restore_proposal_v2.s'
    arena = R/'build/contra-force-p1-restore-arena-controls-v3/controls.json'
    assert B.sha(prior) == '4a6bf61cd52a84a40bd59ee383449a7ae2d4809268fb5e90464246185ec18809'
    assert B.sha(proposal) == '66b3439e9f1b6f27c6d6797173ba2325e08365d9525805e7522b57c153ad192d'
    assert B.sha(source) == 'a75ec54c06142d0619af5dced2e0b6351375f65c0566d3feb24613725d8e5a25'
    assert B.sha(arena) == '7cc41170df761d4ca05b14e96436ab7ae11eaf4ba3bc74af7d363be2caa7d5cd'
    for p in [prior, proposal, arena]:
        B.bound(json.loads(B.read(p)))
    d = json.loads(B.read(arena))
    assert d['passed'] and not d['actual_cartridge'] and not d['resource_adopted']
    assert len(d['checks']['six_valid_epochs_exact_original_final_state']) == 6
    assert len(d['checks']['16_stale_yellow_invalid_cookie_actual_native_PPU']) == 16
    text = B.read(source)
    assert 'lda #>(target)' in text and 'lda #<(target)' in text
    out = prior.with_name('native-restore-source-amendment-v2.json')
    assert not out.exists()
    q = dict(status='PRIVATE_SOURCE_RESTORE67_CORRECTED_SOURCE_AMENDMENT', source=True,
        native=False, installed=False, ready=False, admission=False,
        grant_sha256=B.sha(prior), bytes=67, physical_bank=91, A_span='AE97..<AEDA',
        M3_factor_prerequisite_unchanged=True,
        supersedes='The v1 measured source is unadoptable: unparenthesized #>target with BtServiceVeneers+18 emitted C2 instead of B0 as target high byte. V2 parenthesizes the complete expression; the same67B structural reservation is retained.',
        rejected93_bbox_span_remains_protected=True,
        evidence='Corrected source has finite actualSFC arena coverage: six paired valid epochs and16 poisoned cookie bytes restore native P1 through completed normalNMI. The arena supplies synthetic instruction fetches and is not a linked cartridge or physical placement proof.',
        still_required=['Genuine source composition of qualified M3 factor before67B placement, with correctA-view imports and no post-link patch.',
                        'Full linked current-parent paired OAM/PPU/lifecycle/foreign/interrupt controls, then root native review before admission.',
                        'All constraints of4dc4/5e70/4a6b grants remain. No change to readiness or Downloads.'],
        bindings={str(p.resolve()): B.sha(p) for p in [Path(__file__), prior, proposal, source, arena,
            R/'build/contra-force-p1-restore-arena-controls-v1/controls.json',
            R/'build/contra-force-p1-restore-arena-controls-v2/controls.json']})
    B.write(out, json.dumps(q, indent=2)+'\n')
    print(json.dumps(dict(amendment=str(out), sha256=B.sha(out), bytes=67)))


if __name__ == '__main__':
    main()
