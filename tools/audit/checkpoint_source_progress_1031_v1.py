"""Stage only reviewed frozen checkpoints; leave unrelated user work alone."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(['git',*args],cwd=R,capture_output=True,text=True,check=True).stdout


def main():
    assert not git('diff','--cached','--name-only').strip(),'Existing staged work must be left alone'
    files={Path(__file__)}
    qa=R/'docs/qa/checkpoints/2026-10-31'
    for name in ['cf-owner-retirement-source-v1','cf-cold-warm-source-v1','cf-cold-warm-palette-source-v1']:
        files.update(R/p.strip() for p in (qa/name/'owned-files.txt').read_text().splitlines() if p.strip())
    for name in ['smb3plus-menu-controller-native-v1','contra-force-warm-lifecycle-v1','contra-force-body-palette-names-v1']:
        d=json.loads((qa/name/'owned-files.json').read_text())
        files.update(R/p for p in d['files']+d['source_tools'])
    for name in ['cf-followup-root-review-v1','cf-lifecycle-root-review-v1','cf-final-source-root-review-v1',
        'cf-palette-successor-root-review-v1','contra-force-cold-warm-resources','contra-force-p1-experimental-resources']:
        files.update(p for p in (qa/name).iterdir() if p.is_file())
    files.update(R/'tools/audit'/n for n in ['review_cf_followup_packets_1031_v1.py','review_cf_lifecycle_packet_1031_v1.py',
        'review_cf_final_source_packets_1031_v1.py','review_cf_palette_successor_1031_v1.py',
        'cf_cold_warm_resource_grant_1031_v1.py','cf_cold_warm_resource_grant_1031_v2.py','cf_p1_experimental_resource_grant_1031_v1.py'])
    # Keep the concrete experimental proposal reviewable in Git; compiled
    # artifacts and all ROMs remain private/ignored.
    dest=qa/'contra-force-p1-experimental-resources'
    for source,name in [
        (R/'build/contra-force-p1-shared-factor-proposal-v3/proposal.json','proposal.json'),
        (R/'build/contra-force-p1-classifier-controls-v1/controls.json','classifier-controls.json'),
        (R/'tools/reference/contra_force_p1_shared_factor_proposal_v2.s','shared-selector.s'),
        (R/'build/contra-force-p1-shared-factor-proposal-v3/ff-epoch-native-tail-zero-label.inc','native-tail-zero-label.inc'),
        (R/'build/contra-force-p1-shared-factor-proposal-v3/current-linked-source-consumers.json','source-consumers.json')]:
        assert not (dest/name).exists();shutil.copy2(source,dest/name);files.add(dest/name)
    files.update((R/'tools/audit').glob('prepare_contra_force_p1_shared_factor_proposal_v*.py'))
    files.add(R/'tools/audit/contra_force_p1_classifier_controls_v1.py')
    files.update((R/'tools/reference').glob('contra_force_p1_shared_factor_proposal_v*.s'))
    latest=Path.home()/'Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'
    assert sha(latest)=='c6635815711a624a02c4337cd9f1830ca9c43b14a824f2ea51963f796ad98c2a'
    progress=R/'docs/qa/continuation-2026-10-31-source-native.json';assert not progress.exists()
    d=dict(status='ACTIVE_EXPANDED_ROSTER_GOAL_INCOMPLETE',installed_playable=66,
        installed=str(latest),installed_SHA256=sha(latest),
        SMB3plus=dict(source_handoff='e83da0e0f7ba825cea380acd26ac6168cb0dcc5ab51ea3856997f131b85f9223',
            candidate='05b1c5a861eaf49fbaea1f8278229f2970defa3e81909178e0eb46e1ad2f2d10',
            checkpoint='docs/qa/checkpoints/2026-10-31/smb3plus-menu-controller-native-v1',
            source_original_cases=224,source_original_edges=2016,foreign_movement_pairs=1344,
            graphics_pairs=9072,real_interrupt_cuts=3380,native_Toad_and_Peach=True,
            current66_source_composition_in_progress=True,playable_admission=False,
            remaining=['Complete donor ground-pound/custom stomp delay','Toad kick audio','Special art consumers','Current66 composition and complete1-1/powerup checks']),
        ContraForce=dict(cold_source_handoff='95e76dd28d532910a64a317d422440035790f476da3ee22f16ec6d988a16abb8',
            palette_source_handoff='c2de3f9c76595e5a6e11ec41cf15a02c1b9d5b41091f9f99f612b88e9d315876',
            ready=False,remaining=['Actual linked native name fallback','Paired complete-projectile P1/OAM source experiment','Native gameplay/admission']),
        Battletoads=dict(ready=False,linked_owner_gate_pass=True,remaining=['Current-parent own cold/palette/menu integration','Native gameplay/admission']),
        active_owners=dict(root='SMB3+ donor controls/native/progression and final integration',
            claude_gimmick_review='Surgical SMB3+ source composition onto installed66',
            claude_goku_maaa_review='CF actual name fallback and shared integration',
            claude_dk_review='New private paired P1 source experiment under exact4dc4 grant'),
        cap_bytes=70000000000,last_inventory_bytes=53615680285,
        whole_goal_complete=False,all_character_1_1_and_every_powerup_complete=False)
    progress.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n');files.add(progress)
    paths=[]
    for p in sorted(files):
        p=p.resolve();assert p.is_relative_to(R) and p.is_file(),p
        assert p.name!='current-roster-progress-2026-10-27.json'
        assert p.suffix.lower() not in ['.nes','.o','.dbg','.lbl','.mp4','.avi','.wav','.bin'],p
        assert p.stat().st_size<100000000,p
        paths.append(p.relative_to(R).as_posix())
    git('add','--',*paths)
    staged=git('diff','--cached','--name-only').splitlines()
    assert set(staged)<=set(paths) and 'docs/qa/current-roster-progress-2026-10-27.json' not in staged
    print(json.dumps(dict(staged_files=len(staged),bytes=sum((R/p).stat().st_size for p in staged),
        installed_SHA256=sha(latest),goal_complete=False)))


if __name__=='__main__':main()
