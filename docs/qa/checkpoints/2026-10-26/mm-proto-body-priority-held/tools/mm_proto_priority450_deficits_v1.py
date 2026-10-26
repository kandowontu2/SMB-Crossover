"""Preserve actual DMA-deficit epochs and paired negative wholeframes."""
from pathlib import Path
import argparse,csv,hashlib,json
import numpy as np
from PIL import Image,ImageDraw

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASELINE=D/'root-presentation450-731-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    observations=json.loads((a.candidate/'paired-review-v1/all275-paired-observations.json').read_text())
    negative=[q for q in observations if q['DMA_delta']<0]
    assert [q['frame']for q in negative]==[385]+list(range(437,451))
    logs=[[json.loads(line)for line in(root/'timing.jsonl').read_text().splitlines()]for root in[BASELINE,a.candidate]]
    epochs=[]
    for frame in [384,385,386,387,436,437,438,444,445,446,447,448,449,450]:
        pair=[]
        for rows in logs:
            events=[]
            for row in rows:
                stamp=row.get('ppu',row.get('DMA',{}).get('complete'))
                if stamp and stamp['frame']==frame:
                    events.append({k:v for k,v in row.items()if k!='DMA'}if row['kind']!='DMA-complete'else dict(kind=row['kind'],DMA={k:v for k,v in row['DMA'].items()if k not in['source','hardware']}))
            pair.append(events)
        epochs.append(dict(frame=frame,baseline=pair[0],candidate=pair[1]))
    sheet=Image.new('RGB',(768,4*260),'#202020');draw=ImageDraw.Draw(sheet)
    chosen=[385,387,437,444]
    arrays=[]
    for root in[BASELINE,a.candidate]:
        m=np.memmap(root/'direct.argb',dtype=np.uint8,mode='r',shape=(275,240,256,4))
        arrays.append(np.asarray(m[:,:,:,[2,1,0]]))
    for row,frame in enumerate(chosen):
        for column,label in enumerate(['731baseline','00fbcandidate']):
            img=Image.fromarray(arrays[column][frame-176]);img.save(a.output/f'{label}-{frame:06d}.png')
            draw.text((column*256,row*260),f'{label} actual{frame}',fill='white');sheet.paste(img,(column*256,row*260+20))
        mask=np.any(arrays[0][frame-176]!=arrays[1][frame-176],axis=2)
        heat=np.zeros((240,256,3),dtype=np.uint8);heat[mask]=[255,64,255]
        draw.text((512,row*260),f'RGBdiff{int(mask.sum())}',fill='white');sheet.paste(Image.fromarray(heat),(512,row*260+20))
    sheet.save(a.output/'paired-deficit-wholeframes.png')
    extra=dict(passed=True,evidence_freeze_only=True,candidate_held=True,native_no_harm_cadence_pass=False,physical_prefix_deficit_frames=[q['frame']for q in negative],maximum_DMA_prefix_deficit=max(-q['DMA_delta']for q in negative),first_deficit=negative[0],final_deficit=negative[-1],negative_epochs=epochs,selected_actual_wholeframes=chosen,source_owner_limit='NmiDisable, stacked Main PC, Main release/publication and helper-entry counters were not serialized. No direct first-causal-Main instruction claim is available. Actual completed hardware pages/pixels and logged NMI/DMA timing remain authoritative; do not waive a physical prefix deficit as an endFrame source label.',checker_sha256=sha(__file__))
    (a.output/'proof.json').write_text(json.dumps(extra,indent=2)+'\n')
    print(json.dumps({k:v for k,v in extra.items()if k not in['negative_epochs','first_deficit','final_deficit']},indent=2))


if __name__=='__main__':main()
