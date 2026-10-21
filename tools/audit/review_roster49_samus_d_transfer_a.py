"""Pin the real D MMC3 full clear and retain the distinct MMC5 negative."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIELDS='frame poll world level area areaType x y yHigh state vx vy power engine mode task lives camera buttons'.split()


def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))


def main():
    out=D/'samus-review-a.json';assert not out.exists()
    A=V/'agent-lsr-samus-current-c-route-a';f=json.loads((A/'freeze.json').read_text())
    assert sha(A/'freeze.json')=='d433128054559d987d1bf93e421fa1f2d2209e446e286937928fb7ce35daac54'
    assert sha(A/'file-catalog.json')==f['catalog_sha256'];cat=json.loads((A/'file-catalog.json').read_text())
    for n,h in cat.items():assert sha(A/n)==h,n
    p=R/'build/roster-through-2-2/lsr-samus-c-u-2-v0-mmc3';before=rows(p/'trace.csv')
    checkpoint=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json'
    assert sha(checkpoint)=='1fcbdec758e0a4c09e769f66b110d4d8d60b05cb11dffa55061bfc32bda55c88'
    cp=json.loads(checkpoint.read_text());proofs=[]
    for mapper in ['mmc3','mmc5']:
        q=R/f'build/roster-through-2-2/root49-current-d-samus-fixed-a-2-v0-{mapper}'
        m=json.loads((q/'manifest.json').read_text());result=json.loads((q/'result.json').read_text())
        expected=next(b for b in cp['builds']if b['mapper']==mapper)['artifacts']['nes']['sha256']
        assert sha(q/f'smb-crossover-{mapper}.nes')==m['rom_sha256']==expected
        assert m['full_frame_audit']and m['controller_only']and not m['memory_or_register_writes']and not m['config']['record']
        actual=rows(q/'trace.csv');inputs=rows(q/'inputs.csv')
        assert inputs==rows(p/'inputs.csv')[:len(inputs)]
        identity=json.loads((q/'current-c-identity.json').read_text())
        assert identity==dict(character=2,behavior=0,marioVariant=0,billVariant=0,outlinesOff=1)
        first=None
        for a,b in zip(before,actual):
            if any(a[k]!=b[k]for k in FIELDS):
                first=dict(frame=int(b['frame']),differences={k:[a[k],b[k]]for k in FIELDS if a[k]!=b[k]});break
        if mapper=='mmc3':
            assert m['verified_through_2_2']and result['cleared']and result['all_six_stages']and not result['deaths']and not result['failure']
            assert result['frames']==28809 and len(actual)==len(before)and first is None
            streams=['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']
            assert all((q/n).read_bytes()==(p/n).read_bytes()for n in streams)
            status='PASS_ACTUAL_D_MMC3_FULL_FIXED_CLEAR_NINE_CSVS_LITERAL_TO_C'
        else:
            assert not m['verified_through_2_2']and not result['cleared']and result['failure']=='death'and result['frames']==2351
            assert first is not None
            streams=[];status='RETAINED_MMC5_FIXED_STREAM_TRANSFER_NEGATIVE_NOT_CLASSIFIED_AS_RUNTIME_BUG'
        proofs.append(dict(mapper=mapper,status=status,result=result,identity=identity,first19field_difference_vs_C_MMC3=first,
                           literal_whole_streams=streams,
                           files={r.name:dict(bytes=r.stat().st_size,sha256=sha(r))for r in q.iterdir()if r.is_file()}))
    report=dict(status='D_MMC3_SAMUS_FULL_CLEAR_VERIFIED_MMC5_REMAINS_OPEN',script_sha256=sha(__file__),
                rehashed_C_packet_files=len(cat),parent_freeze_sha256=sha(A/'freeze.json'),checkpoint_sha256=sha(checkpoint),proofs=proofs,
                qualifications=['The MCC5 port of a fixed MMC3 stream is a controller candidate, not a source parity oracle.',
                                'Native injury owner and actual phase/geometry must be bound before proposing any MMC5 runtime change.',
                                'No final recording, Hard inventory, all-arsenal or all-roster completion claim.'],goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],sha256=sha(out),first_MMC5_difference=proofs[1]['first19field_difference_vs_C_MMC3'])))


if __name__=='__main__':main()
