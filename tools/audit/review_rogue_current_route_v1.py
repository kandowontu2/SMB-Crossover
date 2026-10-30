"""Verify every lossless Rogue frame and compare with the qualified backend."""
from pathlib import Path
import csv
import hashlib
import json
import struct
import sys
import numpy as np
from numba import njit

R=Path(__file__).resolve().parents[2]
O=R/'build/rogue-current-menu-v5/native/route-retry-v1'
P=R/'build/verification/rogue-dawn-victory-native-easy-v1'
sys.path.insert(0,str(R/'tools/audit'))
import final_inventory_compact_capture_v1 as codec
from current_roster_compact_11_v1 import png


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@njit(cache=False)
def fnv_words(words):
    value=np.uint32(2166136261)
    for word in words:value=np.uint32((value^word)*np.uint32(16777619))
    return value


def main():
    assert not(O/'review.json').exists()
    result=json.loads((O/'result.json').read_text());binding=json.loads((O/'binding.json').read_text())
    ready=json.loads((O/'ready.json').read_text());budget=json.loads((O/'capture-budget.json').read_text())
    expected='f23af095d2b8ed865c7447d2b8ad5ac6cedd02780dedde9d95ab10c80fd7f134'
    assert result['passed']and result['zero_deaths']and result['cheats_off']
    assert result['ROM_sha256']==binding['ROM_sha256']==ready['ROM_sha256']==expected
    assert binding['exit_code']==budget['returncode']==0 and not budget['violations']
    assert result['real_1_2_control_updates']>=25 and result['frames']==6513
    for p,h in binding['inputs'].items():assert sha(p)==h,p
    old=json.loads((P/'review.json').read_text())
    original_checkpoint=R/'docs/qa/checkpoints/2026-10-30/rogue-dawn-victory-pose/root-review.json'
    frozen=json.loads(original_checkpoint.read_text())
    assert sha(P/'review.json')==frozen['runtime_references'][str(P/'review.json')]
    assert old['passed']and sha(P/'captures.nesppuv1')==old['container']['container_sha256']
    assert sha(P/'captures-index.jsonl')==old['container']['index_sha256']
    assert (P/'inputs.csv').read_bytes()==(O/'inputs.csv').read_bytes(),'Same full controller poll stream'
    rows=list(csv.DictReader((O/'trace.csv').open()))
    assert len(rows)==6513
    walk=next(r for r in rows if r['engine']=='5'and r['level']=='0'and int(r['x'])>=3210)
    index=[json.loads(s)for s in(O/'captures-index.jsonl').open()]
    names=['cold-menu','cold-lives','first-active','corner-332','power-change','flagpole','endpoint']
    selected={name:next(q['record']for q in index if q.get('name')==name+'.argb')for name in names}
    selected['castle-walk']=int(walk['captured'])
    wanted=set(selected.values());images={}
    original_decode=codec.decode;original_fnv=codec.word_fnv;original_records=codec.records
    def fast_fnv(raw):return int(fnv_words(np.frombuffer(raw,dtype='<u4')))
    def fast_decode(mode,payload,previous,expected):
        if mode!=2:return original_decode(mode,payload,previous,expected)
        assert previous is not None and len(previous)==expected
        delta=original_decode(1,payload,None,expected)
        return np.bitwise_xor(np.frombuffer(delta,dtype=np.uint8),np.frombuffer(previous,dtype=np.uint8)).tobytes()
    # Same sequential checksum and XOR semantics, accelerated only on the
    # host. Cross-check canonical implementations before processing frames.
    for n in [0,1,2,16,257,1024,61440]:
        raw=bytes((i*31+19)&255 for i in range(n*4))
        assert fast_fnv(raw)==original_fnv(raw),n
    xor_checks=0
    def capture_records(path):
        nonlocal xor_checks
        for q,raw in original_records(path):
            if q['record']in wanted:images[q['record']]=raw
            yield q,raw
    # Check actual encoded XOR payloads with the original bytewise decoder.
    previous=None
    with(O/'captures.nesppuv1').open('rb')as f:
        assert f.read(16)==codec.MAGIC
        while xor_checks<16:
            header=f.read(codec.HEADER.size);assert len(header)==codec.HEADER.size
            kind,mode,reserved,seq,mb,pb,checksum=codec.HEADER.unpack(header)
            meta=json.loads(f.read(mb));payload=f.read(pb)
            decoded=original_decode(mode,payload,previous,meta['decoded_bytes'])
            assert fast_decode(mode,payload,previous,meta['decoded_bytes'])==decoded
            assert fast_fnv(decoded)==original_fnv(decoded)==checksum
            if kind!=3:previous=decoded
            if mode==2:xor_checks+=1
    codec.word_fnv=fast_fnv;codec.decode=fast_decode;codec.records=capture_records
    try:verified=codec.verify(O/'captures.nesppuv1',O/'captures-index.jsonl')
    finally:codec.word_fnv=original_fnv;codec.decode=original_decode;codec.records=original_records
    assert verified['full_frames']==result['full_frames']==5801
    assert wanted==set(images)
    equal=[];different=[]
    for q in index:
        if q['type']!='record':continue
        identical=verified['record_sha256'][q['record']]==old['container']['record_sha256'][str(q['record'])]
        (equal if identical else different).append(dict(ordinal=q['full_ordinal'],frame=q['stamp']['ppu_frame']))
    assert different==[dict(ordinal=i,frame=77+i)for i in range(1,6)],different[:30]
    assert len(equal)==5796
    sheet=O/'selected-whole-frames.png';png(sheet,[images[selected[n]]for n in names+['castle-walk']])
    castle=O/'actual-victory-walk.png';png(castle,[images[selected['castle-walk']]])
    inputs=dict(binding['inputs'])
    for p in [Path(__file__).resolve(),original_checkpoint,P/'review.json',P/'captures.nesppuv1',P/'captures-index.jsonl',
              P/'inputs.csv',O/'binding.json',O/'ready.json',O/'result.json',O/'trace.csv',O/'captures-index.jsonl',
              O/'captures.nesppuv1',O/'capture-budget.json',sheet,castle,
              R/'tools/audit/final_inventory_compact_capture_v1.py',R/'tools/audit/current_roster_compact_11_v1.py']:
        inputs[str(p)]=sha(p)
    report=dict(passed=True,ROM_sha256=expected,native=result,container=verified,
        full_frame_comparison=dict(exact_pairs=5796,changed_menu_frames=different,
            every_lives_gameplay_powerup_flagpole_castle_and_endpoint_frame_identical=True,
            reference_ROM_sha256=old['native']['ROM_sha256'],same_controller_polls=True),
        host_decoder_acceleration=dict(canonical_checksum_vectors=7,actual_XOR_frames_crosschecked=xor_checks,
            complete_container_checksums_and_aliases_verified=True),
        selected_whole_frames=dict(path=str(sheet),order=names+['castle-walk'],sha256=sha(sheet)),
        castle_walk=dict(trace=walk,path=str(castle),sha256=sha(castle)),
        root_visual_review_pending=True,
        limits=['Exact frame equality against the prior qualified backend establishes composition parity, not perfection of that backend.',
                'No full campaign/all-upgrade/Hard-mode/native-hardware/constant60Hz claim.',
                'Ordinary Bill native cadence still needs a matching comparison before shared installation.'],
        inputs=inputs)
    (O/'review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,verified_frames=5801,exact_reference_pairs=len(equal),changed_menu_frames=len(different),sheet=str(sheet))))


if __name__=='__main__':main()
