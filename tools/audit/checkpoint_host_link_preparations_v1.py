"""Retain source-complete private link preparations without ROM/debug archives."""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
D=R/'docs/qa/checkpoints/2026-10-30/host-link-preparations'
UNITS=[('quickman-host-prep-v2','e4b0bf60cc357b93775f819b1852b27f43e482080fb776cd8a1800518e84d660'),
       ('arthur-host-prep-v5','31a8c6bc9bb97519c5db7f237bd04d971f79be11fb2ed90f35918fa5f9498d1d')]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    D.mkdir(parents=True)
    result=[]
    for name,digest in UNITS:
        hp=R/'build'/name/'handoff.json'
        assert sha(hp)==digest
        h=json.loads(hp.read_text());inputs=dict(h['bindings'])
        inputs[str(hp)]=digest;inputs[str(Path(__file__).resolve())]=sha(__file__)
        for path,v in inputs.items():assert sha(path)==v,path
        archive=D/(name+'-source.zip');members={}
        exclude={'.nes','.dbg','.lbl','.map','.exe','.dll','.o','.zip','.mp4','.wav','.nesppuv1'}
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
            for path,v in inputs.items():
                p=Path(path).resolve()
                if not p.is_relative_to(R)or p.suffix in exclude:continue
                n=p.relative_to(R).as_posix()
                zi=zipfile.ZipInfo(n,(2026,10,30,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
                z.writestr(zi,p.read_bytes());members[n]=v
        with zipfile.ZipFile(archive)as z:
            assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
        result.append(dict(unit=name,handoff_sha256=digest,verified_bindings=len(inputs),
                           archive=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size),
                           members=members,runtime_references=inputs))
    report=dict(status='FROZEN_SOURCE_LINK_PREPARATIONS_NOT_PLAYABLE_ADMISSION',
        units=result,
        Quick_Man='Actual A70/C mapper/selector/source/renderer preparation; permanent resident requirement removed. Full public host gameplay hooks and native qualification remain in successor.',
        Arthur='Source-authenticated movement/weapons/lifecycle/fragment plan; lossless color renderer is a separate successor. No shared gameplay qualification.',
        allocation='docs/qa/checkpoints/2026-10-30/arthur-quick-private-allocation/root-review-and-reservations.json',
        shared_installation=False)
    (D/'root-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([dict(unit=d['unit'],bindings=d['verified_bindings'],archive_bytes=d['archive']['bytes'])for d in result]))


if __name__=='__main__':main()
