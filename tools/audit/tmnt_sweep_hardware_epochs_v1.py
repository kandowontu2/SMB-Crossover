"""Additive actual OAM epochs; never change the strict frame-prefix verdict."""
from pathlib import Path
import argparse
import hashlib
import json
from tmnt_native_storage_driver import ROOT,sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def digest(v):return hashlib.sha256(bytes(v)).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;pair=D/'tmnt-sweep-live-math-native-ready-v1'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    strict=json.loads((pair/'easy-strict-proof.json').read_text());assert not strict['performance_gate_passed']
    data={};observations={}
    for key in ['baseline','candidate']:
        path=pair/(key+'-easy')/'native-bus.jsonl';rows=[json.loads(x)for x in path.read_text().splitlines()]
        ds=[];draw=None
        for row in rows:
            if row['kind']=='draw-construction':draw=row
            elif row['kind']=='DMA-complete':
                q=row['data'];assert q['exact']and q['safe']and q['writes']==256 and q['source']==q['hardware']
                assert 241<=q['start']['scanline']<=260 and 241<=q['finish']['scanline']<=260
                assert q['start']['frame']==q['finish']['frame']
                ds.append(q|dict(latest_source_construction=draw))
        data[key]=ds;observations[key]=rows
    mismatch=next(i for i,(b,c)in enumerate(zip(data['baseline'],data['candidate']))
        if b['start']['frame']!=c['start']['frame']or b['hardware']!=c['hardware'])
    assert mismatch==508
    prefix=[]
    for i,(b,c)in enumerate(zip(data['baseline'][:mismatch],data['candidate'][:mismatch])):
        assert b['start']['frame']==c['start']['frame']and b['hardware']==c['hardware']
        prefix.append(dict(ordinal=i+1,frame=b['start']['frame'],hardware256_sha256=digest(b['hardware']),
            baseline_start=b['start'],candidate_start=c['start'],baseline_finish=b['finish'],candidate_finish=c['finish']))
    # Compare the actual persistent OAM image for each common physical epoch,
    # retaining the last completed hardware page across epochs with no DMA.
    images={};first=max(data[k][0]['finish']['frame']for k in data)
    last=min(data[k][-1]['finish']['frame']for k in data)
    for key,rows in data.items():
        indexed={q['finish']['frame']:q['hardware']for q in rows};image=None;images[key]={}
        for frame in range(first,last+1):
            if frame in indexed:image=indexed[frame]
            assert image is not None
            images[key][frame]=image
    differing=[f for f in range(first,last+1)if images['baseline'][f]!=images['candidate'][f]]
    around={}
    for key,rows in data.items():
        q=next(q for q in rows if q['latest_source_construction']and q['latest_source_construction']['index']==406)
        around[key]=dict(source_construction=q['latest_source_construction'],start=q['start'],finish=q['finish'],
            hardware256_sha256=digest(q['hardware']))
    assert around['baseline']['finish']['frame']==around['candidate']['finish']['frame']==736
    assert around['baseline']['hardware256_sha256']==around['candidate']['hardware256_sha256']
    out.mkdir(parents=True);(out/'matching-prefix.json').write_text(json.dumps(prefix,indent=2)+'\n')
    proof=dict(measurement_valid=True,additive_only=True,old_strict_result_unchanged=True,strict_performance_gate_passed=False,
        inputs={key:sha(pair/(key+'-easy')/'native-bus.jsonl')for key in data},
        actual_DMA_exact_safe256B=True,equal_hardware_and_physical_epoch_prefix_transfers=mismatch,
        primary_update406_next_hardware_transfer=around,physical_epoch_first=first,physical_epoch_last=last,
        differing_persistent_OAM_epochs=differing,first_differing_persistent_OAM_epoch=min(differing),
        criteria='A full256B completed OAM DMA withinscan241..260 precedes the next visible sprite epoch. Same PPUframeCount plus equal complete destination bytes establish equal sprite-OAM image for that upcoming epoch; when no DMA occurs, retain last destination image. This does not assert equal RGB, background VRAM/scroll/CHR, or unrecorded exact NMI acceptance.',
        NMI_entry_stackedPC_not_recorded=True,no_new_native_run=True,no_adoption=True,
        first_strict_completed_update_prefix=406,first_actual_missing_transfer_ordinal=509,
        checker_sha256=sha(Path(__file__)),prefix_sha256=sha(out/'matching-prefix.json'))
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in ['measurement_valid','equal_hardware_and_physical_epoch_prefix_transfers','first_differing_persistent_OAM_epoch','differing_persistent_OAM_epochs']}))


if __name__=='__main__':main()
