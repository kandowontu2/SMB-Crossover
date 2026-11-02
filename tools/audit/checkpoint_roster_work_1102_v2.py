"""Preserve DK Jr source and bounded current-native performance evidence."""
import hashlib
import json
import zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/roster-checkpoint-1102-v2'
PIN = 'cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    O.mkdir(exist_ok=True)
    source = R / 'build/dkjr-source-1102-v1'
    report = read(source / 'source-report.json')
    assert report['component_bytes'] == 4853 and report['CPU_cases'] == 11326
    assert report['total_CHR_bytes'] == 1728 and report['natural_NMI_frames'] == 640
    for p, digest in report['source_files'].items():
        assert sha(R / p) == digest, p
    for p, digest in report['outputs'].items():
        assert sha(source / p) == digest, p
    cp = R / 'docs/qa/checkpoints/2026-11-02/dkjr-source-core-v1'
    cp.mkdir(parents=True, exist_ok=True)
    archive = cp / 'inputs.zip'
    assert not archive.exists()
    members = {}
    for name in ['component.s', 'component.cfg', 'component.bin', 'component.lbl',
                 'component-layout.json', 'CPU.json', 'body.chr', 'body-poses.json', 'source-report.json']:
        members['generated/' + name] = (source / name).read_bytes()
    # Recovery and oracle code remain plain Git source; preserve generated
    # component/art contracts without retaining a complete donor ROM or media.
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in members.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    manifest = dict(source_only=True, native_playable=False, archive_SHA256=sha(archive),
                    archive_bytes=archive.stat().st_size,
                    members=[dict(path=n, bytes=len(v), SHA256=hashlib.sha256(v).hexdigest())
                             for n, v in members.items()],
                    source_files=report['source_files'], no_ROM_or_media=True,
                    scope='Original source component and art only. Ten stage/service imports are explicit oracle boundaries, '
                          'not native adapters. No resource grant, menu, gameplay, IRQ or helper traversal proof.')
    (cp / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (cp / 'commit-files.txt').write_text('\n'.join(report['source_files']) + '\n', encoding='utf-8')
    packet_root = R / 'build/empty-screen-lag-1102-v1'
    packets = read(packet_root / 'packets.json')
    rows = []
    for p in packets:
        target = R / p['directory']
        result, binding, ready = [read(target / n) for n in ['capture/result.json', 'capture/binding.json', 'ready.json']]
        assert binding['exit_code'] == 0 and binding['ROM_sha256'] == PIN and result['passed']
        for path, digest in ready['bindings'].items():
            assert sha(path) == digest, path
        assert all(v['max_visible_enemies'] == v['max_active_slots'] == 0 for v in result['measurements'])
        rows.append(dict(result=result, binding=binding, ready_SHA256=sha(target / 'ready.json')))
    hp = R / 'build/hogan-walk-diagnostic-1102-v1/native'
    hogan, hbinding = [read(hp / n) for n in ['capture/result.json', 'capture/binding.json']]
    assert hogan['passed'] and hbinding['exit_code'] == 0 and hbinding['ROM_sha256'] == PIN
    assert hogan['measurements'][1]['last_x'] == 92
    native = dict(ROM_SHA256=PIN, controller_only=True, measured_identities=9, rows=rows,
                  extended_Hogan=dict(result=hogan, binding=hbinding,
                      passive_trace_SHA256=sha(hp / 'capture/input-source-export.json')),
                  scope='Opening only, all measured active and visible enemy slots zero. '
                        '180 physical idle frames then40 walking frames; longer Hogan replay uses180 walking frames. '
                        'Ratios measure native Main updates, not host emulator rendering speed. '
                        'No all-roster, full-stage, powerup, graphic or performance-completion claim.',
                  graphical_followup='Metal Storm screenshot shows MARIO HUD and body at far left while native worldX77. '
                                       'Investigate actual graphics/HUD ingresses; timing pass does not qualify visuals.')
    np = R / 'docs/qa/checkpoints/2026-11-02/empty-screen-lag-v1'
    np.mkdir(parents=True, exist_ok=True)
    (np / 'receipt.json').write_text(json.dumps(native, indent=2) + '\n', encoding='utf-8')
    lines = ['# Empty-opening performance — November 2', '',
             'Exact installed MMC5 SHA256: `' + PIN + '`.', '',
             'Controller-only measurements in 1-1, with zero active or visible enemy slots. '
             'Each cold launch settles, measures 180 physical idle frames, then holds Right for 40 physical frames. '
             'The percentage is Main updates per physical frame. This does not test a whole level.', '',
             '| Character | Idle updates | Walking updates | Walking displacement |',
             '| --- | ---: | ---: | ---: |']
    for row in rows:
        result = row['result']
        a, b = result['measurements']
        lines.append(f'| {result["character"]} | {100*a["updates_per_frame"]:.1f}% | '
                     f'{100*b["updates_per_frame"]:.1f}% | {b["last_x"]-b["first_x"]} px |')
    lines += ['', 'The longer Hogan replay confirms movement: X40 → X92 over 180 physical frames '
              '(92 Main updates, 51.1%), with correct held Right reaching the original frame handler. '
              'The initial 40-frame check alone was too short to establish whether movement worked. '
              'His delayed start and slowdown remain under review.', '',
              'The single Metal Storm screenshot also reveals a visual issue: the HUD says MARIO and '
              'the visible sprite is at the left edge while native world X is 77. The timing measurement '
              'does not validate his graphics. This needs a separate actual OAM/CHR/graphics ingress check.', '',
              'Every measured run retains lives 2 → 2. Mario, Donatello and Papa reach one update per frame '
              'in this opening. The slower source integrations remain performance work; no thresholds were '
              'relaxed to call them fixed. Full roster routes and every earned powerup remain required.', '',
              'Compact evidence: `docs/qa/checkpoints/2026-11-02/empty-screen-lag-v1/receipt.json`. '
              'Captures stay in the bounded task roots; one PNG per run, no videos.', '']
    (R / 'docs/qa/empty-screen-lag-1102-v1.md').write_text('\n'.join(lines), encoding='utf-8')
    p = R / 'docs/qa/continuation-current.json'
    q = read(p)
    q['DKJr_source_followup'] = dict(source_checkpoint=str(cp.relative_to(R)),
        status='ORIGINAL_SOURCE_COMPONENT_ONLY', code_bytes=4853, state_bytes=2048,
        CHR_bytes=1728, CPU_cases=11326, original_jump_rise=15,
        native_playable=False, helper_placed=False,
        remaining='Actual host terrain/vine/fruit/defeat/ISR and resource integration; native 1-1 with verified helpers if needed.')
    q['Bub_Bob_resource_followup'].update(
        resident_storage_grant='docs/qa/allocations/common-cold-1102-v1.json',
        helper_row_grant='docs/qa/allocations/bubble-helper-row-1102-v2.json',
        frontend_grant='docs/qa/allocations/bub-menu-1102-v1.json',
        private_code_used_bytes=8158,
        remaining='Actual vector/scene/contact/AI and new menu bindings remain unwired. Shared owner frame and '
                  'nine-row immutable helper copy are being qualified. Selector bit7 is conditional until '
                  'CF/BT palette-marker and real Start-mask rewrites pass. No new character admission.')
    q['roster_integration_followup']['active_helpers'] = dict(
        arthur_sol61='Prince source ledge-catching and actual host callbacks/codec fit.',
        excitebike_sol61='Bub/Bob real frontend, selector/Start/retained palette closure.',
        shinobi_sol61='Bub/Bob shared owner loader and actual native service/contact integration.')
    q['empty_screen_performance_followup'] = dict(note='docs/qa/empty-screen-lag-1102-v1.md',
        receipt=str((np / 'receipt.json').relative_to(R)), ROM_SHA256=PIN,
        measured_identities=9, full_stage=False, no_lag_completion=False,
        next='Profile heavy idle integrations and inspect Metal Storm actual OAM/CHR/HUD placement.')
    q['previous_goal_turn_classification'] = 'progress'
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(DKJr_source_bytes=archive.stat().st_size, native_cases=9,
                          graphics_followup='Metal Storm', goal_complete=False)))


if __name__ == '__main__':
    main()
