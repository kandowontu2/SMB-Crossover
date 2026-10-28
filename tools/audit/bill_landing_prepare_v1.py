"""Two identical-policy Bill readies and bounded real-CPU input contracts. No native."""
from pathlib import Path
import argparse
import contextlib
import io
import json
import re
import sys

R = Path(__file__).resolve().parents[2]
B = R / 'build'
sys.path.insert(0, str(R / 'tools/audit'))
import bill_early_cache_cpu_v1 as H
import current_roster_compact_11_v1 as route

POLICY = R / 'tools/playthroughs/roster_bill_landing_v1.lua'
PROOF = B / 'bill_landing_source.json'
ROM = [(B / 'zelda2_easy_glove.nes', '32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0', 'baseline'),
       (B / 'bill_inert_pool.nes', '44204c9b573a82dd4838df1821afeaad8ffab8b264ebb234f31a8e156434ff5a', 'candidate')]
put = lambda p, q: p.write_text(json.dumps(q, indent=2) + '\n', newline='\n')


def buttons(q, mask):
    q.set('SavedJoypadBits', mask)
    q.set('A_B_Buttons', mask & 0xc0)


def invoke(q, name):
    return H.run(q, name)[0]


def main():
    assert not PROOF.exists(), 'Preserve original source controls'
    source = POLICY.read_text()
    assert 'c.poll' not in source and not re.search(r'emu\.|io\.|\b(?:write|setState)\s*\(', source)
    original = R / 'tools/playthroughs/roster_samus_contra.lua'
    assert route.sha(original) == '17b0683a72af2046c7a17f9d16ccf3b0a8322eca7a55a8c0000b9f4a22208847'
    bundles = []
    for path, expected, _ in ROM:
        assert route.sha(path) == expected
        bundles.append(H.scoped_load(path))
    facts = []
    for b, (path, expected, _) in zip(bundles, ROM):
        for name in ('RosterMovement', 'RosterMovement::ImmediateInput', 'RosterMovement::Left',
                     'RosterMovement::Speed', 'RosterWeapons', 'BillSourceProjection'):
            at = H.location(b, name)
            size = int(b['syms'][name].get('size', 0))
            facts.append(dict(ROM=expected, label=name, pc=H.address(b, name), bank=(at-16)//8192,
                              first_bytes=list(b['raw'][at:at+8]), declared_size=size))
    movement = []
    for (path, expected, _), b in zip(ROM, bundles):
        for y, vy, face in [(96, 1, 1), (131, 4, 1), (171, 5, 1), (131, 4, 2)]:
            states = []
            for mask in (0, 2):
                q = H.setup(b, enemies=0)
                q.put(Player_State=1, Player_X_Position=52, Player_PageLoc=3,
                      Player_Y_Position=y, Player_Y_Speed=vy, PlayerFacingDir=face,
                      BillBodyPrevValid=1, RgDoubleJump=128, MmVX=0, MmVY=0)
                q.set('MmVX', 0x40, 1)
                q.set('MmVX', 1, 2)
                q.set('MmVY', 0, 1)
                q.set('MmVY', vy, 2)
                buttons(q, mask)
                invoke(q, 'RosterMovement')
                actual = [q.get('MmVX', i) for i in range(3)]
                assert actual == ([0, 64, 1] if mask == 0 else [0, 192, 254]), (mask, actual)
                assert q.get('PlayerFacingDir') == (face if mask == 0 else 2)
                states.append(dict(mask=mask, VX_Q16=actual,
                                   x=q.get('Player_X_Position')+256*q.get('Player_PageLoc'),
                                   y=q.get('Player_Y_Position'), state=q.get('Player_State')))
            movement.append(dict(ROM=expected, start_y=y, vy=vy, facing=face, outcomes=states))
    shots = []
    for (path, expected, _), b in zip(ROM, bundles):
        for face in (1, 2):
            q = H.setup(b, enemies=0)
            q.put(Player_State=0, Player_Y_Position=176, PlayerFacingDir=face,
                  BillBodyPrevValid=1, RgPreviousButtons=64, PreviousA_B_Buttons=64)
            # Actual release consumer first, then physical fresh press. CPU
            # fixture state is disclosed; no native route setup is introduced.
            buttons(q, 4)
            invoke(q, 'RosterMovement')
            assert q.get('RgCrouch') == 1
            invoke(q, 'RosterWeapons')
            assert q.get('RgPreviousButtons') == 4 and not any(q.get('RgShotType', i) for i in range(10))
            q.set('PreviousA_B_Buttons', q.get('A_B_Buttons'))
            buttons(q, 68)
            invoke(q, 'RosterMovement')
            assert q.get('RgCrouch') == 1 and [q.get('MmVX', i) for i in range(3)] == [0, 0, 0]
            invoke(q, 'RosterWeapons')
            active = [i for i in range(10) if q.get('RgShotType', i)]
            assert len(active) == 1 and q.get('RgAim') == 5, (active, q.get('RgAim'))
            assert q.get('RgPreviousButtons') == 68
            shots.append(dict(ROM=expected, facing=face, real_release_history=4, real_press_history=68,
                              shot_slot=active[0], kind=q.get('RgShotType', active[0]),
                              prone=1, aim=5, logical_VX=[0, 0, 0]))
    # The two real images have different sampling/input histories. These are
    # typed source contracts, not a reconstruction of the unlogged kill/contact.
    controls = dict(source_contracts_passed=True, native_run=False, Lua_VM_executed=False,
        policy_sha256=route.sha(POLICY), original_policy_sha256=route.sha(original),
        ROMs=[dict(path=str(p), sha256=h) for p, h, _ in ROM],
        compiled_owner_metadata=facts, actual_movement_cases=movement, actual_release_press_cases=shots,
        admission=dict(identity='Bill variant0 only', mode='Hard native readiness', world=0, level=0,
                       enemy='native nearest live Goomba6/state<2', phase='descending then grounded',
                       floor='reads every16px column from retreat48 to approach32, plus enemy8, at a common blocking row',
                       writes='Only normal physical controller output. No emulated memory, actors, resources or timers.'),
        limits=['Lua was statically inspected, not executed in a standalone Lua VM.',
                'The source tests seed typed CPU input/pose/history to prove movement and real B-consumer contracts only.',
                'No exact hostile collision/kill writer from the original native death was captured.',
                'No proof of universal safety, enemy defeat, capacity availability or whole-route performance.',
                'Parent controller still handles all other contexts; its private counters advance once per poll even while this wrapper overrides output.'],
        dependencies={str(p): route.sha(p) for p in [Path(__file__), Path(H.__file__), Path(route.__file__),
                    POLICY, original, R / 'tools/playthroughs/roster_samus_contra_nav.lua',
                    B / 'bill_inert_pool_native_review.json']})
    put(PROOF, controls)
    old_ready = json.loads((B / 'verification/bill-inert-pool326-hard-ready-v2/ready.json').read_text())
    packets = []
    for path, expected, label in ROM:
        out = B / f'verification/bill-landing-{label}326-hard-ready-v1'
        assert not out.exists(), 'Do not overwrite earlier evidence'
        with contextlib.redirect_stdout(io.StringIO()):
            route.prepare(argparse.Namespace(identity='bill', mode='hard', rom=path,
                          expected_sha256=expected, output=out, frames=8000, policy=POLICY, replay=None))
        rp = out / 'ready.json'
        ready = json.loads(rp.read_text())
        assert ready['config']['replay'] is None
        # Same literal shared observer, mechanics and guard body: only exact
        # generated configuration changes. No extra callbacks are installed.
        original_config = 'ROSTER_CONFIG=' + route.lua(ready['config']) + '\n'
        before_config = 'ROSTER_CONFIG=' + route.lua(old_ready['config']) + '\n'
        assert (out / 'run.lua').read_text().replace(original_config, before_config, 1) == (B / 'verification/bill-inert-pool326-hard-ready-v2/run.lua').read_text()
        put(out / 'command.json', ready['command'])
        ready['source_contracts'] = dict(path=str(PROOF), sha256=route.sha(PROOF), source_only=True,
                                        no_native_safety_claim=True, guard_body_reverse_exact=True)
        ready['environment'] = old_ready['environment']
        ready['storage'] = dict(total_per_run_bytes=2_000_000_000, total_per_run_files=64,
            one_compact_PPU_container_bytes=512*1024*1024, native_PNG_files=0,
            maximum_offline_distinct_selected_epochs_including_diagnostics=8,
            central_capture_lease_required=True)
        ready['maximum_native_launches'] = 1
        ready['native_grant_required'] = True
        deps = {Path(p) for p in ready['bindings']}
        deps.update([Path(__file__), Path(H.__file__), PROOF, POLICY, out / 'command.json',
                     B / 'bill_inert_pool_native_review.json', B / 'bill_inert_pool_final.json',
                     B / 'bill_inert_pool_verify_build.json', B / 'bill_inert_pool_ordinary.json',
                     Path('C:/Mesen2/Mesen.exe'), Path('C:/Mesen2/MesenCore.dll'), Path('C:/Mesen2/settings.json')])
        ready['bindings'] = {str(p): route.sha(p) for p in sorted(deps)}
        put(rp, ready)
        packets.append(dict(profile=label, ready=str(rp), sha256=route.sha(rp), bindings=len(deps),
                            command=str(out / 'command.json')))
    proof = dict(source_contracts=str(PROOF), source_contracts_sha256=route.sha(PROOF),
                 policy=str(POLICY), policy_sha256=route.sha(POLICY), readies=packets,
                 native_run=False, no_adoption=True)
    put(B / 'bill_landing_handoff.json', proof)
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
