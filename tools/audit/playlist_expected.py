"""Generate independent native-register expectations for emulator playback QA."""
from pathlib import Path
import csv,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
catalog=json.loads((ROOT/'docs/reference/expanded-playlist.json').read_text())
types=['LT_NORMAL','LT_WATER','LT_UNDER_GROUND','LT_CASTLE','LT_COIN_HEAVEN','LT_INTRO','STAR','DIE','GAME_OVER','WIN','WIN_CASTLE','GAME_OVER','WIN','HURRY']
out=ROOT/'tests/fixtures/playlist';out.mkdir(parents=True,exist_ok=True)
manifest={'frames_per_selection':400,'registers':'$4000-$400f and masked $4015','source':'Pinned Crossover 2.02 NSFs and original Rygar native audio-driver captures','fixtures':{}}
for role,data in catalog.items():
    for phase,kind in enumerate(types):
        spec=data['types'][kind];key=spec.get('capture');state=[0]*16;status=15;encoded=bytearray()
        rows={}
        if key:
            folder='reference-audio' if spec.get('fallback') else 'reference-playlist'
            capture=ROOT/f'build/{folder}/{key}.csv'
            for row in csv.DictReader(capture.open()):
                frame,reg,value=map(int,row.values())
                if reg<16 or reg==21:rows.setdefault(frame,[]).append((reg,value))
        else:rows={0:[(21,0)]}
        length=4500 if role=='rygar' and phase==3 else 400
        for frame in range(length):
            for reg,value in rows.get(frame,[]):
                if reg==21:status=value&15
                else:state[reg]=value
            encoded.extend(state+[status])
        (out/f'{role}-{phase}.bin').write_bytes(encoded)
        manifest['fixtures'][f'{role}-{phase}.bin']={'frames':length,'capture':key,'type':kind,'sha256':hashlib.sha256(encoded).hexdigest(),'capture_sha256':hashlib.sha256(capture.read_bytes()).hexdigest() if key else None}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Wrote',len(manifest['fixtures']),'independently decoded 400-frame native APU expectations')
