"""Exact second-failure diagnostic on frozen d49f; prepare only."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json

from current_roster_compact_11_v1 import prepare, lua, linked

R = Path(__file__).resolve().parents[2]
B = R/'build'
SHA = 'd49f265deccb847cde8f6d499c0cd4aec2aeb373226418301d287761aa19398d'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    old = B/'verification/chip-d49f-easy-v1'
    receipt = json.loads((old/'ready.json').read_text())
    assert all(sha(p) == h for p, h in receipt['bindings'].items())
    result = json.loads((old/'result.json').read_text())
    assert result['ROM_sha256'] == SHA and not result['passed']
    assert result['frames'] == 1476 and result['polls'] == 1475
    assert result['reason'] == 'Active render enable precedes pre-render vertical reload'
    rom = B/'chip_hud_queue.nes'
    assert sha(rom) == SHA
    raw, syms, address, location, _ = linked(rom)
    cfg = json.loads((old/'startup-config.json').read_text())
    assert cfg['ROM_sha256'] == SHA
    cfg['start_frame'], cfg['cutoff_frame'] = 1470, 1477
    for name, value in cfg['ram'].items():
        assert address(name) == value
    for h in cfg['hooks'].values():
        at = location(h['source_symbol'])+h['source_delta']
        assert address(h['source_symbol'])+h['source_delta'] == h['pc']
        assert raw[at:at+len(h['bytes'])] == bytes(h['bytes'])
        for bank in h['banks']:
            start = 16+bank*8192+(h['pc']&8191)
            assert raw[start:start+len(h['bytes'])] == bytes(h['bytes'])
    out = B/'verification/chip-d49f-late-vram-probe-v1'
    prepare(SimpleNamespace(rom=rom, expected_sha256=SHA, output=out, identity='chip', mode='easy',
        frames=1500, policy=Path(receipt['config']['policy']), replay=old/'inputs.csv'))
    config = out/'startup-config.json'
    config.write_text(json.dumps(cfg, indent=2)+'\n', newline='\n')
    module = R/'tools/audit/chip_render_vram_probe_v1.lua'
    harness = R/'tools/audit/current_roster_compact_11_v1.lua'
    run = out/'run.lua'
    text = run.read_text()
    needle = 'dofile('+lua(harness.as_posix())+')'
    assert text.count(needle) == 1
    append = ('PROTO_STARTUP_VRAM_TIMING='+lua(cfg)+'\n'
        'local previousClose=ROSTER_CONFIG.bass_close\n'
        'local chipClose=dofile('+lua(module.as_posix())+')\n'
        'ROSTER_CONFIG.bass_close=function()local q=previousClose and previousClose()or{};'
        'q.chip_vram_probe=chipClose();return q end\n')
    run.write_text(text.replace(needle, append+needle), newline='\n')
    ready = out/'ready.json'
    z = json.loads(ready.read_text())
    z['bindings'][str(run)] = sha(run)
    for p in (Path(__file__), config, module, old/'ready.json', old/'result.json', old/'events.jsonl',
              old/'trace.csv', old/'startup-config.json', old/'launch.json'):
        z['bindings'][str(p)] = sha(p)
    z['scope'] = dict(prepared_only=True, native_run=False, original_FALSE_retained=True,
        expected_first_failure='PPU1476 scanline0/dot217; CPU43926320; physical127 E00B',
        exact_inputs='Original1475 poll/frame/mask rows; no invented tail or controller correction',
        observation='Same qualified startup-static read-only NMI/VRAM/CHR/DMA/PPUMASK observer; PPU1470..1477 only',
        unchanged='Original source/hardware/actual256DMA/E3/CHR/SMC/IRQ/stack/deadline guards and input workload',
        output='One bounded CSV in addition to unchanged original compact capture; no extra PNGs or source/runtime trees',
        limit='Diagnostic only; must preserve same actual failure or unmodified replay-exhaustion negative. No second source patch before actual packet attribution.')
    ready.write_text(json.dumps(z, indent=2)+'\n', newline='\n')
    assert all(sha(p) == h for p, h in z['bindings'].items())
    (out/'command.json').write_text(json.dumps(z['command'], indent=2)+'\n', newline='\n')
    print(json.dumps(dict(prepared_only=True, ready=str(ready), sha256=sha(ready), bindings=len(z['bindings']),
                         command=str(out/'command.json')), indent=2))


if __name__ == '__main__':
    main()
