"""Deliver Arthur's native-tested weapon tail and record the actual launch."""
import argparse
import json
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha
from nightly_patch_guard_v1 import check
import check_arthur_side_clamp_1101_v8 as C

O = R / 'build/arthur-weapon-nightly-1102-v15'
S = R / 'build/arthur-side-clamp-1101-v8'
PIN = 'd8a87050beefefe96869ebd4d188beeb52733241cd2c0fa64392a55ec8ebca05'
PARENT = '37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c'
DEST = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def native(p):
    result, binding = read(p / 'capture/result.json'), read(p / 'capture/binding.json')
    assert result['passed'] and binding['exit_code'] == 0 and binding['ROM_sha256'] == PIN
    for path, digest in read(p / 'ready.json')['bindings'].items():
        assert sha(path) == digest, path
    return result


def install():
    O.mkdir(exist_ok=True)
    rom = S / 'weapon-tail-candidate.nes'
    assert sha(rom) == PIN
    cpu = read(S / 'weapon-tail-CPU.json')
    assert cpu['passed'] and cpu['proposed_candidate_sha256'] == PIN
    target = native(S / 'weapon-tail-native')
    route = native(R / 'build/arthur-weapon-route-1102-v15/native')
    assert route['level'] == 1 and route['initial_four_pipes_passed'] == 4
    assert route['three_gaps_passed'] == 3 and route['lives_start'] == route['lives_end'] == 2
    ingress = read(S / 'weapon-tail-native/capture/weapon-ingress.json')
    assert ingress['ingress']['HandleEnemyFBallCol'] > 0
    assert ingress['ingress']['ShellOrBlockDefeat'] > 0 and ingress['contact_carry_set'] > 0
    ref = S / 'weapon-tail-native/controller.lua'
    text = ref.read_text(encoding='utf-8')
    b = C.scoped_load(rom)
    # The observer registers hooks by names in an explicit string list.
    # Include those dynamic names as well as direct L/B and r() references.
    names = {n for n in re.findall(r"['\"]([A-Za-z_]\w*)['\"]", text) if n in b['syms']}
    names |= set(re.findall(r'\b[LB]\.(\w+)', text))
    prefix = [f'L[{json.dumps(n)}]={C.address(b,n)}' for n in sorted(names)]
    for n in sorted(names):
        try:
            bank = (C.location(b, n) - 16) // 8192
        except (KeyError, AssertionError):
            continue
        if 0 <= bank < 128:
            prefix.append(f'B[{json.dumps(n)}]={bank}')
    assert sha(DEST) == PARENT
    before = check(DEST)
    DEST.write_bytes(rom.read_bytes())
    after = check(DEST)
    assert sha(DEST) == PIN
    prepare(O / 'downloads', rom, '\n'.join(prefix) + '\n' + text,
            [Path(__file__), ref, DEST, S / 'weapon-tail-CPU.json'],
            expected=PIN, timeout=150, allow_interactive=True,
            scope='Actual Downloads cold Arthur selection and B-created lance/native '
                  'enemy defeat, same bounded controller and contact observer; explicit '
                  'symbols without Downloads debug sidecars. No emulated state writes '
                  'or backup. Candidate separately passes full1-1 into active1-2.')
    p = O / 'downloads/ready.json'
    ready = read(p)
    ready['ROM'] = str(DEST)
    p.write_text(json.dumps(ready, indent=2) + '\n', encoding='utf-8')
    receipt = dict(installed=True, ROM_sha256=PIN, previous_sha256=PARENT,
                   candidate=rom.relative_to(R).as_posix(), destination=str(DEST),
                   backup_created=False, downloads_launch_verified=False,
                   before=before, after=after, target=target, full11=route,
                   weapon_ingress=ingress, helpers_added=False, complete=False)
    (O / 'delivery.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(installed=True, ROM_sha256=PIN, downloads_verified=False)))


def checkpoint():
    assert sha(DEST) == PIN
    result = native(O / 'downloads')
    receipt = read(O / 'delivery.json')
    receipt.update(downloads_launch_verified=True, downloads_result=result,
                   after_downloads_launch_patch_guard=check(DEST))
    (O / 'delivery.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    p = R / 'docs/qa/continuation-current.json'
    q = read(p)
    old = q['installed_nightly']
    old.update(ROM_sha256=PIN, previous_sha256=PARENT,
               candidate=receipt['candidate'], patch_guard=check(DEST),
               native_scope='Arthur source-lance/native enemy defeat passes on exact candidate and actual Downloads. '
                            'Fresh full1-1 passes5950physicalframes into active1-2, lives2to2, allfourpipes/allthreegaps, nohelpers or sourceinjury. '
                            'Excitebike controls/graphics and prior Arthur flower/torch proofs remain attached to379590; '
                            'every Ex byte is retained outside the two Arthur-owned row34 operand bytes.',
               character_selection='Arthur: row4,column8; Excitebike remains selectable row4,column6. Start fresh after reopening ROM.')
    old['retained_Excitebike_native_proof_SHA256'] = PARENT
    for name in ['native_hardware_checks', 'native_hardware_failures', 'idle_walk_measurement']:
        old.pop(name, None)
    old['controls'] = ('Arthur: D-pad movement, A jump, fresh A press for second jump, B weapon. '
                       'Excitebike: Right throttle, B turbo, A jump, Up/Down lean; Left reverses after stopping.')
    a = q['arthur_natural_powerup_followup']
    a.update(ROM_sha256=PIN, candidate=receipt['candidate'],
             status='INSTALLED_PICKUP_AND_NATIVE_WEAPON_FIX_FULL11_PASS',
             full_stage=old['native_scope'],
             weapon_ingress_followup='Repaired only Arthur owning policy34 operand to the existing row4 worker. '
                                     'Actual ProcFireball_Bubble/tail route now reaches original contacts and genuine native enemy defeat. '
                                     'Targeted candidate and actual Downloads both pass; all other ROM bytes unchanged.')
    f = q.get('roster_integration_followup', {})
    f['installed_ROM_sha256'] = PIN
    f['arthur'] = dict(installed=True, ROM_sha256=PIN, verified=old['native_scope'],
                       candidate=receipt['candidate'], full_stage=True,
                       remaining='All earned weapon upgrades/modes/audio and shortcut route remain open.')
    q['completion'] = ('ACTIVE_INCOMPLETE. Fresh Arthur full1-1 and weapon contact pass. Excitebike recovery/fullstage, '
                       'Prince/Bub/Bob and absent requested characters, all-roster/every-powerup testing remain active.')
    q['previous_goal_turn_classification'] = 'progress'
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/arthur-weapon-tail-v15'
    cp.mkdir(parents=True, exist_ok=True)
    (cp / 'receipt.json').write_text(json.dumps(dict(delivery=receipt,
                                      CPU=read(S / 'weapon-tail-CPU.json')), indent=2) + '\n', encoding='utf-8')
    doc = R / 'docs/qa/arthur-weapon-tail-1102-v15.md'
    text = doc.read_text(encoding='utf-8')
    note = ('\n## Native delivery\n\nThe exact candidate and actual Downloads pass real source-lance/native '
            'enemy defeat. The unchanged full1-1 controller now reaches active1-2 in5950physicalframes, '
            'lives2to2, allfourpipes/allthreegaps, nohelpers and no sourceinjury. Downloads was replaced '
            'without backup; patch guards pass. All other weapons/powerups and full-roster checks remain open.\n')
    assert '## Native delivery' not in text
    doc.write_text(text + note, encoding='utf-8', newline='\n')
    print(json.dumps(dict(installed=True, ROM_sha256=PIN, downloads_verified=True,
                          full11_pass=True, goal_complete=False)))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--checkpoint', action='store_true')
    checkpoint() if ap.parse_args().checkpoint else install()
