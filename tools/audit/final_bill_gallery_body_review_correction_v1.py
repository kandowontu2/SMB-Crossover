"""Read-only correction of a reduced-sheet misread, using exact capture CPU times."""
from pathlib import Path
import argparse,csv,json,hashlib,shutil
from PIL import Image
from final_bill_lance_hard_gallery_source_v1 import D,ROOT,SHA,put,sha


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    native=D/'final-bill-lance-hard-gallery-ready-v5/profiles/bill-hard/native'
    prior=D/'final-bill-hard-v5-qualified-lance-ready-v2'
    assert sha(prior/'proof.json')=='8e2f31fc6282435a973e8030ee9e18049ee8bc00489e88dcc0ad46861d7c971b'
    indices={int(q['ordinal']):q for q in csv.DictReader((native/'actual-ppu-index.csv').open())}
    wanted=[2131,2132,2133,2134,2746,2747,2748,2749]
    last_dma={o:None for o in wanted};last_mask={o:None for o in wanted}
    for line in(native/'ability-dma-epochs.jsonl').open():
        q=json.loads(line)
        for o in wanted:
            cutoff=int(indices[o]['cpu_cycle'])
            if q['kind']=='completed-DMA-before-render-enable' and q['complete']['cpu']<=cutoff:last_dma[o]=q
            elif q['kind']=='actual-PPUMASK-write' and q['stamp']['cpu']<=cutoff:last_mask[o]=q
    rows=[];body_crops=[]
    with(native/'actual-ppu.argb').open('rb')as raw:
        for ordinal in wanted:
            raw.seek((ordinal-1)*245760);pixels=raw.read(245760)
            im=Image.frombytes('RGBA',(256,240),pixels,'raw','BGRA')
            q=last_dma[ordinal];assert q and q['complete']['cpu']<=int(indices[ordinal]['cpu_cycle'])
            assert q['source']==q['hardware'] and len(q['hardware'])==256
            row=dict(ordinal=ordinal,capture=indices[ordinal],raw_frame_sha256=hashlib.sha256(pixels).hexdigest(),
                     last_completed_DMA_id=q['id'],last_completed_DMA_stamp=q['complete'],last_PPUMASK_write=last_mask[ordinal])
            rgb=im.convert('RGB');outside=[(x,y)for y in range(140,208)for x in range(140,240)if rgb.getpixel((x,y))!=(146,144,255)]
            row['right_of_player_projectile_lane_nonbackground_pixels']=len(outside)
            if ordinal in wanted[:4]:
                crop=im.crop((105,160,138,208)).tobytes();body_crops.append(crop)
                row['body_RGBA_crop_sha256']=hashlib.sha256(crop).hexdigest()
                row['body_crop_nonbackground_pixels']=sum(rgb.getpixel((x,y))!=(146,144,255)for y in range(160,208)for x in range(105,138))
                oam=q['hardware'];scans=[]
                candidates=[i//4 for i in range(0,256,4)if oam[i+3]in[113,121,129] and oam[i]in[174,190,206]]
                assert len(candidates)==7
                for y in range(175,223):
                    eligible=[i//4 for i in range(0,256,4)if 0<=y-oam[i]-1<16]
                    body=[i for i in candidates if 0<=y-oam[4*i]-1<16]
                    lost=[i for i in body if i not in eligible[:8]]
                    assert not lost
                    scans.append(dict(scanline=y,actual_eligible_OAM_order=eligible,first8=eligible[:8],candidate_body_slots=body,candidate_body_rejected=[]))
                row['all_48_body_scanlines']=scans
            if ordinal==2133:im.convert('RGB').save(a.output/'actual-whole-PPU2133.png')
            rows.append(row)
    assert all(c==body_crops[0]for c in body_crops) and len(body_crops)==4
    assert [r['body_crop_nonbackground_pixels']for r in rows[:4]]==[320]*4
    assert [r['last_completed_DMA_id']for r in rows[:4]]==[1866,1866,1866,1867]
    assert [r['right_of_player_projectile_lane_nonbackground_pixels']for r in rows[:4]][:3]==[0,0,0]
    put(a.output/'proof.json',dict(passed=True,native_run=False,new_emulator_launches=0,ROM_sha256=SHA,
        original_erroneous_review_preserved=True,prior_ready_sha256=sha(prior/'proof.json'),
        correction='Bill is visible in standalone2133. Its full body crop is byte-identical at2131/2132/2133/2134. Earlier reduced-sheet missing-body statement was an agent visual-review error, not a ROM defect.',
        shot_timing_correction='Laser lane is empty2131..2133; new DMA1867 precedes2134. Flare lane changes with new DMA2268. This tiny interval includes publication repetition/lag and alone does not prove periodic flicker or establish a CHR defect. Preserve native/source/hardware facts without an invented graphics failure.',
        actual_alignment='Captured endFrame CPU cycle determines last physically completed DMA, not equality of PPU callback frame labels. All48 candidate body scanlines retain the body inside the actual first8 eligible sprites.',
        CHR_palette_limits='Historical observer checked write-time CHR latch consistency but did not save each capture-time CHR or palette image. Do not invent those values or infer a CHR/palette cause. No body defect remains in these actual images.',
        confirmed_unrelated_issue='Selected Bill capsule overlapping WORLD/TIME remains source/OAM/pixel-proved; this correction does not dismiss it.',frames=rows))
    files={Path(__file__),prior/'proof.json',prior/'visual-review.json',ROOT/'docs/qa/final-bill-hard-v5-native-and-lance-ready-2026-10-26.txt',
           native/'proof.json',native/'actual-ppu.argb',native/'actual-ppu-index.csv',native/'ability-dma-epochs.jsonl'}
    files.update(a.output.iterdir())
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
    public=ROOT/'docs/qa/checkpoints/2026-10-26/bill-hard-v5-component-lance-prepared-v2/body-review-correction'
    public.mkdir(parents=True,exist_ok=False)
    for name in ['proof.json','manifest.json','actual-whole-PPU2133.png']:shutil.copyfile(a.output/name,public/name)
    (public/'README.txt').write_text('Additive correction; original report/readiness remain byte-exact. Standalone2133 shows Bill. Body pixels identical over four frames, CPU-aligned DMA and first8 candidate body scanlines preserved. Earlier missing-body/reduced-sheet shot timing interpretation was an agent visual-review error. No new native or game edit. Confirmed capsule/header overlap remains. Root may review this addendum with the frozen Lance-only readiness.\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,new_native_launches=0,proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),public=str(public))))


if __name__=='__main__':main()
