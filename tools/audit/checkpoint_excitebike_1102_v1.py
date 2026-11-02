"""Keep the delivered Excitebike scope and remaining roster work explicit."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from nightly_patch_guard_v1 import check
import deliver_excitebike_1102_v1 as D


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    destination = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(destination) == D.PIN
    results = {}
    for name in ['native4', 'arthur-flower', 'shinobi-smoke', 'downloads']:
        c = D.O / name / 'capture'
        result, binding = read(c / 'result.json'), read(c / 'binding.json')
        assert result['passed'] and binding['exit_code'] == 0 and binding['ROM_sha256'] == D.PIN
        ready = read(D.O / name / 'ready.json')
        for path, digest in ready['bindings'].items():
            assert sha(path) == digest, path
        results[name] = result
    menu = read(R / 'build/playable-menu-1102-v5/inventory.json')
    assert menu['ROM_sha256'] == D.PIN and menu['installed_bytes_identical']
    hardware = read(D.O / 'downloads/capture/diagnosis.json')
    assert hardware['hardware_failures'] == 0
    performance = {p['phase']: dict(completed_updates=p['updates'],
                                   physical_frames=p['physical_frames'])
                   for p in results['downloads']['phases'] if p['phase'] in ['idle', 'right']}
    scope = ('Excitebike now confirms from roster slot29. Actual Downloads cold menu, '
             'throttle/turbo/coast/reverse, original61px backlean jump and landing pass; '
             'native CHR/palette/HUD/OAM checks pass. Combined Arthur natural flower/torch '
             'and unchanged Shinobi cold idle/walk/OAM smoke pass. Full1-1 for Excitebike '
             'and fresh full-stage Arthur combat qualification remain incomplete.')
    delivery_path = D.O / 'delivery.json'
    delivery = read(delivery_path)
    delivery.update(downloads_launch_verified=True,
                    after_downloads_launch_patch_guard=check(destination),
                    Shinobi_smoke=results['shinobi-smoke'])
    delivery_path.write_text(json.dumps(delivery, indent=2) + '\n')
    installed = dict(installed=True, ROM_sha256=D.PIN,
                     previous_sha256=delivery['previous_sha256'],
                     destination=str(destination), candidate='build/excitebike-pose-1101-v3/current3.nes',
                     backup_created=False, downloads_launch_verified=True,
                     patch_guard=check(destination), complete=False,
                     character_selection='Excitebike: row4, column6 (slot29). Prince alternate remains locked.',
                     controls='Right throttle, B turbo, A jump, Up/Down lean; Left reverses travel after stopping.',
                     native_scope=scope, native_hardware_checks=hardware['hardware_checks'],
                     native_hardware_failures=0, idle_walk_measurement=performance,
                     helpers_added=False)
    p = R / 'docs/qa/continuation-current.json'
    q = read(p)
    q['installed_nightly'] = installed
    ex = q['excitebike_native_followup']
    ex.update(status='INSTALLED_NATIVE_CONTROLS_GRAPHICS_PASS_FULL_STAGE_OPEN',
              ROM_sha256=D.PIN, candidate=installed['candidate'], native4=scope,
              selection=installed['character_selection'], controls=installed['controls'],
              source_checkpoint='docs/qa/checkpoints/2026-11-02/excitebike-source-v1',
              next='Continue full1-1 with authentic jump/terrain before deciding whether native helper platforms are needed. Prince/Bub/Bob source integrations remain active.')
    f = q.get('roster_integration_followup', {})
    f['installed_ROM_sha256'] = D.PIN
    f['excitebike'] = dict(installed=True, ROM_sha256=D.PIN, verified=scope,
                          full_stage=False, helpers_added=False)
    if 'arthur' in f:
        f['arthur'].update(ROM_sha256=D.PIN, candidate=installed['candidate'],
                           verified='Combined exact379590 natural flower and B-driven torch pass1173frames, lives2to2. All Arthur wall/pickup bytes preserved.',
                           remaining='Fresh full1-1 combat and all other earned powerups/modes remain open.')
    if 'shinobi' in f:
        f['shinobi'].update(ROM_sha256=D.PIN, candidate=installed['candidate'],
                            verified='Current combined cold-menu/idle/walk/OAM smoke passes606frames. Previous6f319 full1-1 proof is historical; source motion/body data retained while shot gate/bbox ingress shifted in the documented one-byte resident expansion.')
    f['menu_audit'] = dict(receipt='build/playable-menu-1102-v5/inventory.json',
                          distinct_names=menu['distinct_named_entries'],
                          confirmable_names=menu['confirmable_named_entries'],
                          blocked=sorted({row['name'] for row in menu['rows'] if not row['confirm_starts']}),
                          absent=menu['requested_names_absent'],
                          scope='Compiled Select/Start/A admission only; native stage qualification remains separate.')
    q['completion'] = ('ACTIVE_INCOMPLETE. Excitebike is newly playable in the delivered WIP. '
                       'Prince remains locked and eight requested identities are absent. '
                       'Every-character1-1, every-powerup, remaining source abilities/audio, '
                       'lag reduction and helper-assisted crossing qualification remain required.')
    q['previous_goal_turn_classification'] = 'progress'
    p.write_text(json.dumps(q, indent=2) + '\n')
    checkpoint = R / 'docs/qa/checkpoints/2026-11-02/excitebike-nightly-v1'
    checkpoint.mkdir(parents=True, exist_ok=True)
    receipt = dict(installed=installed, native_results=results,
                   menu_summary=f['menu_audit'], complete=False)
    (checkpoint / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    doc = R / 'docs/qa/helper-platform-inventory-1101.md'
    text = doc.read_text(encoding='utf-8')
    note = ('\nNovember2: current nightly379590 adds playable Excitebike. '
            'No helper platforms were added; its full1-1/tall-pipe qualification '
            'is still open. The source placements listed above are unchanged.\n')
    if note not in text:
        doc.write_text(text + note, encoding='utf-8', newline='\n')
    print(json.dumps(dict(installed=True, ROM_sha256=D.PIN,
                          downloads_verified=True, goal_complete=False,
                          confirmable_names=menu['confirmable_named_entries'])))


if __name__ == '__main__':
    main()
