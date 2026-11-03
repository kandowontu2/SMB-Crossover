"""Retain rejected live-code staging prototypes and reclaim their exact sidecars."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/prince-live-negative-root-1103-v112'
P = ROOT/'build/prince-actor-1101-v1'
D = ROOT/'docs/qa/checkpoints/2026-11-03/prince-live-negative-v112'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    files = [Path(__file__)]
    sources = ['measure_prince_live_policies_1103_v149.py',
        'prepare_prince_live_backing_1103_v150.py', 'prepare_prince_live_manifest_1103_v151.py',
        'check_prince_live_cold_1103_v152.py']
    files += [ROOT/'tools/audit'/n for n in sources]
    for version, expected in ((149,33),(150,9),(151,5),(152,1)):
        matches = sorted(P.glob(f'*v{version}.*'))
        assert len(matches) == expected, (version,len(matches))
        files.extend(matches)
    disposable = sorted(P.glob('*v150.*')) + [P/name for name in (
        'post-owner-extra-v151.bin','post-owner-v151.bin','post-owner-v151.lbl',
        'post-owner-v149.cfg','post-selector-v149.cfg','post-selector-v149.lbl')]
    assert len(disposable) == len(set(disposable)) == 15
    assert all(f in files and f.is_file() and f.resolve().is_relative_to(P.resolve()) for f in disposable)
    D.mkdir(parents=True,exist_ok=False)
    archive = D/'inputs.zip'
    bindings = {f.relative_to(ROOT).as_posix():sha(f.read_bytes()) for f in files}
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for f in files:
            z.writestr(f.relative_to(ROOT).as_posix(),f.read_bytes())
    with ZipFile(archive) as z:
        for f in files:
            data = z.read(f.relative_to(ROOT).as_posix())
            assert data == f.read_bytes() and sha(data) == bindings[f.relative_to(ROOT).as_posix()]
    assert archive.stat().st_size < 256000
    removed_bytes = sum(f.stat().st_size for f in disposable)
    for f in disposable:
        f.unlink()
    result = dict(passed=True,negative_prototypes_only=True,installed=False,ROM_produced=False,
        archive_SHA256=sha(archive.read_bytes()),archive_bytes=archive.stat().st_size,
        source_files=[f.relative_to(ROOT).as_posix() for f in files[:5]],bindings=bindings,
        removed_disposable_files=[f.relative_to(ROOT).as_posix() for f in disposable],
        removed_disposable_bytes=removed_bytes,
        scope='Private149..152 cold-to-live staging prototypes preserved. Real cold152 proved selector writes through resident A65 target ROM instead of RAM3;153 successor uses the genuine C2 installer FarCall. Separate subsequent disassembly also corrected palette lookup versus actual backdrop queue. These prototypes are not native-qualified or installed.',
        retained_live_dependencies='All149 source/binaries directly needed by153/155/157 retained, except3 verified superseded linker sidecars. Historical151 manifest and owner assembly retained because156 inherited their binding names; next current receipt must correct that scope. Deleted15 generated paths remain available only inside this checkpoint, not claimed live.')
    for f in (OUT/'receipt.json',D/'receipt.json'):
        f.write_text(json.dumps(result,indent=2)+'\n')
    handoff = ROOT/'docs/qa/continuation-current.json'
    current = json.loads(handoff.read_text())
    current['Prince_native_current_1103'].update(
        live_negative_checkpoint=D.relative_to(ROOT).as_posix(),
        live_negative_scope=result['scope'],live_superseded_files_removed=result['removed_disposable_files'])
    handoff.write_text(json.dumps(current,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','removed_disposable_files')},indent=2))


if __name__=='__main__':
    main()
