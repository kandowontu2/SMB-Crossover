"""Freeze current T, menu placement, staged head tests and completed components."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys

R = Path(__file__).resolve().parents[2]
OUT = R/'build/verification/root-current49-progress-u.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    cp = R/'build/checkpoints/roster-audit-v49-ryu-head-t/manifest.json'
    data = json.loads(cp.read_text())
    assert data['status']=='PASS_WORKING_RYU_HEAD_T_BOTH_MAPPERS'
    cat = data['source_hashes']
    assert len(cat)==412 and all(sha(R/n)==h for n,h in cat.items())
    assert not data['accepted_release'] and not data['goal_complete']
    refs = [
        'build/verification/root-current49-progress-t.json',
        str(cp.relative_to(R)),
        'build/checkpoints/roster-audit-v49-menu-options-s2/manifest.json',
        'build/verification/root49-menu-validation-s2.json',
        'build/verification/agent-lsr-s2-head-n2-a/root-qa-suite-a/report.json',
        'build/verification/root49-ryu-ceiling-timing-u/preparation.json',
        'build/verification/root49-ryu-ceiling-fixture-v/staged-regression-review.json',
        'build/verification/root49-bill-cold-f/actual-review.json',
        'build/verification/root49s2-mario-luigi-pickups-b/actual-review.json',
        'build/verification/root49s2-mario-luigi-pickups-b/mario-growth-contact.png',
        'build/verification/root49s2-mario-luigi-pickups-b/luigi-growth-contact.png',
        'build/verification/specialist-scrooge-s2/handoff-final.json',
        'build/verification/specialist-scrooge-s2/mapper-pogo-edge-cause-verified.json',
        'build/verification/agent49s2-pit-fixed-al/actual-proof.json',
        'docs/qa/roster-provisional-v49.md',
    ]
    for optional in [
        'build/verification/specialist-scrooge-s2/handoff-m5-final.json',
        'build/verification/agent49s2-pit-record-an/technical-review.json',
        'build/verification/agent49s2-pit-record-an/final-handoff.json',
    ]:
        if (R/optional).exists():
            refs.append(optional)
    menu = R/'build/verification/root49t-menu-placement-u'
    assert not menu.exists()
    menu.mkdir()
    records = []
    for mapper in ['mmc3','mmc5']:
        rom = R/('build/smb-crossover-'+mapper+'.nes')
        build = next(q for q in data['builds'] if q['mapper']==mapper)
        assert sha(rom)==build['outputs']['nes']['sha256']
        log = R/('build/verification/smb-crossover-'+mapper+'-character-select.log')
        text = log.read_text(errors='replace')
        assert 'PASS static title' in text and 'FAIL ' not in text
        copied = []
        for p in [log, *sorted((R/'build/verification').glob('smb-crossover-'+mapper+'-select-*.png'))]:
            q = menu/p.name
            shutil.copyfile(p,q)
            copied.append(dict(path=str(q.relative_to(R)),sha256=sha(q),bytes=q.stat().st_size))
        records.append(dict(mapper=mapper,ROM_sha256=sha(rom),native_test_pass=True,
            actual_PPU_old_option_row_absent=True, hidden_character_select_option_focus_absent=True,
            power_on_shadows_off=True,controller_only=True,emulated_writes=False,artifacts=copied))
    menu_report = menu/'receipt.json'
    menu_report.write_text(json.dumps(dict(status='PASS_SHADOW_OPTION_ONLY_ON_OPTIONS_T_BOTH_MAPPERS',
        source_test_sha256=sha(R/'tests/character-select.lua'), results=records,
        image_inspected='S2 actual selected-Samus screenshot28 shows no setting row; T uses exact unchanged character-select source and its native PPU absence/navigation assertions pass.',
        source_character_select_sha256=sha(R/'src/character_select.s')),indent=2)+'\n')
    refs.append(str(menu_report.relative_to(R)))
    visual = R/'build/verification/root49s2-mario-luigi-pickups-b/visual-review-u.json'
    assert not visual.exists()
    visual.write_text(json.dumps(dict(status='VISUALLY_INSPECTED_SELECTED_GROWTH_FRAMES',
        source_review_sha256=sha(R/'build/verification/root49s2-mario-luigi-pickups-b/actual-review.json'),
        sheets=[dict(name=n,sha256=sha(visual.parent/n),selected_frames=12)for n in ['mario-growth-contact.png','luigi-growth-contact.png']],
        observation='Both actual retained native-video sheets inspected. Mushroom pickup, alternating growth poses and powered endpoint appear; background/block positions stay stable in selected frames.',
        qualifications='Selected visual frames only; full videos decoded by the separate automated review. Partial ordinary pickup components, not full routes or source-perfect color/audio certification.'),indent=2)+'\n')
    refs.append(str(visual.relative_to(R)))
    sys.path.insert(0,str(R/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used<50_000_000_000
    report = dict(status='progress-T-published-menu-placement-confirmed-full-goal-incomplete',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),
        accepted_release=False,goal_complete=False, main_source412_exact=True,
        current_working_checkpoint=cp.parent.name,
        references=[dict(path=n,sha256=sha(R/n),bytes=(R/n).stat().st_size)for n in refs],
        latest_user_request=dict(shadow_option_removed_from_character_select=True,
            location='Title OPTIONS only',default='OFF',both_current_mapper_native_tests=True),
        completed_root_jobs=['N2 broad suite terminal1:759 unchanged pass,two old ceiling assertion failures retained.',
            'Independent source envelope plus guarded native timing/old-build negative:bothmaps pass revised20-arena test;761 staged coverage.',
            'Bill F cold CPU group terminal0:29952 comparisons per mapper,59904total; body proposal not admitted.',
            'Mario/Luigi actual ordinary mushroom emergence,pickup,cue,growth components verified and selected frames viewed.',
            'Exact six-file Ryu correction published as T; old S2 captures retain original ROM hashes.'],
        S2_recorded_routes_qualified=['Mario and Luigi each mapper:full fixed recorded clears retained in prior snapshots.',
            'Scrooge MMC3 full recorded clear and10 isolated ability fixtures:final handoff pinned.',
            'Scrooge MMC5 fixed recorded clear; agent finishing media/ability/hash handoff.',
            'Pit fixed and recorded clear; agent completing all-frame/native-audio/selected-frame handoff.'],
        live_root_native_or_CPU_handles=[],
        specialists=['MegaMan2-2 ordinary route; Bass remains.',
            'Pit final recording review then requested idle for LSR rotation.',
            'ScroogeM5 final frozen handoff.'],
        workspace_bytes=used,cap_bytes=50_000_000_000,retain_lossless_captures=True,
        remaining=['Full roster/alternate normalroutes and every special/upgrade.',
            'Ryu water Blooper source body/cache geometry; Bill native46 missingpaths and layout integration.',
            'MegaMan water ceiling-route eligibility and contact diagnosis.',
            'Meaningful lag reduction with exact behavior comparisons; current overload/lag remains.',
            'Final same-checkpoint recordings; S2 files are not T route proofs.'])
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(path=str(OUT),sha256=sha(OUT),workspace_bytes=used)),flush=True)


if __name__=='__main__':
    main()
