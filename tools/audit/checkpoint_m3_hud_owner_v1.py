"""Save reviewed HUD repair receipts and explicitly earlier-hash roster progress."""
from pathlib import Path
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'docs/qa/checkpoints/2026-10-25/m3-hud-5ec8';out.mkdir(parents=True,exist_ok=False)
    sources={
        'adoption.json':'m3-hud-timing-v1/adoption-owner-v1/proof.json',
        'native-qualification.json':'m3-hud-timing-v1/final-native-v1/proof.json',
        'baseline-pixels.json':'m3-hud-timing-v1/final-native-v1/baseline-luigi3/proof.json',
        'luigi3-pixels.json':'m3-hud-timing-v1/final-native-v1/candidate-luigi3/proof.json',
        'mario3-pixels.json':'m3-hud-timing-v1/final-native-v1/candidate-mario3/proof.json',
        'leaf-cpu.json':'m3-hud-timing-v1/owner-cpu-v2/proof.json',
        'affected-routes.json':'m3-hud-timing-v1/affected-routes-v1/proof.json',
        'source-build.json':'m3-hud-timing-v1/private-owner-v2/proof.json',
        'implementation.patch':'m3-hud-timing-v1/private-owner-v2/review.patch',
        'rejected-private-carry-cpu.json':'m3-hud-timing-v1/owner-cpu-v1/proof.json',
        'earlier8ff-roster-reconciled.json':'current8ff-roster-reconciled-v1/proof.json',
        'earlier8ff-frame-scan.json':'current8ff-roster-review-v1/batch-v4/proof.json',
        'bass-controller-retry.json':'current8ff-bass-retry-v1/proof.json',
    }
    for name,p in sources.items():shutil.copy2(D/p,out/name)
    snapshots=json.loads((D/'current8ff-roster-review-v1/batch-v4/proof.json').read_text())
    reviewed={'megaman','proto','samus','bill','mario','luigi','lance','zelda2','sypha','alucard','pit','bass'}
    selected=[r for r in snapshots['runs']if r['identity']in reviewed]
    assert len(selected)==12
    review=dict(ROM_sha256=snapshots['ROM_sha256'],reviewer='ROOT actual image inspection',sample_sheets=12,selected_frames=96,
                refs=[{k:r[k]for k in ['identity','mode','sample_sheet','sample_sheet_sha256','samples']}for r in selected],
                observations=['No additional obvious background/body-CHR or score-location anomaly in these96 selected actual frames.',
                              'Sypha2107 below-ground defeated Goomba is a normal V-flipped falling corpse; actual OAM attributes83.',
                              'Bass2738 apparent floating green strip in montage is the next panel left-edge normal pipe exiting viewport; actual2738/2750 checked.',
                              'The independently observed SMB3 P-bar cloud/font defect is real and separately repaired here.'],
                scope='Eight actual frames per listed route plus named detail checks; never an every-frame/source-palette/animation/visibility/SFX verdict. Other26 profile sheets have a separate agent review, pending its final receipt.')
    (out/'earlier8ff-root-selected-review.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
    for dst,source in [('before.png','m3-hud-timing-v1/final-native-v1/baseline-luigi3/frame-001354.png'),('after.png','m3-hud-timing-v1/final-native-v1/candidate-luigi3/frame-001354.png')]:shutil.copy2(D/source,out/dst)
    files={p.name:sha(p)for p in out.iterdir()if p.is_file()}
    tools=['probe_m3_hud_timing_v1.py','prepare_m3_hud_owner_v1.py','check_m3_hud_owner_cpu_v1.py','qualify_m3_hud_owner_v1.py','adopt_m3_hud_owner_once_v1.py','checkpoint_m3_hud_owner_v1.py','scan_direct_background_transients_v1.py','review_direct_roster_ppu_v1.py','retry_bass_route_v1.py','reconcile_roster_routes_v1.py']
    manifest=dict(ROM_sha256='5ec81c9250c20aee31af0d3b98c241932c72b3147e05702de70e266f3c854893',goal_complete=False,
                  external_archive=str(D),files=files,tools={n:sha(ROOT/'tools/audit'/n)for n in tools},
                  source_sha256=sha(ROOT/'src/x5_bounce.s'),earlier_roster_hash=snapshots['ROM_sha256'],
                  limitations='Existing37 identities first. Earlier8ff recordings establish38zero-death1-1routes and193035actualPPUframes, not all-current/every-powerup completion. Conservative scanner has3question-block candidate events; it excludesHUD and missed the real P-bar defect. Selected-image visibility/SFX/source and remaining music/fade work stay open.')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    note='''

2026-10-25 SMB3 P-bar ownership accepted
Current MMC5 is5ec81c9250c20aee31af0d3b98c241932c72b3147e05702de70e266f3c854893.
ROOT canonical compile/Downloads/default match. One sourcefilex5_bounce.s:
16ROMbytes inbank86 reuse real unused15B dispatcher space. Generic native UI
keeps SMB3 custom HUD font ownership through an interrupted/lagged update.
Baseline183wrong-bar frames reproduced; finalMario3/Luigi3 each1892actualPPU
bar frames have0wrong-mask pixels and no latefont publication.1600actualCPU
leaf/register/flag cases and11affected native1-1routes pass. Otherleafcost+19
CPUcycles max is explicit; no universalcadence/perfectionclaim.
Earlier38routes/37identities on8ff all clear after retained BassHardcontroller
jump retry;193035actualPPUframes losslesslyretained/scanned. This is old-hash
route progress, not everyitem/allHard/current5ec8fullroster qualification.
Checkpoint:docs/qa/checkpoints/2026-10-25/m3-hud-5ec8.
Rollfadec32b andMike7992 native packets run on their explicit earlierparents;
compose/requalify before installation. No new characters/menu row yet.
'''
    for name in ['docs/qa/CLAUDE-HANDOFF-2026-10-24.txt','docs/qa/current-work-pr-2026-10-24.md','docs/qa/ten-agent-work-2026-10-25.txt']:
        p=ROOT/name;old=p.read_bytes();nl=b'\r\n'if b'\r\n'in old else b'\n';p.write_bytes(old+note.replace('\n',nl.decode()).encode())
    print(json.dumps(dict(checkpoint=str(out),manifest_sha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
