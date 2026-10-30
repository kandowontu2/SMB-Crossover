"""Bind and compare every controller-only baseline/dense native screen."""
from pathlib import Path
import hashlib
import json
import struct
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/parodius-chr-compact-v1'
D=R/'docs/qa/checkpoints/2026-10-30/parodius-dense-chr-native'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def frames(raw):
    at=0;out=[]
    while at<len(raw):
        frame,n=struct.unpack_from('<II',raw,at);at+=8
        png=raw[at:at+n];at+=n
        assert 0<n<1048576 and len(png)==n and png.startswith(b'\x89PNG\r\n\x1a\n')
        assert not out or frame==out[-1]['frame']+1
        out.append(dict(frame=frame,png_sha256=hashlib.sha256(png).hexdigest(),bytes=n))
    assert at==len(raw)
    return out


def main():
    assert not D.exists()
    build=json.loads((O/'build-proof.json').read_text())
    inputs={};rows=[];screen_count=0
    for v,name in [(1,'Octopus'),(2,'TwinBee'),(3,'Pentarou')]:
        paths=[O/'native'/('parent-v'+str(v)),O/'native'/('dense-v'+str(v))]
        before,after=[json.loads((p/'result.json').read_text())for p in paths]
        for p,data,expected in zip(paths,[before,after],[build['parent_sha256'],build['candidate_sha256']]):
            binding=json.loads((p/'binding.json').read_text())
            guard=json.loads((p/'capture-budget.json').read_text())
            assert binding['exit_code']==0 and data['passed'] and data['ROM_sha256']==expected
            assert binding['ROM_sha256']==expected and sha(p/'controller.lua')==binding['controller_sha256']
            assert guard['workspace_byte_cap']==70000000000 and guard['run_file_cap']==64
            assert guard['workspace_bytes']<guard['workspace_byte_cap']
            for f in p.iterdir():
                if f.is_file():inputs[str(f)]=sha(f)
        normalized_before={k:x for k,x in before.items()if k!='ROM_sha256'}
        normalized_after={k:x for k,x in after.items()if k!='ROM_sha256'}
        assert normalized_before==normalized_after,(v,before,after)
        stream0,stream1=[(p/'screens.bin').read_bytes()for p in paths]
        assert stream0==stream1,(v,'Actual native screen difference')
        sequence=frames(stream1)
        assert len(sequence)==after['captured_screens']
        for filename in ['trace.csv','main-cycles.csv']:
            assert (paths[0]/filename).read_bytes()==(paths[1]/filename).read_bytes(),(v,filename)
        screen_count+=len(sequence)
        rows.append(dict(character=name,variant=v,physical_frames=after['frames'],
                         actual_gameplay_frames=after['gameplay_frames'],main_updates=after['main_updates'],
                         exact_screen_pairs=len(sequence),screens_sha256=sha(paths[1]/'screens.bin'),
                         identical_trace_and_main_timing=True,timing=after['timing'],
                         actual_state=normalized_after,screen_frames=sequence))
    inputs[str(R/'tools/audit/parodius_chr_compact_native_v1.py')]=sha(R/'tools/audit/parodius_chr_compact_native_v1.py')
    inputs[str(Path(__file__).resolve())]=sha(__file__)
    D.mkdir(parents=True)
    archive=D/'native-source-and-telemetry.zip';members={}
    # Keep the six lossless screen streams in their original bounded workspace
    # runs. The compact Git checkpoint stores their hashes and native telemetry.
    excluded={'.bin','.exe','.dll','.nes','.dbg','.lbl','.map'}
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path,h in inputs.items():
            p=Path(path)
            assert sha(p)==h
            if p.suffix in excluded:continue
            n=p.relative_to(R).as_posix()
            zi=zipfile.ZipInfo(n,(2026,10,30,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,p.read_bytes());members[n]=h
    with zipfile.ZipFile(archive)as z:
        assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
    report=dict(passed=True,status='EXACT_NATIVE_A_B_SCREEN_AND_TIMING_EQUIVALENCE',
        ROM_sha256=build['candidate_sha256'],parent_ROM_sha256=build['parent_sha256'],
        serial_runs=6,exact_native_screen_pairs=screen_count,
        no_native_RAM_or_physics_injection=True,rows=rows,
        source_checkpoint='docs/qa/checkpoints/2026-10-30/parodius-dense-chr',
        unchanged_normal_sprite_limit=True,
        lossless_streams_retained=True,shared_installation=False,
        archive=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size),
        members=members,runtime_references=inputs,
        limitations=['Cold selection/lives/up/down/shooting only; no new1-1 or every-upgrade qualification.',
                     'Existing PN lag remains identical to baseline; this data repack does not claim to fix it.',
                     'Parent four-host Bill regression still blocks shared installation.'])
    (D/'root-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,runs=6,exact_native_screen_pairs=screen_count,
                         source_ROM=report['ROM_sha256'],archive_bytes=archive.stat().st_size)))


if __name__=='__main__':main()
