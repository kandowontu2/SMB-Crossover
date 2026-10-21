"""Extract native Rygar songs from the user's pinned ROM, without changing it."""
from pathlib import Path
import concurrent.futures,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen

def main():
    source=Path('C:/NES/Rygar (USA).nes')
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest=='965330fed9f5b8492452f3b53084752e83b7f899a1f88f3c475ece2fde6f9231'
    out=ROOT/'build/reference-playlist';out.mkdir(exist_ok=True)
    def capture(track):
        key=f'rygar-{track}';csv=out/(key+'.csv');meta=out/(key+'.complete.json')
        if csv.exists() and meta.exists():return key+' cached'
        script=out/(key+'.lua')
        script.write_text(f'AUDIO_OUTPUT=[=[{csv.as_posix()}]=]\nAUDIO_BEGIN=300\nAUDIO_END=10300\nAUDIO_NATIVE="rygar"\nAUDIO_FREEZE=true\nAUDIO_TRACK={track}\ndofile([=[{(ROOT/"tools/reference/capture_expanded_audio.lua").as_posix()}]=])\n')
        if run_mesen.run(script,source,timeout=120):raise RuntimeError(key)
        meta.write_text(json.dumps({'frames':10000,'source_sha256':digest,'capture_sha256':hashlib.sha256(csv.read_bytes()).hexdigest(),'native_driver_song':track,'extraction_fixture':True}))
        return key+' complete'
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(capture,range(1,14)):print(result,flush=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    catalog=ROOT/'docs/reference/expanded-playlist.json'
    playlist=json.loads(catalog.read_text())
    # Rygar is an addition to this port, so its SMB area assignments are ours.
    # Numbers are actual native driver IDs, not guessed soundtrack titles.
    mapping={'LT_NORMAL':5,'LT_UNDER_GROUND':6,'LT_WATER':9,'LT_CASTLE':4,
             'LT_PIPE_BONUS':6,'LT_COIN_HEAVEN':12,'LT_INTRO':3,'STAR':11,'HURRY':11}
    specs={kind:{'song':f'Native song {track:02X}','track':track,'capture':f'rygar-{track}'} for kind,track in mapping.items()}
    for kind,key in [('DIE','death'),('GAME_OVER','death'),('WIN','victory'),('WIN_CASTLE','victory')]:
        specs[kind]={'song':'SMB event fallback','capture':key,'fallback':True}
    playlist['rygar']={'source':'User-supplied Rygar (USA).nes','sha256':digest,
                       'extraction':'Native $e000 audio driver; $0740 song queue; bank 3; frozen-world extraction fixture',
                       'area_assignments_are_port_adaptations':True,'types':specs}
    catalog.write_text(json.dumps(playlist,indent=2)+'\n')

if __name__=='__main__':main()
