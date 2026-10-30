"""Publish source closure and retain the measured Bill performance blocker."""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/character-host-union-v10'
D=R/'docs/qa/checkpoints/2026-10-30/four-host-union-v10'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    hp=O/'handoff.json';h=json.loads(hp.read_text())
    expected='2256c9afc68495cae53e064e6a6ee27036108e000f8544e1ba68e06e1c03f534'
    assert h['candidate_sha256']==sha(O/'candidate.nes')==expected
    assert not h['installation_ready']and h['native_route_qualification']
    assert len(h['receipts'])==24
    for path,digest in h['receipts'].items():
        assert sha(path)==digest,path
        receipt=json.loads(Path(path).read_text())
        assert receipt.get('passed')or receipt.get('status')=='PASS_ISOLATED_LINKED_6502_SOURCE_REVIEW',path
        if 'ROM_sha256'in receipt:assert receipt['ROM_sha256']==expected,path
    upstream=Path(h['source_archive']);assert sha(upstream)==h['source_archive_sha256']
    bindings=dict(h['bindings']);bindings[str(hp)]=sha(hp)
    for p in [Path(__file__).resolve(),O/'HANDOFF.md']:
        bindings[str(p)]=sha(p)
    for path,digest in bindings.items():assert sha(path)==digest,path
    D.mkdir(parents=True)
    archive=D/'frozen-source-and-evidence.zip';members={}
    excluded={'.nes','.dbg','.lbl','.map','.exe','.dll','.o','.zip','.mp4','.wav','.nesppuv1'}
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path,digest in bindings.items():
            p=Path(path).resolve()
            if not p.is_relative_to(R)or p.suffix.lower()in excluded or p.name=='screens.bin':continue
            name=p.relative_to(R).as_posix()
            zi=zipfile.ZipInfo(name,(2026,10,30,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,p.read_bytes());members[name]=digest
    with zipfile.ZipFile(archive)as z:
        assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
    report=dict(status='SOURCE_AND_BOUNDED_NATIVE_PASS_BILL_CADENCE_STILL_BLOCKS_INSTALLATION',
        ROM_sha256=expected,handoff_sha256=sha(hp),source_suites=23,
        source_menu=dict(slots=32,profiles=80,private_ready=51,private_pending=29),
        native=dict(Mario='300Main/300frames,0lag',
            Bill=dict(mean_CPU=21787.3033,parent_mean_CPU=21514.7258,
                      zero_completion_frames=8,parent_zero_completion_frames=4,lag_NMIs=6,parent_lag_NMIs=4),
            Gimmick='Easy1-1clear then25real1-2updates;5180frames,3actualchargedstar rides,zero life loss'),
        installed=False,shared_download_changed=False,
        limitations=['Bill remains272.5776CPU/Main over parent; next source optimization still required.',
                     'No native all-roster1-1/every-powerup pass.',
                     'Independent Rogue/Arthur/Quick work is not included in this ROM.'],
        archive=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size,members=len(members)),
        members=members,runtime_references=bindings)
    (D/'root-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,members=len(members),archive_bytes=archive.stat().st_size)))


if __name__=='__main__':main()
