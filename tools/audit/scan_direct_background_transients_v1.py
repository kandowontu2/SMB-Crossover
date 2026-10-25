"""Screen exact direct-PPU replay frames for transient background tile changes.

Derived from scan_background_transients_oq.py; alignment, masking and thresholds
are unchanged. Direct proof, discovery, exact inputs/trace and every indexed
PNG/RGB hash are independently checked. Sprite rectangles are conservatively excluded. Candidate sheets require human
investigation; a completed scan is not a certificate that the game has no bugs.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from collections import defaultdict
import numpy as np
from PIL import Image,ImageDraw


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--route',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--minimum-pixels',type=int,default=12)
    p.add_argument('--discovery',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    direct=json.loads((a.route/'proof.json').read_text())
    manifest=json.loads((a.discovery/'manifest.json').read_text())
    assert direct['passed'] and direct['fixed_inputs_and_trace_exact'] and direct['every_saved_PNG_RGB_exact']
    assert direct['actual_PPU_frame_ids_complete'] and direct['raw_gzip_roundtrip_exact']
    assert direct['source_discovery_manifest_sha256']==sha(a.discovery/'manifest.json')
    assert direct['ROM_sha256']==manifest['ROM_sha256'] and direct['result']==manifest['result']
    assert manifest['exit']==0 and manifest['result']['cleared'] and manifest['result']['deaths']==0
    assert (a.route/'inputs.csv').read_bytes()==(a.discovery/'inputs.csv').read_bytes()
    assert (a.route/'trace.csv').read_bytes()==(a.discovery/'trace.csv').read_bytes()
    assert direct['frame_index_sha256']==sha(a.route/'direct-frame-index.csv')
    frame_index={int(r['frame']):r for r in csv.DictReader((a.route/'direct-frame-index.csv').open())}
    assert sorted(frame_index)==list(range(200,manifest['result']['frames']))
    paths=sorted((a.route/'frames').glob('*.png'))
    assert[int(p.stem)for p in paths]==list(range(200,manifest['result']['frames']))
    trace={int(r['frame']):r for r in csv.DictReader((a.route/'trace.csv').open())}
    oam=defaultdict(list);dma_frames=set()
    for r in csv.DictReader((a.route/'oam.csv').open()):
        dma_frames.add(int(r['frame']))
        data=bytes.fromhex(r['oamHex']);assert len(data)==256
        for i in range(0,256,4):
            y,x=data[i]+1,data[i+3]
            if 16<=y<208:oam[int(r['frame'])].append((x,y))
    hardware={};last_dma=None
    for frame in range(manifest['result']['frames']+1):
        if frame in dma_frames:last_dma=frame
        if last_dma is not None:hardware[frame+1]=oam[last_dma]
    def load(path):
        n=int(path.stem)
        with Image.open(path)as image:
            assert image.size==(256,240)
            assert sha(path)==frame_index[n]['PNG_sha256'],'Direct PNG changed since original replay'
            assert hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()==frame_index[n]['RGB_sha256']
            pixels=np.asarray(image.convert('RGBA'),dtype=np.uint8).copy().view(np.uint32).reshape(240,256)[32:208]
        mask=np.zeros((176,256),dtype=bool)
        # DMA uses the previous endFrame label. Retain the actual last DMA
        # through frames without another transfer; absent early logs do not
        # mean that hardware has no sprites. Neighbor masks remain conservative.
        for f in [n-1,n,n+1]:
            for x,y in hardware.get(f,[]):mask[max(0,y-32):min(176,y+16-32),x:min(256,x+8)]=True
        return n,pixels,mask
    previous,current=load(paths[0]),load(paths[1]);events=[];triples=0
    def active(n):
        r=trace[n]
        return r['engine']=='8'and r['mode']=='1'and r['task']=='3'
    def best_shift(other,cur,forward):
        scores=[]
        for shift in range(5):
            at=8-shift if forward else 8+shift
            valid=~(cur[2][:,8:248]|other[2][:,at:at+240])
            diff=(cur[1][:,8:248]!=other[1][:,at:at+240])&valid
            scores.append(int(np.count_nonzero(diff)))
        return min(range(5),key=lambda i:scores[i])
    for path in paths[2:]:
        following=load(path);numbers=[v[0]for v in [previous,current,following]]
        t=[trace[n]for n in numbers]
        if all(active(n)and n in hardware for n in numbers)and len({(r['world'],r['level'],r['area'])for r in t})==1:
            triples+=1
            before=best_shift(previous,current,False);after=best_shift(following,current,True)
            p0=previous[1][:,8+before:248+before];p1=current[1][:,8:248];p2=following[1][:,8-after:248-after]
            masked=previous[2][:,8+before:248+before]|current[2][:,8:248]|following[2][:,8-after:248-after]
            changed=(p0==p2)&(p1!=p0)&~masked
            count=int(np.count_nonzero(changed))
            if count>=a.minimum_pixels:
                ys,xs=np.nonzero(changed);cells=defaultdict(list)
                for y,x in zip(ys.tolist(),xs.tolist()):cells[((x+8)//16,(y+32)//16)].append((x,y))
                hits=[]
                for (col,row),points in cells.items():
                    if len(points)<a.minimum_pixels:continue
                    greens=0
                    for x,y in points:
                        v=int(p1[y,x]);red=v&255;green=(v>>8)&255;blue=(v>>16)&255
                        greens+=green>=72 and green>red*1.12 and green>blue*1.12
                    hits.append(dict(screen_cell=[col,row],pixels=len(points),green_pixels=int(greens)))
                if hits:events.append(dict(frame=current[0],alignment_shifts=[before,after],changed_pixels=count,
                    green_pixels=sum(q['green_pixels']for q in hits),cells=hits))
        previous,current=current,following
    selected=sorted(events,key=lambda q:(q['green_pixels']>0,q['changed_pixels']),reverse=True)[:12]
    sheets=[]
    for event in selected:
        n=event['frame'];image=Image.new('RGB',(768,264),(24,28,36));draw=ImageDraw.Draw(image)
        for col,frame in enumerate([n-1,n,n+1]):
            with Image.open(a.route/'frames'/f'{frame:06d}.png')as source:image.paste(source.convert('RGB'),(col*256,24))
            draw.text((col*256+5,5),f'frame {frame}',fill='white')
        for cell in event['cells']:
            x,y=cell['screen_cell'];draw.rectangle((256+x*16,y*16+24,256+x*16+15,y*16+39),outline=(255,64,64))
        out=a.output/f'candidate-{n:06d}.png';image.save(out);sheets.append(dict(frame=n,path=str(out),sha256=sha(out)))
    q=dict(scan_complete=True,accepted=False,ROM_sha256=manifest['ROM_sha256'],identity=manifest['config']['name'],mode=manifest['config']['behavior'],
        retained_PNGs=len(paths),admitted_adjacent_triples=triples,first_hardware_OAM_frame=min(hardware),candidate_events=len(events),events=events,sheets=sheets,
        manifest_sha256=sha(a.discovery/'manifest.json'),direct_proof_sha256=sha(a.route/'proof.json'),direct_frame_index_sha256=sha(a.route/'direct-frame-index.csv'),original_algorithm_sha256='b435093d658a5cd99a668b594222e9780f09376b6006509192d80cbc44de3b9c',trace_sha256=sha(a.route/'trace.csv'),oam_sha256=sha(a.route/'oam.csv'),
        driver_sha256=sha(Path(__file__)),minimum_pixels=a.minimum_pixels,
        scope='Every retained PNG is decoded; only three adjacent active same-area engine8frames with actual retained hardware OAM coverage enter the comparison. Early frames before DMA logging are not treated as sprite-free. Last DMA is retained through skipped transfers. Each image pair is aligned within the original0..4horizontal-scroll bound. Conservative neighbor DMA sprite rectangles and outer8pixels are excluded. Same-before/after yet different-middle clusters of12pixels per16pxscreen cell are candidates, ranked with green colors first. Legitimate animation/palette effects and imperfect masking can trigger candidates. Persisting changes, longer flashes, sprite/body defects, missing actors, source fidelity and other glitches are not excluded by an empty result. Each candidate needs rendered/source investigation; no automatic game-defect or all-graphics pass is claimed.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['scan_complete','identity','mode','retained_PNGs','admitted_adjacent_triples','candidate_events']},indent=2))


if __name__=='__main__':main()
