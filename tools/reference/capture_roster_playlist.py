"""Capture the pinned 2.02 playlists, without modifying original assets."""
from pathlib import Path
import concurrent.futures,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen
OUT=ROOT/'build/reference-playlist'
GAMES={'bass':'MegaMan10','ryu':'NinjaGaiden','sophia':'BlasterMaster'}
TYPES=['LT_NORMAL','LT_UNDER_GROUND','LT_WATER','LT_CASTLE','LT_PIPE_BONUS','LT_COIN_HEAVEN','LT_INTRO','STAR','HURRY','DIE','WIN','WIN_CASTLE','GAME_OVER']
def main():
    OUT.mkdir(exist_ok=True)
    previous=ROOT/'docs/reference/expanded-playlist.json'
    plan={k:v for k,v in json.loads(previous.read_text()).items() if k not in GAMES} if previous.exists() else {}
    jobs={}
    for role,game in GAMES.items():
        path=ROOT/f'reference/crossover2/extracted/scripts/com/explodingRabbit/cross/games/Game{game}.as'
        s=path.read_text()
        songs={n:int(track) for n,track in re.findall(r'const (\w+):Song = addSong\(this.Nsf,(\d+),',s)}
        source=next((ROOT/'reference/crossover2/extracted/binaryData').glob(f'*Game{game}_Nsf.bin'))
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        choices=dict(re.findall(r'addToTypePlayList\((\w+),(?:this\.)?(\w+)\);',s))
        plan[role]={'source':str(source.relative_to(ROOT)).replace('\\','/'),'sha256':digest,'game_source':str(path.relative_to(ROOT)).replace('\\','/'),'types':{}}
        for kind in TYPES:
            name=choices[kind];track=songs.get(name)
            plan[role]['types'][kind]={'song':name,'track':track}
            if track is None:continue
            key=f'{role}-{track}'
            length=10000 if kind.startswith('LT_') or kind in ('STAR','HURRY') else 1200
            if key in jobs:jobs[key]['length']=max(length,jobs[key]['length'])
            else:jobs[key]={'role':role,'track':track,'source':source,'length':length}
            plan[role]['types'][kind]['capture']=key
    (ROOT/'docs/reference/expanded-playlist.json').write_text(json.dumps(plan,indent=2)+'\n')
    def capture(item):
        key,job=item;csv=OUT/(key+'.csv')
        if csv.exists() and (OUT/(key+'.complete.json')).exists():return key+' cached'
        rom=OUT/(key+'.nsf');data=bytearray(job['source'].read_bytes());data[7]=job['track'];rom.write_bytes(data)
        script=OUT/(key+'.lua')
        script.write_text(f'AUDIO_OUTPUT=[=[{csv.as_posix()}]=]\nAUDIO_BEGIN=0\nAUDIO_END={job["length"]}\nAUDIO_NATIVE="nsf"\nAUDIO_FREEZE=false\ndofile([=[{(ROOT/"tools/reference/capture_expanded_audio.lua").as_posix()}]=])\n')
        if run_mesen.run(script,rom,timeout=120):raise RuntimeError(key)
        (OUT/(key+'.complete.json')).write_text(json.dumps({'frames':job['length'],'source_sha256':hashlib.sha256(job['source'].read_bytes()).hexdigest(),'capture_sha256':hashlib.sha256(csv.read_bytes()).hexdigest()}))
        return key+' complete'
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(capture,jobs.items()):print(result,flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
