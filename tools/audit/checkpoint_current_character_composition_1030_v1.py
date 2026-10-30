"""Save the actual Arthur/FF/Quick shared source lineage, without ROM files."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
Q=R/'docs/qa/checkpoints/2026-10-30/shared-quick-ff-arthur-source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not Q.exists()
    parents=[(R/'build/current-character-composition-v1/source-stage-handoff-v1.json','05438f12'),
        (R/'build/current-character-composition-v2/source-stage-handoff-v2.json','131d238ed8669a294d348dae2123557c8562b4bbe418e7fd76ab2fb5e4b7ee0a'),
        (R/'build/current-character-quick-transport-v4/handoff.json','bdce3f232fa8b9ab95967d619e78aaff5e9eeed7346705a6919eff97d0917509')]
    files={Path(__file__)};packets=[]
    for p,want in parents:
        assert sha(p).startswith(want),p
        h=json.loads(p.read_text())
        for n,v in h['bindings'].items():assert sha(n)==v,n
        files|={p}|set(map(Path,h['bindings']))
        packets.append(dict(path=str(p),sha256=sha(p),status=h['status'],verified_bindings=len(h['bindings'])))
    Q.mkdir(parents=True);archive=Q/'source-lineage.zip';omitted=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
        for p in sorted(files):
            if p.suffix.lower()in['.nes','.zip','.mp4','.avi']:
                omitted.append(dict(path=str(p),sha256=sha(p)));continue
            z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        members=z.namelist()
        for n in members:assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
    h=json.loads(parents[-1][0].read_text())
    proof=dict(status='SHARED_QUICK_FF_ARTHUR_SOURCE_INGRESS_CPU_PASS_COLD_QUICK_PENDING',
        native=False,installed=False,candidate=h['candidate'],packets=packets,checks=h['checks'],
        resource_sizes=h['resource_sizes'],archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        archive_members=len(members),all_archive_member_hashes_verified=True,omitted_media_and_ROMs=omitted,
        limits=['Source lineage and instruction controls only; Quick natural cold startup/readiness and native gameplay remain incomplete.',
            'Arthur native performance hold remains; no new native test or Downloads change.',
            'FF palette lifecycle/scheduler and SMB2 shared integration remain ongoing.',
            'Later frozen UI optimization is a separate successor and is not represented as already present here.',
            'Measured foreign ingress CPU changes and exact authorized FF graphics publication differences remain in the bound original handoff.'])
    (Q/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(packets=len(packets),bindings=sum(p['verified_bindings']for p in packets),
        archive_members=len(members),archive_bytes=archive.stat().st_size)),flush=True)


if __name__=='__main__':main()
