"""Fresh, unchanged Alucard v4 route metadata on the explicit 58-byte union.

Source preparation only. Never launches an emulator or modifies old readies.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse
import hashlib
import json

from current_alucard_bat_restore_prepare_v1 import controls
from current_roster_compact_11_v1 import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load

ROOT = Path(__file__).resolve().parents[2]
BASE = '9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
EXPECTED = 'ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    p.write_text(json.dumps(value, indent=2)+'\n', newline='\n')


def check(bindings):
    for p, h in bindings.items():
        assert sha(p) == h, ('Changed frozen input', p)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, required=True)
    ap.add_argument('--expected-sha256', required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    rom, out = a.rom.resolve(), a.output.resolve()
    assert a.expected_sha256 == EXPECTED and sha(rom) == EXPECTED
    old = ROOT/'build/verification/compact-next-alucard-9ea-easy-v4'
    old_ready = old/'ready.json'
    prior = json.loads(old_ready.read_text())
    assert sha(old_ready) == 'e318445410efa80526d08700c984443212eda5a92c39984999fe2d216dc926fb'
    assert prior['ROM_sha256'] == BASE and not prior['native_run']
    check(prior['bindings'])
    assert not (old/'result.json').exists(), 'The preserved9ea v4 remains unrun'
    assert not out.exists()
    policy = ROOT/'tools/playthroughs/current_roster_alucard_bat_restore_v3.lua'
    original_policy_sha = sha(policy)
    source = ROOT/'build/mega_proto_body_palette_9ea_build.json'
    union = json.loads(source.read_text())
    check(union['bindings'])
    assert union['parent_sha256'] == BASE and union['candidate_sha256'] == EXPECTED
    assert union['exact_disjoint_union'] and union['changed_bytes'] == 58
    assert union['body_bytes'] == 34 and union['body_bank'] == 4
    assert union['palette_bytes'] == 24 and union['palette_bank'] == 66
    parent = ROOT/'build/bill_early_cache.nes'
    before, after = parent.read_bytes(), rom.read_bytes()
    diff = [i for i, (x, y) in enumerate(zip(before, after)) if x != y]
    assert len(before) == len(after) and len(diff) == 58
    by_bank = {b: sum((i-16)//8192 == b for i in diff) for b in {4, 66}}
    assert by_bank == {4: 34, 66: 24}
    assert all((i-16)//8192 in {4, 66} for i in diff)
    assert before[:16] == after[:16] and before[16+128*8192:] == after[16+128*8192:]
    # Fresh execution is warranted because the finite model invokes actual
    # PlayerCtrl/background/CV3 calls, not because the new private Restore
    # label is assumed to be a public compatibility alias.
    cpu = controls(scoped_load(rom))
    historical = json.loads((old/'source-poll-readback-controls.json').read_text())
    assert cpu == historical, 'Fresh actual-candidate finite source outcomes must match'
    prepare(SimpleNamespace(rom=rom, expected_sha256=EXPECTED, output=out,
                            identity='alucard', mode='easy', frames=8000,
                            policy=policy, replay=None))
    ready_path = out/'ready.json'
    ready = json.loads(ready_path.read_text())
    cfg, oldcfg = ready['config'], prior['config']
    normalized = dict(cfg, out=oldcfg['out'], prefix=oldcfg['prefix'], ROM_sha256=BASE)
    assert normalized == oldcfg, 'Only target/output metadata may differ'
    assert ready['required_ram_reads'] == prior['required_ram_reads']
    assert ready['hook_copy_owners'] == prior['hook_copy_owners']
    normalize_command = [x.replace(str(out), str(old)).replace(str(rom), str(parent))
                         for x in ready['command']]
    assert normalize_command == prior['command'], 'Same controller/runtime/caps/CLI'
    put(out/'source-poll-readback-controls.json', dict(
        passed=True, source_CPU_only=True, ROM_sha256=EXPECTED,
        freshly_executed=True, historical_outcomes_exact=True, controls=cpu,
        historical_receipt_sha256=sha(old/'source-poll-readback-controls.json'),
        limits='Actual finite CPU calls only; no Lua/native scheduling, full level parser, '
               'PPU, waveform, route clear or native cadence evidence.'))
    put(out/'source-correspondence.json', dict(
        passed=True, native_run=False, original_ROM_sha256=BASE,
        candidate_ROM_sha256=EXPECTED, changed_bytes=58, by_bank=by_bank,
        header_CHR_and_every_other_bank_exact=True,
        original_ready_sha256=sha(old_ready), original_ready_unrun=True,
        controller_byteexact_sha256=original_policy_sha,
        config_delta='Only ROM hash and output/prefix paths; hooks, RAM addresses, '
                     'navigation, mechanics, assertions and8000frame cap identical.',
        legitimate_private_label_move=union['genuine_old_label_moves'],
        source_overlay=union['source_overlay'],
        source_binding_role='Current parent source bindings are provenance; three '
                            'explicit source leaves in the union receipt and real '
                            'candidate ROM/DBG supply the actual candidate inputs.',
        union_receipt=dict(path=str(source), sha256=sha(source))))
    ready.update(PREPARED_DO_NOT_RUN=True, native_run=False,
                 controller_revision=prior['controller_revision'],
                 source_execution='Fresh eight paired actual-candidate source cases: '
                                  '0/1/2/3 unconsumed restore polls, old/new controller. '
                                  'All outcomes exactly match historical9ea receipt; '
                                  'no native result transfer.',
                 original_ready_sha256=sha(old_ready), exact_disjoint_union_bytes=58)
    paths = [Path(__file__).resolve(), old_ready, old/'source-poll-readback-controls.json',
             old/'controller.patch', source,
             ROOT/'tools/audit/current_alucard_bat_restore_prepare_v1.py',
             ROOT/'tools/audit/current_alucard_bat_gap_prepare_v1.py',
             ROOT/'tools/audit/luigi_mario_profile731_cpu_v1.py',
             ROOT/'tools/audit/mario_luigi731_coefficients_v1.py',
             ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',
             ROOT/'tools/audit/check_tmnt_render_oa.py',
             ROOT/'tools/audit/robots_weapon_cpu_v1.py',
             ROOT/'src/cv3_core.s', ROOT/'src/cv3_abilities.s',
             out/'source-poll-readback-controls.json', out/'source-correspondence.json']
    paths += [Path(p) for p in union['source_overlay'].values()]
    for p in paths:
        ready['bindings'][str(p)] = sha(p)
    put(out/'command.json', dict(PREPARED_DO_NOT_RUN=True, ROOT_owns_native_lease=True,
                                 argv=ready['command']))
    ready['bindings'][str(out/'command.json')] = sha(out/'command.json')
    check(ready['bindings'])
    assert sha(policy) == original_policy_sha and sha(old_ready) == ready['original_ready_sha256']
    put(ready_path, ready)
    print(json.dumps(dict(status='PREPARED_DO_NOT_RUN', ready=str(ready_path),
                          sha256=sha(ready_path), bindings=len(ready['bindings']),
                          ROM_sha256=EXPECTED, fresh_source_cases=8)))


if __name__ == '__main__':
    main()
