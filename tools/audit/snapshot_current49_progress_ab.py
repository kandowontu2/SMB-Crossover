"""Preserve tested AI, retained verifier interruption, and next frozen layer."""
from pathlib import Path
import datetime, hashlib, json, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root-current49-progress-ab.json';assert not output.exists()
    previous = V / 'root-current49-progress-aa.json'
    assert sha(previous) == '7f019145dbb509ba43423974bd919884c6813d838004bb48c3f93391e1f7d6c4'
    checkpoint = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    assert sha(checkpoint) == '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    pub = json.loads(checkpoint.read_text())
    assert all(sha(R / n) == h for n, h in pub['source_hashes'].items())
    for b in pub['builds']:
        for ext in ['nes', 'lbl', 'map', 'dbg']:
            x = b['artifacts'][ext];assert sha(R / x['path']) == x['sha256']
    H = V / 'root49-easy-ryu-union-ai'
    assert sha(H / 'report.json') == '01d1cff7c0075adc5bd74403a644379811e83a7f7921babd1910577c0185c55a'
    ai = json.loads((H / 'report.json').read_text())
    assert len(ai['source_hashes']) == 428 and all(sha(H / 'source' / n) == h for n, h in ai['source_hashes'].items())
    for parent in ['root49-easy-bro-union-ab', 'root49-easy-whip-phase-y']:
        p = V / parent;d = json.loads((p / 'report.json').read_text())
        assert all(sha(p / 'source' / n) == h for n, h in d['source_hashes'].items())
    pins = {
        H / 'report.json': '01d1cff7c0075adc5bd74403a644379811e83a7f7921babd1910577c0185c55a',
        H / 'native/checks-aj/report.json': '221cc928c8be8e894c2df1055d94d3fbd834bff000719c29d5c60ac7f0d56896',
        H / 'native/checks-ak/report.json': 'bfee51eab12a2353232a8a0e220a14f9a4f60e5984f4070983c41ac0144c5ca9',
        H / 'native/checks-al/report.json': '87f250d0de4ca8d52fbd9433ccdf469a25faac16f52b453b359aceb7ec29bcb9',
        H / 'native/checks-am/report.json': '6bbe45db69c3783930b273743115306357d617aa7ddefc4cba6714a2511e7b77',
        H / 'native/source-review-an.json': '8982aef595368eb1a0eb063c76a3ae8aaf988e82f98daa572a5633b4a7b4d3fb',
        V / 'agent-lsr-ryu-source-body-o/implementation-freeze-o.json': 'be0e4181de7a3370a9b84ec8dd217731cd2468d1b7b0280b6d57451166a9bf6d',
        V / 'agent49-enemy-geometry-advanced-g/freeze.json': '9662d023b870f152b86d1f68b6b043af4091afd64879a253e4e45d43b91aa111',
        V / 'agent49-enemy-geometry-advanced-g/admission-c2.json': '2229d65ff7680d79df107df2671cc43bf842cb7e9cf38578a4fb469f2ea851a8',
        V / 'agent49-enemy-geometry-advanced-g/review-c2.json': '4bc255bde6548462ec06830ed3a2f6c1df6fbac71b14c6686f7317c66d79cf25',
    }
    for p, expected in pins.items():
        assert sha(p) == expected, p
    refs = [previous, checkpoint, R / 'docs/qa/easy-hard-legacy-v49.md'] + list(pins)
    branches = []
    for tag in ['root49y-pit-platform-e', 'root49y-pit-flame-i', 'root49y-pit-banks-k', 'root49y-pit-bowser-m', 'root49y-pit-pipe-o']:
        p = R / 'build/roster-through-2-2/search' / tag
        m = json.loads((p / 'manifest.json').read_text());q = json.loads((p / 'winning-reusable-root.json').read_text())
        assert m['branch_coldboot_verified'] and q['verified_coldboot'] and q['ram_bytes_identical'] == 10240 and not q['emulated_writes'] and not q['savestate_loads']
        branches.append(dict(tag=tag, frame=q['frame'], poll=q['poll'], inputs_sha256=sha(p / 'winning-inputs.csv')))
        refs += [p / 'manifest.json', p / 'winning-reusable-root.json']
    for tag in ['root49y-pit-continuation-n', 'root49y-pit-continuation-p']:
        p = R / 'build/roster-through-2-2' / (tag + '-6-v0-mmc3/manifest.json')
        refs.append(p)
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R);assert used < 50_000_000_000
    report = dict(status='ACTIVE_U_PUBLISHED_PRIVATE_AI_ALL_32_TARGETED_GROUPS_VERIFIED_C2_PENDING_INTEGRATION',
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
                  working_U_source_and_artifacts_exact=True, published_source_files=len(pub['source_hashes']),
                  private_Y_AB_AI_source_unchanged=True, AI_source_files=len(ai['source_hashes']), builds=ai['builds'],
                  AI_native_groups=dict(ryu=8, foreign_and_bomb=20, Bro=4,
                                        scope='452 Ryu body/platform/terrain cases;18 foreign weapon groups plus222 Samus bombs/map;1120 Bill Bro cases. Targeted components, not full-roster ordinary route certification.'),
                  AI_source_review='19955 independent original XML Q8 source receipts;964 rejected hull-gap contacts. New RAM7FE4 only; old globals/header/CHR/audio size/addresses exact.',
                  retained_AL_interrupt='AL MMC5 boundary hit the Lua one-second execution limit at case298. AM exact core, assertions, timeout and ROM pass384cases; original partial events and negatives retained.',
                  AB_ordinary_Luigi='Bothmaps full17412frames/17411polls six stages0deaths;19movement/controllerfields exactY. These AB interim runs are unrecorded and do not certify AI.',
                  ordinary_Pit=dict(image='Y MMC3', cold_verified_branches=branches,
                                    N='Clears1-4, enters2-1 at14788, ordinary powerup; finite controller pipe-cap assertion while aliveX1633/Y176.',
                                    P='New O branch passes pipe/gap, later ordinary injury/power loss and fall at17163X2272/Y242. Retained.',
                                    Q='Root current opaque branch discovery from genuinePpoll17088 toward next safe landing; no state-content/ROM/register/RAM patches.'),
                  C2=dict(status='FROZEN_RECEIVED_NOT_YET_ROOT_INTEGRATED', source_files=['remaining_weapons.s', 'megaman_weapons.s', 'roster_weapons.s'],
                          frozen_native_cases=792, deltas=dict(GUEST=-176, SPECIAL_EXTRA=286, SPECIAL_ROSTER=-62, BILL_GFX=1303, LEGACY_COLD=953),
                          predicted_merged_cold_bytes=2757, MMC5_cold_free=59,
                          qualifications='Geometry/origin/cache/spacing/reveal/Bro layer only. ConfirmedHit/despawn, armor, graphics rotation and other behavior/order items still need proof or repair; some conservative ledger entries may already match source.'),
                  references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
                  live_root_handles=[54732], active_specialists=[
                      'Mario K EasyMMC3 ordinary route now2-2; latest independentBQ at14237X1305/Y128. All other mode/map routes still pending.',
                      'Ryu O EasyMMC3 ordinary route clears first5stages then different valid water overlap. Source sword/body order receipts and water route continuing. FrozenO unchanged.',
                      'Bill advanced descendantH now closes remaining source-confirmed gaps; retained phase cap raised2GB to3.5GB total under global50GB. FrozenG/C2 unchanged.'],
                  workspace_bytes=used, cap_bytes=50_000_000_000, retain_lossless_captures=True, files_deleted=False,
                  accepted_release=False, goal_complete=False,
                  next='Three-way merge frozenC2 overAI, actual compiled fit and unchanged native core rebinding, then H behavior successor. Continue all-roster ordinary end2-2 routes/alternates/upgrades, measured lag work, final one-checkpoint recordings. Existing S2 videos do not certify AI.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), used, flush=True)


if __name__ == '__main__':
    main()
