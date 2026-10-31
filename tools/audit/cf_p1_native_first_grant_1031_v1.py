"""Amend the private experiment to draw native once before the late guard."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B


def main():
    proposal=R/'build/contra-force-p1-shared-factor-proposal-v4/proposal.json'
    prior=R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-experimental-resources/root-review-and-reservations.json'
    assert B.sha(proposal)=='4cdd8638d84a0a1419b6dbb0ae06e1e4960125c530d99ed6dc17c1e9f39ed7c3'
    p,d=[json.loads(B.read(x)) for x in [proposal,prior]];B.bound(p);B.bound(d)
    assert p['measured_source_size']==p['current_bridge']['span']==59
    assert p['selected31']['native_first_then_guarded_late_only']
    source=R/'tools/reference/contra_force_p1_shared_factor_proposal_v3.s'
    s=B.read(source);branch=s[s.index('CF:\n'):]
    assert branch.index('jsr FfMuxNativeTail')<branch.index('sta SafecallA_SMC+1')
    assert 'bne Far' in branch and 'lda #.lobyte(.bank(BtServiceVeneers)|$80)' in branch
    out=prior.with_name('native-first-amendment-v2.json');assert not out.exists()
    receipt=dict(status='PRIVATE_NATIVE_FIRST_P1_EXPERIMENT_AMENDMENT',source=True,native=False,
        installed=False,ready=False,admission=False,prior_grant_sha256=B.sha(prior),
        amendment='Use the whole existing59B span for the measured native-first source. Original native DrawAll completes once before guarded selected31 row6 late-only filtering. Invalid cache cannot skip native world. Both real target ROM banks are nonzero, so final BNE safely shares the exact FarCallCommon tail.',
        shared_additional_bytes=0,own_RAM_and_temporal_aliases_unchanged=True,
        all_prior_constraints=d['required_before_any_admission'],
        additional_required='Prove actual nativeDrawAll-once for every valid/invalid/stale-cookie case; early attribute save/tag must occur only after ROM authentication, late row6 must never draw a second time. Check actual native input/output flags, A/C maps, live stack/33SMC across normal/lag/pausedNMI and IRQ. The previous57B model is historical and is not validation of this59B product.',
        bindings={str(x):B.sha(x) for x in [Path(__file__),proposal,prior,source]})
    B.write(out,json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(grant=str(out),sha256=B.sha(out),shared_span_bytes=59,new_bytes=0)))


if __name__=='__main__':main()
