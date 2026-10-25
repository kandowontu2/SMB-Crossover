"""Recheck native springs/contact and outline guards on the combined repair ROM."""
from pathlib import Path
import argparse, hashlib, importlib.util, json

R = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output = a.output.resolve()
    a.output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('nd_adapters_mesen', R/'tools/run_mesen.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    bounce = R/'build/verification/expanded-bounce-mu-candidate-agent/native_bounce_bound.lua'
    outlines = R/'build/verification/expanded-controls-agent/raw-id-audit'
    cases = [('bounce', bounce), ('outline-mike', outlines/'outline-fixed-native.lua'),
             ('outline-samus', outlines/'outline-fixed-samus.lua')]
    results, binding = {}, dict(ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(), fixtures={})
    for name, source in cases:
        folder = a.output/name
        folder.mkdir()
        text = source.read_text()
        if name == 'bounce':
            text = 'INCLUDE_MAC=true\n'+text
        if name == 'outline-mike':
            text = text.replace('right=f==140 or f==160', 'right=f==140 or f==160 or f==170')
        script = folder/(name+'.lua')
        script.write_text(text)
        runner.ROOT = folder
        results[name] = runner.run(script, a.rom.resolve(), timeout=45)
        binding['fixtures'][name] = dict(source=str(source),
            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            bound_sha256=hashlib.sha256(script.read_bytes()).hexdigest(), exit=results[name])
        (a.output/'adapter-native-results.json').write_text(json.dumps(results, indent=2)+'\n')
        (a.output/'binding.json').write_text(json.dumps(binding, indent=2)+'\n')
        assert results[name] == 0, name
    print('PASS native spring/contact arenas and both bounded outline fixtures')


if __name__ == '__main__':
    main()
