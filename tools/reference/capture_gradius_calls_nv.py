"""Capture original NSF driver calls, stopping before a player advances songs."""
from pathlib import Path
import concurrent.futures
import gzip
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen

OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv/gradius-call-captures-v1')


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    plan = json.loads((ROOT / 'reference/new-roster-audio/playlist-plan.json').read_text())['vic']
    original = (ROOT / plan['source']).read_bytes()
    assert hashlib.sha256(original).hexdigest() == plan['source_sha256']
    def capture(song):
        folder = OUT / f'track-{song:02d}'; folder.mkdir()
        payload = bytearray(original); payload[7] = song
        (folder / 'source.nsf').write_bytes(payload)
        lua = r'''local calls,inits,writes,frames=0,0,0,0
local done=false
local out=assert(io.open(OUTPUT..'native-calls.csv','w'));out:write('call,register,value,pc\n')
local function finish(reason)
 if done then return end;done=true;out:close()
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(string.format('{"song":%d,"calls":%d,"inits":%d,"writes":%d,"frames":%d,"reason":"%s"}',SONG,calls,inits,writes,frames,reason));f:close()
 print('PASS original source call capture '..SONG..' '..reason..' calls='..calls);emu.stop(0)
end
emu.addMemoryCallback(function()
 if done then return end
 inits=inits+1
 if inits>1 then finish('host-reinitialization');return end
 assert(emu.getState()['cpu.a']==SONG-1,'First native initialization is the requested original song')
end,emu.callbackType.exec,0xec48)
emu.addMemoryCallback(function()
 if done then return end
 if calls==15000 then finish('complete-call-limit');return end
 calls=calls+1
end,emu.callbackType.exec,0xed30)
emu.addMemoryCallback(function(address,value)
 if done or inits~=1 then return end
 local pc=emu.getState()['cpu.pc']
 -- The NSF player's own silence/reset writes are not part of the source driver.
 if pc<0xebf0 then return end
 writes=writes+1;out:write(calls..','..(address-0x4000)..','..value..','..pc..'\n')
end,emu.callbackType.write,0x4000,0x4017)
emu.addEventCallback(function()
 frames=frames+1
 if frames>16000 then error('Source call capture did not finish')end
end,emu.eventType.endFrame)
'''
        script = folder / 'capture.lua'
        script.write_text(f'OUTPUT=[=[{folder.as_posix()}/]=]\nSONG={song}\n' + lua)
        namespace = dict(run_mesen.__dict__)
        code = (ROOT / 'tools/run_mesen.py').read_text().replace("    output = ROOT / 'build/verification'\n", '    output = ISOLATED_OUTPUT\n')
        namespace.update(__file__=str(ROOT / 'tools/run_mesen.py'), __name__='_gradius_calls_nv', ISOLATED_OUTPUT=folder)
        exec(compile(code, str(ROOT / 'tools/run_mesen.py'), 'exec'), namespace)
        result = namespace['run'](script, folder / 'source.nsf', timeout=55)
        assert result == 0, song
        path = folder / 'native-calls.csv'; raw = path.read_bytes()
        packed = path.with_suffix('.csv.gz'); packed.write_bytes(gzip.compress(raw, mtime=0))
        assert gzip.decompress(packed.read_bytes()) == raw
        path.unlink()
        return song, dict(path=str(packed), capture_sha256=hashlib.sha256(raw).hexdigest(),
                          result=json.loads((folder / 'result.json').read_text()), source_sha256=plan['source_sha256'])
    report = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for song, result in pool.map(capture, sorted(set(plan['tracks'].values()))):
            report[song] = result
            (OUT / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
            print(song, result['result'], flush=True)


if __name__ == '__main__':
    main()
