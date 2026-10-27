"""Preserve the exact0a first Mega common-gallery FALSE; offline evidence only."""
from pathlib import Path
import argparse, collections, csv, hashlib, json, shutil
from PIL import Image, ImageDraw
from final_megaproto_common_source_v2 import D, R, SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest

READY = D/'current0a-mega-common-ready-v5'
SOURCE = D/'mm-proto-construction-pivot-candidate-v9/source/src/metasprite_engine.s'
PPU = D/'current3cee-nmi-mask-order-audit-v1/NesPpu.cpp'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p, z): p.write_text(json.dumps(z, indent=2)+'\n', encoding='utf-8')
def binding(p): return dict(path=str(p.resolve()), bytes=p.stat().st_size, sha256=sha(p))
def physical(source): return [v & 0xe3 if i % 4 == 2 else v for i, v in enumerate(source)]

def analyze(output):
    output.mkdir(parents=True, exist_ok=False)
    assert verify_manifest(READY/'manifest.json') == 934
    ready = json.loads((READY/'proof.json').read_text())
    n = Path(ready['output']); original = json.loads((n/'proof.json').read_text())
    assert original['passed'] is False and original['runner_exit'] == 1
    assert original['dependencies_unchanged'] and original['native_worker_released']
    assert original['ROM_sha256'] == SHA and sha(n/'candidate.nes') == SHA
    for name, b in original['bindings'].items():
        assert (n/name).stat().st_size == b['bytes'] and sha(n/name) == b['sha256']
    failure = json.loads((n/'first-failure.json').read_text())
    assert failure['message'] == 'All256 physical OAM bytes equal the actual DMA source'
    assert failure['phase'] == dict(name='arm-face1', phase='funded')
    events = [json.loads(s) for s in (n/'events.jsonl').read_text().splitlines()]
    counts = collections.Counter(); completed = []; starts = []; safe = []; bad = []
    last = None
    for line, s in enumerate((n/'ability-dma-epochs.jsonl').open(), 1):
        q = json.loads(s); counts[q['kind']] += 1
        if q['kind'] == 'completed-DMA-before-render-enable':
            assert q['id'] == len(completed)+1
            assert len(q['source']) == len(q['hardware']) == len(q['writes']) == 256
            assert q['page'] == 2 and q['start']['pc'] == 0xe005 and q['complete']['pc'] == 0xe008
            assert q['start']['oamaddr'] == q['complete']['oamaddr'] == 0
            assert q['start']['mask'] & 24 == q['complete']['mask'] & 24 == 0
            for i, w in enumerate(q['writes']):
                assert w['stamp']['oamaddr'] == i and w['value'] == q['source'][i]
                assert w['stamp']['mask'] & 24 == 0
            assert q['hardware'] == physical(q['source'])
            if q['source'] != q['hardware']:
                differences = [dict(offset=i, source=a, hardware=b) for i,(a,b) in enumerate(zip(q['source'],q['hardware'])) if a != b]
                assert differences == q['differences']
                bad.append(dict(line=line, **q))
            completed.append(q); last = q
        elif q['kind'] == 'startFrame-hardware':
            assert len(q['hardware']) == 256
            if q.get('completed_dma_id') and not q.get('pending_dma_id'):
                assert q['completed_dma_id'] == last['id'] and q['hardware'] == last['hardware']
            starts.append(q)
        elif q['kind'] == 'actual-PPUMASK-write' and q['scoped'] and q['enabling']:
            assert q['safe']; safe.append(q)
    assert len(completed) == 392 and len(bad) == 1 and bad[0]['id'] == 392
    badrow = bad[0]
    assert badrow['differences'] == [dict(offset=34, source=16, hardware=0)]
    assert badrow['start']['frame'] == badrow['complete']['frame'] == 416
    assert badrow['start']['scanline'] == 243 and badrow['start']['cycle'] == 67
    assert badrow['complete']['scanline'] == 247 and badrow['complete']['cycle'] == 255
    assert badrow['writes'][34]['stamp']['scanline'] == 243 and badrow['writes'][34]['stamp']['cycle'] == 280
    assert len(starts) == 414 and len(safe) == 63
    assert not (n/'native-megaproto-common.json').exists() and not (n/'ppu-capture-native-result.json').exists()
    ppu = PPU.read_text(); assert 'value &= 0xE3;' in ppu and '(_spriteRamAddr & 0x03) == 0x02' in ppu
    source = SOURCE.read_text(); assert 'and #$f3' in source
    put(output/'first-physical-difference.json', badrow)
    put(output/'source-context.json', dict(
        emulator_source=binding(PPU), emulator_source_lines_436_443=ppu.splitlines()[435:443],
        game_source=binding(SOURCE), game_source_lines_1250_1267=source.splitlines()[1249:1267],
        caveat='This archived Mesen source explains the observed write mask; it is not asserted to be the exact binary build source revision. The raw native write/physical difference independently demonstrates bit4 removal.',
        source_RAM_attribute_writer='Not logged at instruction granularity. No exact foreground writer or record identity is inferred from this native capture. Game renderer AND F3 permits bit4; physical PPU write storage clears bits2..4.'))
    models = []
    for off in [0,1,2,3,34,254]:
        for value in range(256):
            s = [0]*256; s[off] = value; h = physical(s)
            assert h[off] == (value & 0xe3 if off % 4 == 2 else value)
            models.append((off,value,h[off]))
    negative = []
    for off,bit in [(0,0x10),(1,0x10),(3,0x10),(34,0x01),(34,0x02),(34,0x20),(34,0x40),(34,0x80)]:
        altered = list(badrow['hardware']); altered[off] ^= bit
        assert altered != physical(badrow['source']); negative.append(dict(offset=off, bit=bit, rejected=True))
    put(output/'offline-physical-model.json',dict(passed=True,models=len(models),negative_mutations=negative,all_raw_transfers_match_physical_storage_model=True,native_result_unchanged_FALSE=True,scope='Read-only interpretation of saved bytes. No changed Lua oracle, emulator retry, game pass or future readiness is implied.'))
    rows = list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')))
    assert len(rows) == 415 and (n/'actual-ppu.argb').stat().st_size == 415*245760
    assert [int(z['ordinal']) for z in rows] == list(range(1,416))
    assert all(int(z['mode']) == 1 for z in rows if int(z['updates']) > 0)
    for q in events:
        if q['kind'] == 'ppu-frame-captured':
            rawpath = n/(q['data']['name']+'.argb'); frame = int(q['wall'])
            with (n/'actual-ppu.argb').open('rb') as f: f.seek((frame-1)*245760); b=f.read(245760)
            assert rawpath.read_bytes() == b
    placements = [374,376,396,397,398,403,404,414,415]
    sheet = Image.new('RGB',(3*272,3*272),(28,28,28)); draw=ImageDraw.Draw(sheet); selected=[]
    for k, ordinal in enumerate(placements):
        with (n/'actual-ppu.argb').open('rb') as f: f.seek((ordinal-1)*245760); b=f.read(245760)
        im=Image.frombytes('RGBA',(256,240),b,'raw','BGRA').convert('RGB')
        name=output/f'actual-{ordinal:06}.png';im.save(name);x=(k%3)*272;y=(k//3)*272
        sheet.paste(im,(x,y+30));draw.text((x+2,y+2),f'Actual PPU {rows[ordinal-1]["ppu_frame"]} / u{rows[ordinal-1]["updates"]}',fill='white')
        selected.append(dict(ordinal=ordinal,actual_epoch=rows[ordinal-1],raw_slice_sha256=hashlib.sha256(b).hexdigest(),image=binding(name)))
    sheet.save(output/'nine-actual-whole-frames.png');put(output/'selection.json',selected)
    facts=dict(native_aggregate_remains_FALSE=True,ROM_sha256=SHA,actual_numeric_mode=1,variant=0,completed_cases=0,entered_case=1,
        first_failure=failure,source_debit=[z for z in events if z['kind']=='actual-source-spend'],zero_witness=[z for z in events if z['kind']=='actual-funded-debit-zero'],
        source_art=[z for z in events if z['kind']=='actual-source-effect-draw'],completed_PPU_frames=415,complete_DMA_observations=392,literal_byte_equal_DMAs=391,
        physical_storage_model_equal_DMAs=392,startFrame_rows=414,scoped_safe_enables=63,missing_terminal_components=['native-megaproto-common.json','ppu-capture-native-result.json'],
        native_worker_released=True,no_retry=True,classification='Invalid hardware oracle: one unimplemented OAM attribute bit4 is discarded by PPU storage. No timing/OAM corruption or game defect is established. All raw data and original assertion FALSE remain unchanged.',
        scope='Only first ARM right partial funded use. Free lift, real throw debit8 to0 and source-art observation occurred. No target/contact, cleanup, refusal, pool, second facing, other six weapons, acquisition, full timing or visual verdict is claimed. Complete native PPU ends415; failure occurs during VBlank416 before render enable. First-failure snapshot is not a completed416 image.')
    put(output/'facts.json',facts)
    refs=[Path(__file__), READY/'proof.json',READY/'manifest.json',READY/'ROOT-grant.json',SOURCE,PPU]+[q for q in n.iterdir() if q.is_file()]+[q for q in output.iterdir()if q.is_file()]
    put(output/'manifest.json',dict(bindings=[binding(q)for q in sorted(set(refs),key=str)]));verify_manifest(output/'manifest.json')
    put(output/'proof.json',dict(passed=True,negative_preserved=True,native_aggregate_remains_FALSE=True,agent_visual_review=False,ROM_sha256=SHA,original_proof_sha256=sha(n/'proof.json'),manifest_sha256=sha(output/'manifest.json'),bindings=len(set(refs)),native_worker_released=True))
    print(json.dumps(dict(proof_sha256=sha(output/'proof.json'),manifest_sha256=sha(output/'manifest.json'),facts=facts),indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();analyze(a.output)
if __name__=='__main__':main()
