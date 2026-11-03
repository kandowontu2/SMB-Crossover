"""Preserve reviewed terminal Bub evidence, then remove its exact loose files."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-supplement-root-freeze-1102-v35'
D=R/'docs/qa/checkpoints/2026-11-02/bub-landing-v35'

def main():
    owner=(R/'build/bub-menu-candidate-1102-v2').resolve()
    source=owner/'landing-current-supplement-v35.json';q=json.loads(source.read_text())
    archive=owner/'landing-current-supplement-v35.zip'
    assert q['passed']and not q['installed']and sha(archive)==q['archive_SHA256']=='41ca85f81278f25fe33349193e196134456abd1617006caa11826625805fb857'
    cleanup=[]
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(q['files'])and sum(i.file_size for i in z.infolist())<4_000_000
        for name,meta in q['files'].items():
            assert not Path(name).is_absolute()and '..'not in Path(name).parts and not name.endswith(('.nes','.mp4'))
            data=z.read(name);assert len(data)==meta['bytes']and hashlib.sha256(data).hexdigest()==meta['SHA256']
            assert(R/name).read_bytes()==data,name
        for name in q['exact_capture_files_safe_to_remove_only_after_root_archive_bytecomparison']:
            path=(R/name).resolve();assert path.is_relative_to(owner)and path.parent.name=='capture'and path.is_file()
            assert name in q['files']and path.read_bytes()==z.read(name)
            cleanup.append(path)
    assert len(cleanup)==33 and all(run['exit_code']==1 for run in q['terminal_runs'])
    assert not D.exists();D.mkdir(parents=True)
    for src,name in [(archive,'inputs.zip'),(source,'receipt.json')]:
        dest=D/name;dest.write_bytes(src.read_bytes());assert sha(dest)==sha(src)
    # Root confirmed all three session handles terminal. The next v36/v37
    # recipes read exact inputs from this ZIP in memory, not loose captures.
    removed_bytes=sum(p.stat().st_size for p in cleanup)
    for path in cleanup:
        assert path.resolve().is_relative_to(owner)and path.parent.name=='capture'
        path.unlink()
    for parent in{p.parent for p in cleanup}:
        if not any(parent.iterdir()):parent.rmdir()
    O.mkdir(exist_ok=True)
    (O/'receipt.json').write_text(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),ZIP_SHA256=sha(D/'inputs.zip'),verified_members=len(q['files']),removed_files=len(cleanup),removed_bytes=removed_bytes,ROM_written=False,installed=False,scope='Exact terminal v28/v31/v34 loose captures replaced by verified compact source/evidence packet. Source/controller/CPU inputs remain; archived run paths are no longer live. No recursive deletion or other Mesen session touched.'),indent=2)+'\n')
    print(json.dumps(dict(verified_members=len(q['files']),removed_files=len(cleanup),removed_bytes=removed_bytes)))

if __name__=='__main__':main()
