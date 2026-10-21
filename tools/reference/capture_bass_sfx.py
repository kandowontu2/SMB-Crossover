"""Capture the exact NSF tracks selected by 2.02 MusicInfo for Bass.

These are reference-only NSF runs, not gameplay tests. Source bytes remain
unchanged; only the temporary NSF's starting-song header is selected.
"""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen

NAMES=['Shoot','Land','TakeDamage','Die','Deflect','GetEnergy','GetNewLife',
       'HitEnemy','Teleport','ChargeKick','MetalBlade','PharaohShotSmall',
       'PharaohShotBig','WaterShieldExpand']


def main():
    out=ROOT/'build/reference-bass-sfx';out.mkdir(exist_ok=True)
    base=ROOT/'reference/crossover2/extracted'
    scriptbase=base/'scripts/com/smbc/sound'
    source=(scriptbase/'MusicInfo.as').read_text()
    plan={}
    for name in NAMES:
        match=re.search(r'SFX_MegaMan'+name+r'Snd:Array = addSfx\(\[\[MegaMan(\d)Nsf,NSF,(\d+),',source)
        assert match,name
        game,track=map(int,match.groups())
        embed=(scriptbase/f'MusicInfo_MegaMan{game}Nsf.as').read_text()
        asset=re.search(r'source="/_assets/([^"]+)"',embed)[1]
        path=base/'binaryData'/asset
        assert path.exists(),path
        plan[name]={'game':game,'track':track,'source':path.relative_to(ROOT).as_posix(),
                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    def capture(name):
        spec=plan[name];data=bytearray((ROOT/spec['source']).read_bytes())
        data[7]=spec['track']
        nsf=out/(name+'.nsf');nsf.write_bytes(data)
        csv=out/(name+'.csv')
        script=out/(name+'.lua')
        script.write_text(f'AUDIO_OUTPUT=[=[{csv.as_posix()}]=]\nAUDIO_BEGIN=0\nAUDIO_END=180\nAUDIO_NATIVE="nsf"\nAUDIO_FREEZE=false\ndofile([=[{(ROOT/"tools/reference/capture_expanded_audio.lua").as_posix()}]=])\n')
        if run_mesen.run(script,nsf,timeout=30):raise RuntimeError(name)
        spec['capture_sha256']=hashlib.sha256(csv.read_bytes()).hexdigest()
        return name
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(capture,plan):print('Captured',result,flush=True)
    (out/'source.json').write_text(json.dumps(plan,indent=2)+'\n')


if __name__=='__main__':main()
