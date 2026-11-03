"""Preserve the unadmitted DK menu and Prince's actual graphics negative."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

R=Path(__file__).resolve().parents[2]
O=R/'build/menu-render-root-freeze-1103-v118'
C=R/'docs/qa/checkpoints/2026-11-03'
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
    O.mkdir(exist_ok=False)
    src=R/'build/dkjr-menu-current-1103-v1/current-menu-v7.json'
    q=json.loads(src.read_text()); archive=R/q['archive']
    assert q['passed'] and not q['menu_admitted'] and not q['ROM_written']
    assert sha(archive.read_bytes())==q['archive_SHA256']
    assert archive.stat().st_size==q['archive_bytes']
    with ZipFile(archive) as z:
        assert len(z.namelist())==len(q['members'])
        for row in q['members']:
            data=z.read(row['path'])
            assert len(data)==row['bytes'] and sha(data)==row['SHA256']
            assert (R/row['path']).read_bytes()==data,row['path']
    d=C/'dkjr-menu-source-v118';d.mkdir(exist_ok=False)
    (d/'inputs.zip').write_bytes(archive.read_bytes())
    (d/'helper-manifest.json').write_bytes(src.read_bytes())
    (d/'receipt.json').write_text(json.dumps(dict(passed=True,source_CPU_only=True,
        menu_admitted=False,installed=False,archive_SHA256=q['archive_SHA256'],
        scope='Exact frozen7 source and finite current93-profile/menu/scene CPU evidence. No native DK admission or assisted crossing claimed.'),indent=2)+'\n')
    paths={Path(__file__)}
    native_roots=[
        R/'build/prince-live-root-controls-1103-v114/native',
        R/'build/prince-native-followup-1103-v176/native',
        R/'build/prince-chr-owner-1103-v177/native',
    ]
    source_paths=[R/'tools/audit'/p for p in (
        'prepare_prince_live_root_1103_v114.py',
        'prepare_prince_render_turn_1103_v176.py',
        'prince_render_turn_1103_v176.lua',
        'prepare_prince_chr_writer_1103_v177.py')]
    paths.update(source_paths)
    for root in native_roots:
        ready=json.loads((root/'ready.json').read_text())
        for path,h in ready['bindings'].items():
            assert sha(Path(path).read_bytes())==h,path
        binding=json.loads((root/'capture/binding.json').read_text())
        assert binding['ready_sha256']==sha((root/'ready.json').read_bytes())
        assert binding['ROM_sha256']=='6c9e85a94d34a4623d21789d5293c61af2ad14d214f5780f57613a51ae6bb25a'
        for p in root.rglob('*'):
            if p.is_file():
                assert p.suffix.lower() not in ('.nes','.mp4','.avi','.state')
                paths.add(p)
    negative=json.loads((native_roots[-1]/'capture/render-evidence.json').read_text())
    assert negative['DMA']['banks'][0]==320 and not negative['graphics_qualified']
    assert any(e['stamp']['PC']==0xa22c and e['writer_physical']==33324
               and e['value']==64 for e in negative['CHR0_events'])
    dest=C/'prince-render-negative-v118';dest.mkdir(exist_ok=False)
    members=[]
    with ZipFile(dest/'inputs.zip','w',ZIP_DEFLATED,compresslevel=9) as z:
        for path in sorted(paths):
            data=path.read_bytes();name=path.relative_to(R).as_posix()
            z.writestr(name,data);members.append(dict(path=name,bytes=len(data),SHA256=sha(data)))
    with ZipFile(dest/'inputs.zip') as z:
        for p in members:assert sha(z.read(p['path']))==p['SHA256']
    receipt=dict(preserved=True,graphics_qualified=False,installed=False,
        ROM_SHA256=binding['ROM_sha256'],archive_SHA256=sha((dest/'inputs.zip').read_bytes()),
        members=members,scope='114 short Left controller negative;176 event-based Left reversal PASS, actual full-DMA image still corrupt;177 finite writer proof finds native bank4 A22C overrides intended341 to320. Generic diagnostic PASS is not graphics acceptance. Exact source/packets/results retained without ROM copies.')
    (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    stage=[Path(__file__).relative_to(R).as_posix(),*[p['path'] for p in q['source_files']],
           *[p.relative_to(R).as_posix() for p in source_paths]]
    for directory in (d,dest):stage.extend(p.relative_to(R).as_posix() for p in directory.iterdir())
    (O/'stage-files.txt').write_text('\n'.join(dict.fromkeys(stage))+'\n')
    (O/'receipt.json').write_text(json.dumps(dict(passed=True,checkpoints=[str(d),str(dest)]),indent=2)+'\n')
    print(json.dumps(dict(preserved=True,DK_source_only=True,Prince_graphics_negative=True,
                         archive_bytes=sum((p/'inputs.zip').stat().st_size for p in (d,dest)))))


if __name__=='__main__':main()
