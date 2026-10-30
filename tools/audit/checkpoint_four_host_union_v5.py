"""Preserve the current-menu four-host tests and their blocking cadence result."""
from pathlib import Path
import csv
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
UNIT=R/'build/character-host-union-v5'
ROUTE=R/'build/character-host-union-native-v1/gimmick-star-v1'
DEST=R/'docs/qa/checkpoints/2026-10-30/four-host-current-menu-native'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not DEST.exists()
    handoff=UNIT/'handoff.json'
    d=json.loads(handoff.read_text())
    assert d['candidate_sha256']=='1a71b8b5a5752aeec7440c4dc2de91a136d6285c98922c99b52f39f4047f2b25'
    inputs=dict(d['bindings'])
    for path,h in inputs.items():assert sha(path)==h,path
    assert len(d['receipts'])==12
    for path,h in d['receipts'].items():
        assert sha(path)==h
        receipt=json.loads(Path(path).read_text())
        if Path(path).parent.name=='menu-controls':
            assert receipt['status']=='PASS_ISOLATED_LINKED_6502_SOURCE_REVIEW'
            assert (receipt['slot_count'],receipt['profile_count'],receipt['ready_reselect_count'],receipt['pending_profile_count'])==(32,80,51,29)
        else:
            assert receipt['passed'],path
    upstream=Path(d['source_archive'])
    assert sha(upstream)==d['source_archive_sha256']=='4b68b506ff38a792f0dac71203d0f5e3a05afeb2e102308a94a459560e1a0ae3'
    summary=json.loads((UNIT/'native-summary.json').read_text())
    runs={q['run']:q for q in summary['runs']}
    assert len(runs)==8 and all(q['passed'] for q in runs.values())
    assert runs['bill-parent-v5']['completion_histogram']['0']==4
    assert runs['bill-cold-v1']['completion_histogram']['0']==16
    binding=json.loads((ROUTE/'binding.json').read_text())
    negative=json.loads((ROUTE/'result.json').read_text())
    assert not negative['passed'] and negative['reason']=='native death engine'
    assert negative['actual_star_ride_acceptances']==3 and negative['x']==1411
    assert binding['ROM_sha256']==d['candidate_sha256'] and binding['exit_code']==0
    assert sha(UNIT/'gimmick_route.lua')==binding['source_controller_sha256']
    assert sha(ROUTE/'controller.lua')==binding['wrapper_sha256']
    events=list(csv.DictReader((ROUTE/'events.csv').open()))
    assert sum(e['event']=='actual-GmRideStar-Yes'for e in events)==3
    assert [e['detail']for e in events if e['event']=='tall-wall-passed']==['761','936']
    inputs.update({str(p):sha(p)for p in ROUTE.iterdir()if p.is_file()})
    inputs[str(handoff)]=sha(handoff)
    inputs[str(UNIT/'gimmick_route.lua')]=sha(UNIT/'gimmick_route.lua')
    inputs[str(Path(__file__))]=sha(__file__)
    DEST.mkdir(parents=True)
    # Retain ROM/debug hashes as runtime references; publish source and compact
    # evidence. The verified upstream ZIP also includes ROM/debug copies.
    excluded={'.nes','.dbg','.lbl','.map','.exe','.dll','.zip','.mp4','.wav','.nesppuv1'}
    archive=DEST/'frozen-source-packet.zip'
    members={}
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path,h in inputs.items():
            p=Path(path).resolve()
            assert sha(p)==h
            if not p.is_relative_to(R) or p.suffix in excluded:continue
            member=p.relative_to(R).as_posix()
            info=zipfile.ZipInfo(member,(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes());members[member]=h
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(members)
        assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
    proof=dict(status='Source and bounded native tests reviewed; Bill cadence regression blocks shared installation',
        installed=False,ROM_sha256=d['candidate_sha256'],handoff_sha256=sha(handoff),
        upstream_archive_verified_sha256=sha(upstream),verified_unique_bindings=len(inputs),
        source_suites=12,source_menu='Current32-slot80-profile frontend,51 ready/29 pending in private candidate only. '
            'Only Goku,Gimmick,DonkeyKong and Maaa admitted relative to shared parent.',
        native=summary,root_visual_review='Viewed four authentic endpoint frames plus the actual accepted-star-ride image. '
            'No all-frame or sound certification. Gimmick HP slash glyph is misleading; source HP/capacity are2/2 and presentation successor is in progress.',
        charged_star=dict(actual_ride_acceptances=3,completed_tall_pipe_traversals=2,
            real_1_1_clear=False,terminal=negative,events=events,
            cause='Controller requested jump after support was lost at first pit; source physics remains unchanged.'),
        blocking='Bill zero-update frames increase4→16 and lag NMIs4→12 in matching cold controller scenarios. '
            'Source successor must minimize added dispatch and retest this same route.',
        open=['Bill regression fix and matching exact-candidate native budget rerun',
              'Actual1-1 clears and every earned powerup for all four owners',
              'Gimmick gap-controller timing and HUD readability',
              'Shared installation and remaining29 pending profiles'],
        archive=dict(path=str(archive),bytes=archive.stat().st_size,sha256=sha(archive)),
        members=members,runtime_references=inputs)
    (DEST/'root-review.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(DEST),archive_bytes=archive.stat().st_size,
                         members=len(members),verified_bindings=len(inputs))))


if __name__=='__main__':main()
