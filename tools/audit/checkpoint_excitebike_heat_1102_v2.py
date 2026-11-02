"""Record exact delivered recovery evidence and the full-stage result."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from nightly_patch_guard_v1 import check
import deliver_excitebike_heat_1102_v2 as D


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def native(name):
    p = D.O / name
    result, binding = read(p / 'capture/result.json'), read(p / 'capture/binding.json')
    assert binding['exit_code'] == 0 and binding['ROM_sha256'] == D.PIN and result['passed']
    for path, digest in read(p / 'ready.json')['bindings'].items():
        assert sha(path) == digest, path
    return result


def main():
    dest = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(dest) == D.PIN
    controls, heat, downloads = [native(n) for n in ['native5', 'heat-native2', 'heat-downloads']]
    full = native('full11-v5')
    assert full['world'] == 0 and full['level'] == 1 and full['engine'] == 8
    assert full['initial_four_pipes_passed'] == 4 and full['three_gaps_passed'] == 3
    assert full['initial_lives'] == full['final_lives'] == 2
    assert full['third_pipe_top_support'] and full['fourth_pipe_top_support']
    actual_heat = read(D.O / 'heat-downloads/capture/heat.json')
    assert all(actual_heat[n] for n in ['heat_seen', 'recovery5_seen', 'returned_recovery0', 'resumed_motion'])
    delivery_path = D.O / 'heat-delivery.json'
    delivery = read(delivery_path)
    delivery.update(downloads_launch_verified=True, after_downloads_launch_patch_guard=check(dest),
                    full11=full, downloads_result=downloads)
    delivery_path.write_text(json.dumps(delivery, indent=2) + '\n', encoding='utf-8')
    qpath = R / 'docs/qa/continuation-current.json'
    q = read(qpath)
    scope = ('Excitebike original timer divider, cooling, lane and throttle release restored. '
             'Controls, native 61px jump, graphics and real overheat recovery pass on this exact candidate. '
             'Actual Downloads repeats the earned overheat → recovery 5 → 0 → resumed motion, lives 2 → 2. '
             f'Full 1-1 reaches active 1-2 in {full["frames"]} physical frames, all four pipes and three gaps, '
             'lives 2 → 2, no helpers. Arthur weapon fix bytes are retained; its full-stage proof remains '
             'attached to parent d8a87050.')
    q['installed_nightly'] = dict(installed=True, ROM_sha256=D.PIN,
                                  previous_sha256=D.PARENT, destination=str(dest),
                                  candidate='build/excitebike-pose-1101-v3/current4.nes',
                                  backup_created=False, downloads_launch_verified=True,
                                  patch_guard=check(dest), native_scope=scope, complete=False,
                                  character_selection='Excitebike row4,column6; Arthur row4,column8. Reopen ROM and start fresh.',
                                  helpers_added=False)
    ex = q['excitebike_native_followup']
    ex.update(status='INSTALLED_NATIVE_RECOVERY_AND_FULL11_PASS', ROM_sha256=D.PIN,
              candidate=q['installed_nightly']['candidate'], native_recovery=delivery['native_heat'],
              full11=full, source_continuation_checkpoint='docs/qa/checkpoints/2026-11-02/excitebike-continuation-v2',
              next='Complete shortcut route, earned powerups/original audio and remaining character integrations.')
    ex['full11_v4_observer_negative'] = ('Allpipes/gaps reached, then an overly strict observer latched Unexpected Main epoch gap at actualscene reset. '
                                         'Separatev5 permits only independently observed native task/level/area transitions and retains actualactive1-2 requirement.')
    f = q.get('roster_integration_followup', {})
    f['installed_ROM_sha256'] = D.PIN
    f['excitebike'] = dict(installed=True, ROM_sha256=D.PIN, verified=scope,
                          full_stage=True, helpers_added=False,
                          remaining='Shortcut, every earned powerup and original audio remain incomplete.')
    f['next'] = ('Continue Prince, Bub/Bob and the other absent identities. Complete every-character '
                 '1-1 and every-powerup testing; source-only components and menu admission do not '
                 'establish native playability. Preserve the installed cf1412eb nightly.')
    f['active_helpers']['excitebike_sol61'] = 'Donkey Kong Jr. original actor and art recovery.'
    q['completion'] = ('ACTIVE_INCOMPLETE. Arthur and Excitebike now have no-helper full1-1 proofs. '
                       'Prince/Bub/Bob and absent requested identities, every-character/every-powerup, '
                       'remaining source abilities/audio and lag work remain required.')
    q['previous_goal_turn_classification'] = 'progress'
    qpath.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/excitebike-recovery-native-v2'
    cp.mkdir(parents=True, exist_ok=True)
    receipt = dict(delivery=delivery, native_controls=controls, native_heat=heat,
                   scenes=read(D.O / 'full11-v5/capture/scene.json'), complete=False)
    (cp / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    doc = R / 'docs/qa/helper-platform-inventory-1101.md'
    text = doc.read_text(encoding='utf-8')
    import re
    text = re.sub(r'Current nightly SHA256: `[^`]+`\.', f'Current nightly SHA256: `{D.PIN}`.', text, count=1)
    text += (f'\nExcitebike now clears full non-shortcut 1-1 into active 1-2 on cf1412eb in {full["frames"]} '
             'physical frames, lives 2 → 2, all four pipes and three gaps, with no added or inherited helpers. '
             'Third and fourth 64px pipe support contacts are recorded in the native receipt.\n')
    doc.write_text(text, encoding='utf-8', newline='\n')
    print(json.dumps(dict(installed=True, ROM_sha256=D.PIN, downloads_verified=True,
                          full11_pass=True, frames=full['frames'], complete=False)))


if __name__ == '__main__':
    main()
