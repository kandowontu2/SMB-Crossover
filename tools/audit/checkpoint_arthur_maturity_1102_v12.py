"""Record the exact Downloads validation and the remaining roster work."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from nightly_patch_guard_v1 import check
import deliver_arthur_maturity_1102_v12 as D


def main():
    destination = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(destination) == D.PIN
    c = D.O / 'downloads/capture'
    result = json.loads((c / 'result.json').read_text())
    binding = json.loads((c / 'binding.json').read_text())
    assert result['passed'] and binding['exit_code'] == 0 and binding['ROM_sha256'] == D.PIN
    delivery_path = D.O / 'delivery.json'
    delivery = json.loads(delivery_path.read_text())
    delivery.update(downloads_launch_verified=True,
                    after_downloads_launch_patch_guard=check(destination),
                    downloads_result=result)
    delivery_path.write_text(json.dumps(delivery, indent=2) + '\n')
    p = R / 'docs/qa/continuation-current.json'
    q = json.loads(p.read_text())
    q['installed_nightly'] = dict(delivery, complete=False,
                                  character_selection='Arthur original roster slot31, raw32. Reopen ROM and start fresh.')
    q['arthur_natural_powerup_followup'] = dict(
        ROM_sha256=D.PIN, status='INSTALLED_TARGETED_NATIVE_PASS_FULL_STAGE_OPEN',
        candidate=delivery['candidate'], note='docs/qa/arthur-maturity-1102-v12.md',
        native='Actual candidate and actual Downloads cold-menu release/maturity/collection/torch replays both pass. '
               'First flower grants original event6 and weapon68; two B presses reach original torch60times, '
               'lives2to2. Corrected side clamp retains original0/16 probes. No helpers.',
        diagnosis='Parked flower overlapped authentic contact boxes, but all397 actual HuMature calls returnedCclear. '
                  'Owned row23 now selects existing pure SEC policy; original collector still rejects immature items.',
        CPU='Wall/Ryu/foreign/IRQ checks pass. Pickup admission112, all35 other owned rows140, foreign152, actual contacts240, IRQ/lagNMI54.',
        full_stage='Previous6f319 full1-1 pass is historical. On corrected8be route, allfourpipes/allthreegaps crossed, '
                   'but complete1-1 enemy controller still fails: stop60 lands by secondKoopa1799; distance38 later2042. '
                   'No claim of a fresh full-stage clear onb9. Preserve negatives.',
        helpers='GPT-6.1 Sol xhigh: Arthur/Prince, Excitebike, Bub/Bob. Root owns Mesen queue.')
    f = q.get('roster_integration_followup', {})
    f['installed_ROM_sha256'] = D.PIN
    if 'arthur' in f:
        f['arthur'].update(candidate=delivery['candidate'], ROM_sha256=D.PIN,
                           verified=q['arthur_natural_powerup_followup']['native'],
                           remaining='Fresh full1-1 enemy route and all other earned powerups/modes remain incomplete.')
    q['completion'] = ('ACTIVE_INCOMPLETE. Arthur wall and real flower/torch repairs delivered. '
                       'Excitebike native successor, Prince and Bub/Bob integrations, absent requested identities, '
                       'every-character1-1 and every-powerup verification remain active.')
    q['previous_goal_turn_classification'] = 'progress'
    p.write_text(json.dumps(q, indent=2) + '\n')
    checkpoint = R / 'docs/qa/checkpoints/2026-11-02/arthur-wall-pickup-v12'
    checkpoint.mkdir(parents=True, exist_ok=True)
    payload = dict(delivery=delivery,
                   CPU=json.loads((D.SOURCE / 'maturity-fix-CPU.json').read_text()),
                   candidate=json.loads((D.SOURCE / 'maturity-candidate.json').read_text()),
                   limits=q['completion'])
    (checkpoint / 'receipt.json').write_text(json.dumps(payload, indent=2) + '\n')
    doc = R / 'docs/qa/arthur-maturity-1102-v12.md'
    text = doc.read_text(encoding='utf-8')
    text = text.replace('-112 ', '- 112 ').replace('-140 ', '- 140 ').replace('-152 ', '- 152 ')
    text = text.replace('-240 ', '- 240 ').replace('-54 ', '- 54 ').replace('-`', '- `')
    note = ('\n## Native delivery — November 2\n\n'
            'The exact candidate and the actual Downloads nightly both pass the '
            'unchanged controller-earned flower/torch replay: 1,173 physical '
            'frames, original event6 once, weapon68, original torch handler60 '
            'calls, lives2→2, no helpers or emulated state writes. Downloads '
            'was replaced directly with no backup; both patch guards pass. '
            'Full1-1 enemy encounters and other earned powerups remain open. '
            'Compact retained receipt: '
            '`docs/qa/checkpoints/2026-11-02/arthur-wall-pickup-v12/receipt.json`.\n')
    assert '## Native delivery — November 2' not in text
    doc.write_text(text + note, encoding='utf-8', newline='\n')
    print(json.dumps(dict(installed=True, ROM_sha256=D.PIN,
                          downloads_launch_verified=True, complete=False)))


if __name__ == '__main__':
    main()
