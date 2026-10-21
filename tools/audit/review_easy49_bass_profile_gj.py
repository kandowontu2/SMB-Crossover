"""Freeze completed ordinary water timing samples and observer-transparency prefixes."""
from pathlib import Path
from collections import defaultdict
import csv
import hashlib
import json
import statistics

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = R / 'build/roster-through-2-2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    out = V / 'root49-el-bass-water-profile-gj.json'
    assert not out.exists()
    refs, profiles, transparency = {}, {}, []

    def pin(p):
        refs[p.relative_to(R).as_posix()] = dict(sha256=sha(p), bytes=p.stat().st_size)

    for a, b, n in [('root49ga-bass-live', 'root49gd-bass-live', 23700),
                    ('root49gd-bass-live', 'root49gg-bass-live', 24720)]:
        aa, bb = [P / (tag + '-9-v0-mmc3') for tag in (a, b)]
        x, y = rows(aa / 'trace.csv'), rows(bb / 'trace.csv')
        assert len(x) >= n and len(y) >= n
        assert x[:n] == y[:n]
        assert len(x[0]) == 21
        transparency.append(dict(before=a, after=b, exact_all21_trace_frames=n,
            includes_CPU_cycles_and_NmiSkipped=True, allRAM_comparison_claim=False))
        for f in (aa / 'trace.csv', bb / 'trace.csv'):
            pin(f)
    for tag in ('root49gd-bass-live', 'root49gg-bass-live'):
        folder = P / (tag + '-9-v0-mmc3')
        m = json.loads((folder / 'manifest.json').read_text())
        assert m['result']['failure'] == 'death' and not m['verified_through_2_2']
        assert m['rom_sha256'] == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
        scopes = defaultdict(list)
        for line in (folder / 'ordinary-profile.jsonl').read_text().splitlines():
            z = json.loads(line)
            assert z['world'] == 1 and z['level'] == 1
            assert z['return_cycle'] >= z['cycles'] > 0
            assert z['return_sp'] == (z['entry_sp'] + 2) % 256
            assert z['entry_bank'] >= 0 and z['return_bank'] >= -1
            scopes[z['name']].append(z)
        stats = {}
        for name, zs in scopes.items():
            c = [z['cycles'] for z in zs]
            clean = [z['cycles'] for z in zs if z['nmi'] == 0 and z['irq'] == 0]
            stats[name] = dict(samples=len(c), cycles_mean=round(statistics.mean(c), 3),
                cycles_min=min(c), cycles_max=max(c),
                crossed_NMI_samples=sum(z['nmi'] > 0 for z in zs),
                crossed_IRQ_samples=sum(z['irq'] > 0 for z in zs),
                no_interrupt_samples=len(clean),
                no_interrupt_cycles_mean=round(statistics.mean(clean), 3) if clean else None)
        profiles[tag] = dict(result=m['result'], completed_return_scopes=stats)
        for name in ('manifest.json', 'ordinary-profile.jsonl', 'inputs.csv', 'trace.csv',
                     'mm-injury-owner.csv', 'endpoint.png'):
            pin(folder / name)
    gc = P / 'root49gc-bass-live-9-v0-mmc3/manifest.json'
    assert json.loads(gc.read_text()).get('result') is None
    pin(gc)
    for name in ('root49-el-bass-profile-gd-preparation.json', 'root49-el-bass-profile-gd-core.lua',
                 'root49-el-bass-profile-gd/binding.json', 'root49-el-bass-profile-gg/binding.json',
                 'root49-el-bass-profile-gg-preparation.json'):
        pin(V / name)
    report = dict(status='PASS_SCOPED_ORDINARY_EL_MMC3_BASS_WATER_PROFILE',
        script_sha256=sha(__file__), immutable_EL_ROM='2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060',
        observer_transparency=transparency, profiles=profiles,
        timing_method='Actual physical-bank/eight-byte function entries, exact SP/physical-bank/eight-byte parent returns, CPU cycle counter. Exact RAM FarCallCommon return369 is separately bound to original compiled bytes. No emulator writes or state loads.',
        qualifications=['Times are inclusive nested scopes and must not be summed as disjoint CPU work.',
            'Interrupt-free subsets contain different gameplay states; their mean is descriptive, not a causal interrupt-cost estimate.',
            'Only scopes whose actual return was reached are included; terminal death stops before some final enclosing calls return.',
            'GC is an instrumentation rejection at the first RAM farcall return; retained as a negative, not a game failure.',
            'GD pit death24826 and GG RedCheep ID10 contact25212 are controller-route failures. No source collision defect is inferred.',
            'No MMC5 timing, new code optimization, full-clear, arsenal, final movie or perceptual frame-by-frame claim.'],
        runtime_changes=False, performance_improvement_claim=False,
        accepted_release=False, goal_complete=False, references=refs)
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(report['status'], sha(out))


if __name__ == '__main__':
    main()
