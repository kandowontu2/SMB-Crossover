"""Independent complete controller replay with the physical-frame graphics/audio audit."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-el-bass-fixed-gl'
    out.mkdir(exist_ok=False)
    discovery = R / 'build/roster-through-2-2/root49gk-bass-live-9-v0-mmc3'
    manifest = json.loads((discovery / 'manifest.json').read_text())
    result = manifest['result']
    assert result['cleared'] and result['all_six_stages'] and result['deaths'] == 0
    assert result['frames'] == 26689 and result['polls'] == 26688
    assert result['stage_entries']['1-2'] == 26665
    assert not manifest['full_frame_audit'] and not manifest['verified_through_2_2']
    rom = V / 'root49-link-watch-ej/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == manifest['rom_sha256'] == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
    policy = V / 'root49-el-bass-pipes-fw/policy.lua'
    fw = json.loads((policy.parent / 'binding.json').read_text())
    assert sha(policy) == fw['policy_sha256']
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'),
        '--character', '9', '--mapper', 'mmc3', '--rom', str(rom),
        '--tag', 'root49gl-bass-fixed', '--policy', str(policy),
        '--replay', str(discovery / 'inputs.csv'), '--frames', '36000',
        '--timeout', '900', '--workspace-cap-gb', '60']
    report = dict(status='PREPARED_INDEPENDENT_EL_BASS_FULL_FIXED_AUDIT',
        script_sha256=sha(__file__), discovery_manifest_sha256=sha(discovery / 'manifest.json'),
        discovery_inputs_sha256=sha(discovery / 'inputs.csv'),
        discovery_trace_sha256=sha(discovery / 'trace.csv'), ROM_sha256=sha(rom),
        command=command, emulated_writes=False, state_loads=False,
        root_Bass_phase_prior_measured_bytes=551_672_272,
        root_Bass_phase_prior_ceiling_bytes=600_000_000,
        root_Bass_phase_new_ceiling_bytes=700_000_000,
        allocation_reason='Retain all negatives, both ordinary water profiles and the independent full fixed audit with room for the separate mapper transfer. Global60GB remains enforced.',
        final_movie=False, all_arsenal_claim=False, goal_complete=False)
    (out / 'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    rc = subprocess.run(command, cwd=R).returncode
    (out / 'host-result.json').write_text(json.dumps(dict(exit=rc), indent=2)+'\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
