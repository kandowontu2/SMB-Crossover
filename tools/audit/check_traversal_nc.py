"""Bind focused physical-pickup and obstacle fixtures to the combined ROM."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
CV3 = ROOT/'build/player-guide-agent/cv3-pipe-private/adoption-packet/scripts'
Z2 = ROOT/'build/verification/new-pipe-playability-agent/handoff-z2-pipes-h'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rom, output = args.rom.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('nc_traversal_runner', ROOT/'tools/run_mesen.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    cases = [
        ('zelda2-physical-jump', Z2/'z2-food-route-g.lua', '', 'z2-food-route-g-proof.json'),
        ('darkwing-arrow', Z2/'dd-mz-recovery-c.lua', '', 'dd-mz-recovery-c-proof.json'),
        ('sypha-pipes', CV3/'native_pipe_land.lua', 'CV3_VARIANT=2\n', 'result.json'),
        ('alucard-pipes', CV3/'native_pipe_land.lua', 'CV3_VARIANT=3\n', 'result.json'),
        ('sypha-gap', CV3/'native_gap.lua', 'CV3_VARIANT=2\n', 'result.json'),
        ('alucard-gap', CV3/'native_gap.lua', 'CV3_VARIANT=3\n', 'result.json'),
        ('grant-pipes', CV3/'native_pipes.lua', 'CV3_VARIANT=1\n', 'result.json'),
        ('mac-pipes', CV3/'native_pipes.lua', 'PIPE_CHARACTER=15\n', 'result.json'),
    ]
    digest = hashlib.sha256(rom.read_bytes()).hexdigest()
    results = {}
    for name, source, prefix, proof_name in cases:
        folder = output/name
        folder.mkdir()
        script = folder/(name+'.lua')
        text = source.read_text()
        if name == 'darkwing-arrow':
            # Use the existing strict logical-bank assertion, including its
            # decoded shadow-before-hardware publication window. Keep the
            # original physical-entry failure and record any accepted window.
            template = (ROOT/'tests/full-roster-entry.lua').read_text()
            first = template.index('emu.addMemoryCallback(function()\n assert(not ctx')
            last = template.index('emu.addMemoryCallback(function()irqs=')
            block = template[first:last]
            block = block.replace('publicationWindows=publicationWindows+1',
                "publicationWindows=publicationWindows+1\n  local witness=assert(io.open(TEST_DIR..'verified-publication-window.json','w'));witness:write(string.format('{\"logical\":%d,\"physical\":%d,\"pendingStorePC\":%d,\"pendingValue\":%d}',ctx,actual(0xc000),pc,value));witness:close()")
            first = text.index('emu.addMemoryCallback(function()assert(not ctx)')
            last = text.index('emu.addMemoryCallback(function()irqs=')
            text = text[:first]+"local publicationWindows=0\nlocal function actual(a)return emu.convertAddress(a).address//8192 end\n"+block+text[last:]
        script.write_text(prefix+text)
        runner.ROOT = folder
        code = runner.run(script, rom, timeout=45)
        assert code == 0, name
        proof = folder/proof_name
        if not proof.exists():
            # Some legacy fixtures write their own output beside the wrapper.
            matches = list(folder.rglob(proof_name))
            assert len(matches) == 1, (name, matches)
            proof = matches[0]
        data = json.loads(proof.read_text())
        if name.endswith('-gap'):
            assert data['landed'] and not data['dead'] and data['maxX'] >= 176, data
        elif name in ('grant-pipes', 'mac-pipes'):
            assert data['maxX'] >= 1000 and data['land32'] and data['land48'] and data['land64'], data
        else:
            assert data['passed'], data
        results[name] = dict(exit=code, script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(), proof=data)
        witness = folder/'verified-publication-window.json'
        if witness.exists():
            results[name]['decoded_publication_window'] = json.loads(witness.read_text())
        (output/'results.json').write_text(json.dumps(dict(ROM_sha256=digest,
            results=results, campaign_verified=False,
            scope='Z2 ordinary no-write first-item route; DD/Grant/Mac ordinary map with entry damage cheat only; CV3 pipe/gap fixtures disclose seeded native geometry.'), indent=2)+'\n')
    print('PASS all8 combined physical-reward and obstacle fixtures')


if __name__ == '__main__':
    main()
