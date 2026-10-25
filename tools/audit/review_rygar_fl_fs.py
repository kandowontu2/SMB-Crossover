"""Review every recorded current Rygar frame against the complete visible-write log."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/rygar-current-review-fs'
ROOT=R/'build/roster-through-2-2'
FP=ROOT/'root-rygar-current-fl-proof-fp-7-v0-mmc3'
FQ=ROOT/'root-rygar-current-fl-av-fq-7-v0-mmc3'
FR=ROOT/'root-rygar-full-visible-fr-7-v0-mmc3'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    O.mkdir()
    recording=json.loads((FQ/'manifest.json').read_text())
    assert recording['recording_verified'] and recording['verified_through_2_2']
    identical={}
    for name in ('trace.csv','inputs.csv','oam.csv','chr.csv','render.csv','audio-events.csv'):
        values=[sha(p/name)for p in (FP,FQ,FR)]
        assert len(set(values))==1,(name,values)
        identical[name]=values[0]
    code=(R/'tools/playthroughs/roster_review.py').read_text()
    old='splits = rows(directory / "scroll-writes.csv")'
    assert code.count(old)==1
    code=code.replace(old,'splits = rows(SCROLL_SOURCE)')
    old='sheet.save(directory / f"review-contact-{offset // 48 + 1}.png")'
    assert code.count(old)==1
    code=code.replace(old,'sheet.save(ROOT_OUTPUT / directory.name / f"review-contact-{offset // 48 + 1}.png")')
    old='(directory / "review.json").write_text'
    assert code.count(old)==1
    code=code.replace(old,'(ROOT_OUTPUT / directory.name / "review.json").write_text')
    (O/FQ.name).mkdir()
    (O/'adapted-review.py.txt').write_text(code)
    binding=dict(ROM_sha256=recording['rom_sha256'],recording_manifest_sha256=sha(FQ/'manifest.json'),
                 scroll_source=FR.relative_to(R).as_posix(),scroll_sha256=sha(FR/'scroll-writes.csv'),
                 exact_replays=identical,reviewer_sha256=sha(R/'tools/playthroughs/roster_review.py'),
                 scope='The video replay and the separate all-visible-write replay have literal identical inputs, CPU/position traces, committed OAM/CHR, render and audio-event logs. No capture files or metadata are altered; use the complete scroll evidence for the video review.',goal_complete=False)
    (O/'binding.json').write_text(json.dumps(binding,indent=2)+'\n')
    ns=dict(__name__='_rygar_fl_review',__file__=str(R/'tools/playthroughs/roster_review.py'),ROOT_OUTPUT=O,SCROLL_SOURCE=FR/'scroll-writes.csv')
    exec(compile(code,ns['__file__'],'exec'),ns)
    result=ns['review'](FQ)
    assert result['every_recorded_frame_decoded'] and result['verified_controller_clear']
    (O/'summary.json').write_text(json.dumps(dict(status='CURRENT_RYGAR_FULLFRAME_AUTOMATED_REVIEW_FLAGS_REQUIRE_INSPECTION',
        review=(O/FQ.name/'review.json').relative_to(R).as_posix(),review_sha256=sha(O/FQ.name/'review.json'),
        decoded=result['decoded_video_frames'],visible_scope=result['scroll_capture_scope'],split_flags=len(result['split_timing_candidates']),
        motion_flags=len(result['motion_candidates']),pixel_flags=len(result['video_vertical_shift_candidates']),
        flash_flags=len(result['video_background_flash_candidates']),audio_unconfirmed=len(result['audio_events_needing_priority_or_audible_review']),
        goal_complete=False),indent=2)+'\n')


if __name__=='__main__':
    main()
