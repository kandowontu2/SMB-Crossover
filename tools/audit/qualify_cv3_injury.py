"""Independently qualify the exact real-injury Grant/Alucard DMC repair."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import load, address, location
from cv3_primary_sfx_compare_v1 import cadence

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = 'ae97d45e5a33b20a399c0b55f241ea933a72eaea6f88e7fc69eae93af85c96e4'
FINAL = '52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    packet = D / 'cv3-dmc-followup-v1'
    prepared = packet / 'proposal-v1'
    assert sha(prepared / 'baseline.nes') == sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == PARENT
    assert sha(prepared / 'candidate.nes') == FINAL
    meta = json.loads((prepared / 'prepare.json').read_text())
    assert meta['changed_bytes'] == 68 and meta['changed_banks'] == [7, 82, 127]
    old, new = load(prepared / 'baseline.nes'), load(prepared / 'candidate.nes')
    before, after = qualified(prepared / 'baseline.nes'), qualified(prepared / 'candidate.nes')
    assert all(after.get(name) == value for name, value in before.items())
    changed = [i for i, (a, b) in enumerate(zip(old['raw'], new['raw'])) if a != b]
    assert len(changed) == 68 and sorted({(i-16)//8192 for i in changed}) == [7, 82, 127]
    for name, row in meta['sample_bytes_locations_lengths_exact'].items():
        assert address(old, name) == address(new, name) == row['address']
        a, b = location(old, name), location(new, name)
        assert old['raw'][a:a+row['length']] == new['raw'][b:b+row['length']]
    tools = [ROOT / ('tools/audit/' + name) for name in ['cv3_dmc_cpu_v1.py', 'cv3_dmc_native_v1.py', 'cv3_dmc_native_v1.lua']]
    hashes = {str(path): sha(path) for path in tools}
    with (out / 'cpu-host.log').open('w') as log:
        subprocess.run([sys.executable, str(tools[0]), '--prepared', str(prepared),
                        '--source', str(packet / 'capacity-source-v1'), '--output', str(out / 'cpu-v1')],
                       cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
    cpu_path = out / 'cpu-v1/proof.json'
    cpu = json.loads(cpu_path.read_text())
    assert cpu['passed'] and cpu['ROM_sha256'] == FINAL
    rows = []
    receipts = [cpu_path, prepared / 'prepare.json']
    def count(items):
        return dict(wall_frames=len(items), zero_update_frames=sum(row['updates'] == 0 for row in items),
                    draws=sum(row['draws'] for row in items), updates=sum(row['updates'] for row in items))
    for name, character, variant in [('grant', 5, 1), ('alucard', 5, 3), ('sypha', 5, 2), ('simon', 5, 0), ('link', 4, 0)]:
        baseline_path = packet / ('native-' + name + '-baseline-v1')
        prior = json.loads((baseline_path / 'native-proof.json').read_text())
        frozen = json.loads((packet / ('native-' + name + '-v1/native-proof.json')).read_text())
        assert prior['passed'] and prior['ROM_sha256'] == PARENT
        assert frozen['passed'] and frozen['ROM_sha256'] == FINAL
        assert frozen['fixture_sha256'] == sha(tools[2]) and frozen['runner_sha256'] == sha(tools[1])
        target = out / ('native-' + name)
        with (out / (name + '-host.log')).open('w') as log:
            subprocess.run([sys.executable, str(tools[1]), '--rom', str(prepared / 'candidate.nes'),
                            '--source', str(packet / 'capacity-source-v1'), '--output', str(target),
                            '--character', str(character), '--variant', str(variant)],
                           cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
        current_path = target / 'native-proof.json'
        current = json.loads(current_path.read_text())
        assert current['passed'] and current['ROM_sha256'] == FINAL
        assert len(current['cases']) == (4 if name in ['grant', 'alucard'] else 2)
        for a, b in zip(prior['cases'], current['cases']):
            assert a['name'] == b['name'] and a['durationUpdates'] == b['durationUpdates']
            assert b['realInjuries'] > 0
            if name in ['grant', 'alucard']:
                assert b['sourceExact'] and b['sourcePayloadChecks'] >= 193 and b['hardwareCompleted']
                assert b['dmcStarts'] >= 1
            else:
                hardware = lambda case: [(r['age'], r['register'], r['value']) for r in case['apu'] if r['register'] not in [0x4014, 0x4016]]
                assert hardware(a) == hardware(b)
        before_frames, after_frames = cadence(baseline_path), cadence(target)
        # Exact old hashes are retained; compare actual pressure work rather
        # than concealing new DMC steals behind equal wall-frame samples.
        bp = count([r for r in before_frames if r['case'] == 2])
        ap = count([r for r in after_frames if r['case'] == 2])
        assert bp['updates'] == ap['updates'] == 180 and bp['draws'] == ap['draws']
        assert ap['zero_update_frames']-bp['zero_update_frames'] <= (1 if name == 'alucard' else 0)
        rows.append(dict(character=name, cases=len(current['cases']), pressure_before=bp, pressure_after=ap,
                         minimum_sampled_SP=current['min_sp'], native=str(current_path), baseline=str(baseline_path / 'native-proof.json')))
        receipts += [current_path, baseline_path / 'native-proof.json']
        print(json.dumps(dict(character=name, cases=len(current['cases']), passed=True)), flush=True)
    assert all(sha(Path(path)) == expected for path, expected in hashes.items())
    proof = dict(passed=True, adopted=False, goal_complete=False, ROM_sha256=FINAL, parent_ROM_sha256=PARENT,
                 changed_bytes=68, changed_banks=[7, 82, 127], retained_PC_RAM_CHR_exact=True,
                 existing_DMC_samples_exact=True, new_RAM_bytes=0, candidate_native_cases=sum(row['cases'] for row in rows),
                 public_DMC_cases=cpu['actual_public_DMC_start_cases'], injury_owner_CPU_cases=cpu['actual_injury_owner_cases'],
                 original_injury_to_APU_CPU_chains=cpu['actual_injury_to_source_APU_cases'],
                 ordinary_AudioUpdate_CPU_cases=cpu['ordinary_full_AudioUpdate_cases'],
                 public_DMC_start_added_CPU_cycles=cpu['public_DMC_cycle_delta'], native=rows,
                 tools=hashes, receipts={str(path): sha(path) for path in receipts},
                 scope='Exact original shared193-byte injury payload/rates14/13 through real Grant/Alucard contact, pending attack, pressure and Start pause/resume. One extra Alucard pressure lag frame, unchanged180updates/91draws, disclosed. Controls preserve hardware/cadence; all DMC starts add34..49 CPU cycles. Distinct Sypha sample, primary72 storage/priority and full-roster/campaign remain open.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in proof.items() if k not in ['tools', 'receipts', 'native']}, indent=2))


if __name__ == '__main__':
    main()
