"""Assemble Sunny's independent leaf component; never link/install/run Mesen.

The current shared entrypoint supplies the genuine host macros/symbols. Its
assembly is a syntax/emitted-size context, not runtime integration proof.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

R = Path(__file__).resolve().parents[1]
B = R / 'build'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    manifest = R / 'chr/characters/sunny-manifest.json'
    assets = json.loads(manifest.read_text())
    assert sha(assets['source_ROM']) == assets['source_sha256']
    for path, digest in assets['generated_files'].items():
        assert sha(R / path) == digest
    assert assets['CHR_bytes'] == 16384 and assets['used_pages'] == 4
    assert assets['source_frame_count'] == 35 and assets['maximum_body_parts'] == 5
    assert all(t['raster_exact'] and t['mirror_exact'] for t in
               assets['all35_native_interpreter_and_raster_controls'])
    wrapper = B / 'sunny_compile.s'
    entry = R / 'src/entrypoint.s'
    assert '"sunny.s"' not in entry.read_text(), 'ROOT already integrated Sunny; use that build'
    wrapper.write_text('.include "entrypoint.s"\n.include "sunny.s"\n', newline='\n')
    context = B / 'bill_capsule_hud44204_build.json'
    old = json.loads(context.read_text())['command']
    defines = [old[i+1] for i, value in enumerate(old) if value == '--asm-define']
    obj = B / 'sunny_component.o'
    dep = B / 'sunny_component.d'
    command = [str(R / 'tools/Windows/cc65/bin/ca65.exe'), '--cpu', '6502x', '-g',
               '-I', str(R / 'src'), '-I', str(R), '--create-full-dep', str(dep),
               '-o', str(obj)]
    for define in defines:
        command += ['-D', define]
    command.append(str(wrapper))
    # Bind all local source/asset inputs before assembly; retain only the actual
    # dependency subset in the small receipt. No source/runtime copies.
    possible = [p for folder in ('src', 'chr', 'inc', 'audio', 'build/generated',
                                 'tools/Windows/cc65/asminc')
                for p in (R/folder).rglob('*') if p.is_file()]
    possible += [Path(__file__), context, wrapper, manifest,
                 R/'tools/Windows/cc65/bin/ca65.exe', R/'tools/Windows/cc65/bin/od65.exe']
    before = {str(p.resolve()): sha(p) for p in possible}
    run = subprocess.run(command, cwd=R, capture_output=True, text=True)
    (B/'sunny_compile.log').write_text(run.stdout+run.stderr, newline='\n')
    assert run.returncode == 0, run.stdout+run.stderr
    dump = subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'), '--dump-segments', str(obj)],
                          capture_output=True, text=True, check=True).stdout
    segments = {name: int(size) for name, size in re.findall(
        r'Name:\s+"(SUNNY_\w+)"\s+Flags:\s+\d+\s+Size:\s+(\d+)', dump)}
    assert set(segments) == {'SUNNY_CORE', 'SUNNY_ART', 'SUNNY_CHR'}, segments
    assert segments['SUNNY_CORE'] <= 3584 and segments['SUNNY_ART'] <= 4608
    assert segments['SUNNY_CHR'] == 16384
    dependency_text = dep.read_text().split(':\t', 1)[1].strip().removesuffix(':')
    actual = {}
    for word in re.split(r'(?<!\\)\s+', dependency_text):
        path = Path(word.replace('\\ ', ' '))
        path = (path if path.is_absolute() else R/path).resolve()
        digest = before[str(path)]
        assert sha(path) == digest, ('Input changed during assembly', str(path))
        actual[str(path)] = digest
    for path in (Path(__file__), context, manifest, entry, R/'src/sunny.s', R/'src/sunny_state.inc',
                 R/'src/sunny_art.inc', R/'chr/characters/sunny.chr'):
        assert sha(path) == before[str(path.resolve())]
        actual[str(path)] = sha(path)
    proof = dict(passed=True, source_only=True, unlinked=True, native_run=False,
        no_shared_source_edits=True, actual_emitted_segments=segments,
        placements=dict(SUNNY_CORE=dict(bank=81, start=0xb200,
            end_exclusive=0xb200+segments['SUNNY_CORE']),
            SUNNY_ART=dict(bank=94, start=0xce00, end_exclusive=0xce00+segments['SUNNY_ART']),
            SUNNY_CHR=dict(physical_pages=[724, 739], used_pages=[724, 727])),
        reserved_free_extents=assets['current_parent'], assembly_command=command,
        dependency_file_sha256=sha(dep), dependencies=actual, object_sha256=sha(obj),
        asset_manifest_sha256=sha(manifest),
        qualification='Actual ca65 syntax/emitted sizes and all35 source-native interpreter/raster/mirror/packed controls. Not linked runtime/publicPC/fullcaller/IRQ/deadline or gameplay acceptance.',
        root_integration_required=True)
    out = B/'sunny_component.json'
    out.write_text(json.dumps(proof, indent=2)+'\n', newline='\n')
    print(json.dumps(dict(proof=str(out), sha256=sha(out), segments=segments)))


if __name__ == '__main__':
    main()
