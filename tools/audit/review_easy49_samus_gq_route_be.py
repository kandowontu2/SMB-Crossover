"""Independently rehash Samus's completed, explicitly GQ-scoped route packet."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/specialist-samus-gq-route-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = R / 'build/verification/root49-samus-gq-route-review-be.json'
    assert not out.exists()
    f = D / 'phase-freeze-be.json'
    i = D / 'phase-index-be.json'
    h = D / 'handoff-bd.json'
    assert sha(f) == 'cd2d95890e43fb33fe4a787d3d2edc44b45483c1c6e5f8d3b78f4c6879644c81'
    assert sha(i) == '3c63ef953b7f462c13301c1eced8dc2aaf49d8606668baf7b4c68b9d007369dd'
    assert sha(h) == 'b0dc09ef59553835208484d0e1b3c6bfe3f8f3ae63037d5b223b221a5c388c69'
    frozen, index, handoff = [json.loads(p.read_text()) for p in (f, i, h)]
    total = 0
    assert len(frozen['files']) == frozen['file_count'] == 1534
    for item in frozen['files']:
        p = R / item['path']
        assert p.stat().st_size == item['bytes'] and sha(p) == item['sha256'], item['path']
        total += item['bytes']
    assert total == frozen['total_listed_bytes']
    assert not index['owned_native_job_live'] and not index['emulated_state_RAM_register_PC_or_coordinate_writes']
    assert handoff['result']['cleared'] and handoff['result']['all_six_stages'] and not handoff['result']['deaths']
    assert handoff['result']['frames'] == 28285 and handoff['next_controls']['frames'] == 25
    assert not handoff['savestate_loads'] and not handoff['opaque_branches_adopted']
    assert index['unknown_support_count'] == 0 and sum(index['support'].values()) == 136
    report = dict(status='PASS_INDEPENDENT_GQ_SAMUS_ROUTE_PACKET_REHASH', script_sha256=sha(__file__),
        freeze_sha256=sha(f), index_sha256=sha(i), handoff_sha256=sha(h),
        rehashed_files=1534, rehashed_bytes=total,
        mapper='mmc3', behavior='Easy', ROM_sha256=index['ROM_sha256'], result=handoff['result'],
        support=index['support'], tier_and_injury_scope=index['tier_and_injury_scope'],
        qualifications=index['qualifications'],
        scope='Root rehash/review of actual fixed GQ proof. Not another native replay; not a transfer to source-c/source-e, final movie, complete arsenal or source-perfect claim.',
        main_changed=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], sha256=sha(out), rehashed_files=1534)))


if __name__ == '__main__':
    main()
