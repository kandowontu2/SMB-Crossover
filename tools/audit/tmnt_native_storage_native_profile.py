"""Freeze an identical-work diagnostic replay, adding read-only call accounting."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
from tmnt_native_storage_driver import ROOT, sha
from link_pit_rygar_sophia_audit_cpu import scoped_load as load
from check_tmnt_render_oa import address, location
from observe_chip_committed_write import lua


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    original = json.loads((a.prepared / 'binding.json').read_text())
    assert sha(a.prepared / 'run.lua') == original['script_sha256']
    assert all(sha(Path(path)) == digest for path, digest in original['dependencies'].items())
    a.output.mkdir(parents=True, exist_ok=False)
    b = load(Path(original['ROM']))
    names = ['AudioUpdate', 'ExpandedAudioUpdate']
    if original['ROM_sha256'].startswith('a983'):
        names += ['TnAudioUpdate', 'TnNativeInit', 'TnNativePlay']
        names += sorted(name for name in b['syms'] if name.startswith('TnSourceSTA') and '::' not in name)
    hooks, seen = [], set()
    for name in names:
        if 'seg' not in b['syms'][name]:
            assert name in ['TnNativeInit', 'TnNativePlay'] and address(b, name) in [0xa000, 0xa644]
            at = 16 + 63 * 8192 + address(b, name) - 0xa000
        else:
            at = location(b, name)
        h = dict(name=name, pc=address(b, name), bank=(at - 16) // 8192)
        if (h['bank'], h['pc']) in seen: continue
        seen.add((h['bank'], h['pc']));hooks.append(h)
    stores = []
    for bank in [38, 63, 125, 127]:
        raw = b['raw'][16 + bank * 8192:16 + (bank + 1) * 8192]
        start = 0xc000 if bank in [38, 125] else 0xa000 if bank == 63 else 0xe000
        for i in range(8190):
            if raw[i] == 0x8d and raw[i + 2] == 0x40 and raw[i + 1] in [0x10, 0x11, 0x12, 0x13, 0x15]:
                stores.append(dict(bank=bank, pc=start + i, register=0x4000 + raw[i + 1]))
    names = ['SelectedCharacter', 'OperMode', 'GameEngineSubroutine']
    if original['ROM_sha256'].startswith('a983'): names += ['TnAudioSong', 'TnAudioRam', 'TnAudioZp']
    cfg = dict(hooks=hooks, stores=stores, ram={name: address(b, name) for name in names})
    extra = ROOT / 'tools/audit/tmnt_native_storage_native_profile.lua'
    script = a.output / 'run.lua'
    script.write_text((a.prepared / 'run.lua').read_text() + '\nTMNT_STORAGE_PROFILE=' + lua(cfg) + '\n' + extra.read_text())
    parser = ROOT / 'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    py = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    command = 'import pathlib,sys;sys.path.insert(0,sys.argv[1]);from lupa.lua54 import LuaRuntime;LuaRuntime().eval("function(s)local f,e=load(s);assert(f,e);return true end")(pathlib.Path(sys.argv[2]).read_text());print("Lua54 syntax PASS")'
    result = subprocess.run([str(py), '-c', command, str(parser / 'runtime'), str(script)], capture_output=True, text=True)
    (a.output / 'parse.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    binding = original | dict(script_sha256=sha(script), identical_work_origin_binding=sha(a.prepared / 'binding.json'),
                              identical_work_origin=str(a.prepared), diagnostic_read_only=True)
    binding['dependencies'] = original['dependencies'] | {str(Path(__file__)): sha(Path(__file__)), str(extra): sha(extra)}
    (a.output / 'binding.json').write_text(json.dumps(binding, indent=2) + '\n')
    (a.output / 'profile-config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    print(json.dumps(dict(prepared=True, ROM_sha256=binding['ROM_sha256'], script_sha256=binding['script_sha256'], hooks=len(hooks), STA_DMC_sites=len(stores))))


if __name__ == '__main__':
    main()
