"""Preserve the native Lua parse failure; derive an ASCII-metadata-only retry."""
from pathlib import Path
import hashlib
import json

from current_roster_compact_11_v1 import lua

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', newline='\n')


def main():
    old = ROOT / 'build/current-bdf9-mike-bat-render-v1'
    source = old / 'prepared-not-run.json'
    assert sha(source) == '781d1a6bfe68ad3b23ae77bff734e43aec988673564e30e7f886534eca375d82'
    ready = json.loads(source.read_text())
    for binding in ready['bindings']:
        assert sha(Path(binding['path'])) == binding['sha256'], binding['path']
    launch = json.loads((old / 'launch.json').read_text())
    assert launch['exit_code'] == 1 and launch['changed_inputs'] == []
    log = old / 'native/mike_bat-run.log'
    assert "missing '{'" in log.read_text() and not (old / 'native/result.json').exists()
    cfg = json.loads((old / 'config.json').read_text())
    assert cfg['scope'].count('\u2192') == 2
    cfg['scope'] = cfg['scope'].replace('\u2192', '->')
    old_run = (old / 'run.lua').read_text()
    header, body = old_run.split('\n', 1)
    assert header.count('\\u2192') == 2 and '\\u' not in header.replace('\\u2192', '')
    text = 'CURRENT_MAC_MIKE_POWERUPS=' + lua(cfg) + '\n' + body
    assert text == old_run.replace('\\u2192', '->')
    out = ROOT / 'build/current-bdf9-mike-bat-render-v2'
    assert not out.exists()
    out.mkdir()
    put(out / 'config.json', cfg)
    (out / 'run.lua').write_text(text, newline='\n')
    command = json.loads((old / 'command.json').read_text())
    command['argv'] = [arg.replace(str(old), str(out)) for arg in command['argv']]
    assert str(out / 'run.lua') in command['argv'] and str(out / 'native') in command['argv']
    put(out / 'command.json', command)
    paths = [source, old / 'launch.json', log, Path(__file__),
             out / 'run.lua', out / 'config.json', out / 'command.json']
    ready['scope'] = cfg['scope']
    ready['original_ready_sha256'] = sha(source)
    ready['preparation_correction'] = 'Only two display-metadata arrows changed to ASCII ->. Same ROM, profile body, scene/input plan, assertions, hardware guard and caps. Original native parse rejection retained.'
    ready['bindings'] += [dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p)) for p in paths]
    put(out / 'prepared-not-run.json', ready)
    print(json.dumps(dict(ready=str(out / 'prepared-not-run.json'),
                          sha256=sha(out / 'prepared-not-run.json'), bindings=len(ready['bindings']))))


if __name__ == '__main__':
    main()
