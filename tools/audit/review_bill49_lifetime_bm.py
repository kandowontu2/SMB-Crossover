"""Independently review the source premise used for finite Flare orbit data."""
from pathlib import Path
import hashlib, json, math

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-bill-lifetime-review-bm'
SOURCE = R / 'reference/crossover2/extracted/scripts/com/smbc'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    H.mkdir(exist_ok=False)
    draft = V / 'agent49-bill-advanced-parity-h/lifetime-source-g.json'
    review = json.loads(draft.read_text())
    sources = []
    for name, anchors in {
        'characters/Bill.as': ['private const WALK_SPEED:int = 150;', 'vxMax = xSpeed;'],
        'characters/Character.as': ['protected function checkPlatform()', 'nx += dxPlatform;'],
        'main/AnimatedObject.as': ['nx += vx * dt;', 'this.dxPlatform = this.onPlatform.dx;'],
        'ground/Platform.as': ['private const CONSTANT_RIGHT_SPEED:int = 120;', 'protected var hWaveSpeed:Number = 1.5;',
                               'protected var hWaveRange:Number = 60;', 'this.dx = nx - x;', 'player.x = player.x + this.dx;'],
        'level/Level.as': ['if(this.cgpx > this.rightScrollPos)', '_loc4_ = this.cgpx - this.rightScrollPos;', 'this.x -= _loc4_;']
    }.items():
        path = SOURCE / name
        text = path.read_text()
        lines = text.splitlines()
        assert all(x in text for x in anchors), name
        sources.append(dict(path=path.relative_to(R).as_posix(), sha256=sha(path),
                            anchors={x: [i + 1 for i, line in enumerate(lines) if x in line] for x in anchors}))
    dt = 1 / 60
    own = 150 * dt / 2
    carry = 60 * math.sin(1.5 * dt) / 2
    assert own == 1.25 and carry > 0.74
    report = dict(status='SOURCE_DRAFT_PREMISE_REQUIRES_PLATFORM_QUALIFICATION',
                  script_sha256=sha(__file__), source_draft_sha256=sha(draft),
                  draft_bounds=review['bounds_updates'], sources=sources,
                  mathematical_one_update=dict(dt_seconds=dt, Bill_walk_NES=own,
                                               horizontal_wave_platform_delta_NES=carry,
                                               sum_NES=own + carry, WALK_SPEED_only_bound_NES=own),
                  finding='Character.checkPlatform applies transport outside vxMax, and the follow camera tracks the resulting position. WALK_SPEED alone therefore does not bound every ordinary camera update.',
                  requirements='Admit a finite source/native platform extent and overlap argument, or provide enough orbit coverage for every supported ordinary trajectory. Preserve original scalar bytes; do not substitute an arbitrary runtime age kill.',
                  qualifications=['This algebraic counterexample invalidates the speed-only premise; it does not establish that a source-valid Flare survives384 updates.',
                                  'Finite platform width, source/native support, camera clamps and possible platform changes must be evaluated before a whole-lifetime claim.',
                                  'No ROM or source runtime is changed, and no gameplay defect is diagnosed by this review.'],
                  accepted_release=False, goal_complete=False)
    target = H / 'report.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(target), flush=True)


if __name__ == '__main__':
    main()
