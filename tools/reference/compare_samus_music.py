"""Identify hosted Samus music against native Metroid APU renders."""
from pathlib import Path
import concurrent.futures
import json
import subprocess
import numpy as np
from compare_crossover_music import feature

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/samus-audio'

def render(item):
    name,path=item
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(path),'-t','8',
        '-ar','16000','-ac','1','-f','f32le',str(OUT/(name+'.raw'))],check=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rom=Path('C:/NES/Metroid (USA).nes').read_bytes()
    songs={'brinstar':(1,1,0),'norfair':(2,8,0),'kraid':(4,16,0),
      'ridley':(5,128,0),'tourian':(1,64,0),'item':(1,32,0),
      'fade':(1,0,128),'powerup':(1,0,64),'intro':(0,0,16),'ending':(0,0,32)}
    items=[]
    for name,(bank,flag,multi) in songs.items():
        header=bytearray(128);header[:5]=b'NESM\x1a';header[5:8]=bytes([1,1,1])
        header[8:14]=bytes([0,0xa0,0,0xc0,0xb4,0xb3])
        header[110:112]=(16639).to_bytes(2,'little')
        data=rom[16+bank*0x4000+0x2000:16+(bank+1)*0x4000]
        # Reset engine; enable APU; queue one song in the unmodified ROM.
        init=bytes([0xa9,0x0f,0x8d,0x15,0x40,0x20,0x04,0xb4,
          0xa9,1,0x8d,0x2c,6,0xa9,flag,0x8d,0x85,6,
          0xa9,multi,0x8d,0x84,6,0x60])
        path=OUT/(name+'.nsf');path.write_bytes(header+data+init)
        items.append((name,path))
    refs=list((ROOT/'reference/crossover/assets/sounds').glob('*Samus*.mp3'))
    items += [(p.stem,p) for p in refs]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(render,items))
    tracks={name:feature(OUT/(name+'.raw')) for name in songs}
    results={}
    for refpath in refs:
        ref=feature(OUT/(refpath.stem+'.raw'));rank=[]
        for name,ft in tracks.items():
            score=0
            for shift in range(-30,31):
                r=ref[max(0,shift):];t=ft[max(0,-shift):];n=min(len(r),len(t))
                if n>20:score=max(score,np.sum(r[:n]*t[:n],axis=1).mean())
            rank.append((float(score),name))
        rank.sort(reverse=True)
        results[refpath.name]=[{'cosine_similarity':v,'track':name} for v,name in rank[:3]]
        print(refpath.stem,rank[:3])
    (OUT/'comparison.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
