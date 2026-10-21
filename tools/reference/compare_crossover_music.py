"""Compare hosted MP3 chroma with original MM2 NSF tracks; requires numpy/ffmpeg."""
from pathlib import Path
import concurrent.futures
import json
import subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/mm2-audio'

def feature(path):
    d=np.fromfile(path,dtype=np.float32);n=2048
    d=np.pad(d,(0,max(0,n-len(d))))
    a=np.lib.stride_tricks.sliding_window_view(d,n)[::256]
    a=np.abs(np.fft.rfft(a*np.hanning(n)))
    f=np.fft.rfftfreq(n,1/16000);mask=(f>80)&(f<4000)
    midi=np.round(69+12*np.log2(f[mask]/440)).astype(int)
    chroma=np.stack([a[:,mask][:,midi%12==i].sum(axis=1) for i in range(12)],axis=1)
    return chroma/np.maximum(np.linalg.norm(chroma,axis=1,keepdims=True),1e-8)

def render(item):
    name,args=item
    subprocess.run(['ffmpeg','-v','error','-y',*args,'-t','8','-ar','16000','-ac','1','-f','f32le',str(OUT/(name+'.raw'))],check=True)

def main():
    files=list((ROOT/'reference/crossover/assets/sounds').glob('*MegaMan*.mp3'))
    items=[(f'track-{i}',['-track_index',str(i),'-i',str(OUT/'megaman2.nsf')]) for i in range(24)]
    items += [(p.stem,['-i',str(p)]) for p in files]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(render,items))
    tracks=[feature(OUT/f'track-{i}.raw') for i in range(24)]
    results={}
    for p in files:
        ref=feature(OUT/(p.stem+'.raw'));rank=[]
        for i,ft in enumerate(tracks):
            score=0
            for shift in range(-15,16):
                r=ref[max(0,shift):];t=ft[max(0,-shift):];n=min(len(r),len(t))
                if n>20:score=max(score,np.sum(r[:n]*t[:n],axis=1).mean())
            rank.append((float(score),i))
        rank.sort(reverse=True)
        results[p.name]=[{'cosine_similarity':v,'zero_based_track':i} for v,i in rank[:3]]
        print(p.stem,rank[:3])
    (OUT/'comparison.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
