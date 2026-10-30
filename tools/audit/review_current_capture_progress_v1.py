"""Verify bounded RCR smokes and retained V13 route outcomes without recapture."""
from pathlib import Path
import argparse
import json
import sys
import numpy as np

R = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import review_rogue_current_route_v1 as reference
codec, sha = reference.codec, reference.sha


def verify(out, expected_pass):
    target=out/'capture-review.json'
    assert not target.exists()
    result=json.loads((out/'result.json').read_text())
    binding=json.loads((out/'binding.json').read_text())
    ready=json.loads((out/'ready.json').read_text())
    budget=json.loads((out/'capture-budget.json').read_text())
    assert result['passed']==expected_pass
    assert binding['ROM_sha256']==ready['ROM_sha256']==result['ROM_sha256']
    assert binding['ready_sha256']==sha(out/'ready.json')
    assert binding['exit_code']==budget['returncode']==(0 if expected_pass else 1)
    assert not budget['violations']
    assert '--nes.removeSpriteLimit=false' in budget['command']
    for path,digest in binding['inputs'].items():
        assert sha(path)==digest,path
    names=[n for n in ['cold-menu','cold-lives','first-active','power-change','flagpole','endpoint','failure']
           if n in result['markers']]
    index=[json.loads(s)for s in(out/'captures-index.jsonl').open()]
    selected={n:next(q['record']for q in index if q.get('name')==n+'.argb')for n in names}
    assert len(selected)<=8
    wanted=set(selected.values());images={}
    od,of,orr=codec.decode,codec.word_fnv,codec.records
    def fnv(raw):return int(reference.fnv_words(np.frombuffer(raw,dtype='<u4')))
    def decode(mode,payload,previous,expected):
        if mode!=2:return od(mode,payload,previous,expected)
        assert previous is not None and len(previous)==expected
        delta=od(1,payload,None,expected)
        return np.bitwise_xor(np.frombuffer(delta,dtype=np.uint8),np.frombuffer(previous,dtype=np.uint8)).tobytes()
    for n in [0,1,2,16,257,1024,61440]:
        raw=bytes((i*31+19)&255 for i in range(n*4));assert fnv(raw)==of(raw)
    previous=None;crosschecks=0
    with(out/'captures.nesppuv1').open('rb')as f:
        assert f.read(16)==codec.MAGIC
        while crosschecks<16:
            header=f.read(codec.HEADER.size);assert len(header)==codec.HEADER.size
            kind,mode,reserved,seq,mb,pb,checksum=codec.HEADER.unpack(header)
            meta=json.loads(f.read(mb));payload=f.read(pb)
            raw=od(mode,payload,previous,meta['decoded_bytes'])
            assert decode(mode,payload,previous,meta['decoded_bytes'])==raw
            assert fnv(raw)==of(raw)==checksum
            if kind!=3:previous=raw
            if mode==2:crosschecks+=1
    def records(path):
        for meta,raw in orr(path):
            if meta['record']in wanted:images[meta['record']]=raw
            yield meta,raw
    codec.decode,codec.word_fnv,codec.records=decode,fnv,records
    try:verified=codec.verify(out/'captures.nesppuv1',out/'captures-index.jsonl')
    finally:codec.decode,codec.word_fnv,codec.records=od,of,orr
    assert verified['full_frames']==result['full_frames']and wanted==set(images)
    sheet=out/'selected-whole-frames.png'
    reference.png(sheet,[images[selected[n]]for n in names])
    bindings=dict(binding['inputs'])
    for path in [Path(__file__).resolve(),Path(reference.__file__),Path(codec.__file__),sheet,
                 *[out/n for n in ['ready.json','binding.json','result.json','capture-budget.json',
                   'trace.csv','inputs.csv','events.jsonl','captures-index.jsonl','captures.nesppuv1']]]:
        bindings[str(path)]=sha(path)
    hardware=None
    if result['identity']in ['alex','ryan']:
        hardware=json.loads((out/'endpoint-hardware.json').read_text())
        assert result['smoke_active_Main_updates']==100 and result['zero_deaths']
        assert hardware['Shadows_off']==ready['config']['expected_outlines_off']
        assert hardware['variant']==ready['config']['variant']
        assert hardware['ink_parts']>0 and hardware['palette'][29]==15
        bindings[str(out/'endpoint-hardware.json')]=sha(out/'endpoint-hardware.json')
    elif expected_pass:
        assert result['zero_deaths']and result['real_1_2_control_updates']>=25
    report=dict(passed=expected_pass,evidence_integrity_passed=True,native=result,
                container=verified,normal_sprite_limit=True,script_state_writes=False,
                hardware=hardware,selected=dict(path=str(sheet),order=names,sha256=sha(sheet)),
                root_visual_review_pending=True,
                decoder_crosschecks=dict(canonical_vectors=7,actual_XOR_records=crosschecks),
                scope=result['scope'],bindings=bindings)
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(identity=result['identity'],passed=expected_pass,verified_frames=verified['full_frames'],sheet=str(sheet))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('group',choices=['routes','rcr']);a=p.parse_args()
    if a.group=='routes':
        for name,passed in [('dk',False),('supermaaa',True)]:
            verify(R/'build/character-host-union-remaining-routes-v1'/name,passed)
    else:
        for v,off in [(0,1),(1,1),(0,0),(1,0)]:
            verify(R/f'build/required-rcr-ink-shared-v3/native/v{v}-off{off}',True)
