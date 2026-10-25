"""Independent Mesen TMNT NSF calls; stop before host song advancement."""
from pathlib import Path
import argparse
import concurrent.futures
import gzip
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--songs',type=int,nargs='+',default=list(range(1,17)));a=p.parse_args()
    assert len(set(a.songs))==len(a.songs)and all(1<=s<=16 for s in a.songs)
    a.output.mkdir(parents=True,exist_ok=False)
    source=ROOT/'reference/new-roster-audio/tmnt/Teenage Mutant Ninja Turtles [Gekikame Ninja Den] (1989-05-12)(Konami).nsf'
    raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    assert digest=='f220e8d069e321f392526d41e46f5d0f72966d5a22e56d2b269607c678bd58d9'
    def run(song):
        d=a.output/f'song-{song:02d}';d.mkdir();payload=bytearray(raw);payload[7]=song
        nsf=d/'source.nsf';nsf.write_bytes(payload)
        lua='''local plays,inits,writes,frames=0,0,0,0
local done=false
local f=assert(io.open(TEST_DIR..'calls.csv','w'));f:write('call,address,value,pc\\n')
local function finish(reason)
 if done then return end;done=true;f:close()
 local p=assert(io.open(TEST_DIR..'result.json','w'))
 p:write(string.format('{"passed":true,"song":%d,"play_calls":%d,"initializations":%d,"writes":%d,"frames":%d,"reason":"%s"}\\n',SONG,plays,inits,writes,frames,reason));p:close();emu.stop(0)
end
emu.addMemoryCallback(function()
 if done then return end;inits=inits+1
 if inits>1 then finish('host-song-advancement');return end
 assert(emu.getState()['cpu.a']==SONG-1,'Original init selected requested source song')
end,emu.callbackType.exec,0xc000)
emu.addMemoryCallback(function()
 if done then return end
 if plays==12000 then finish('complete-call-bound');return end
 plays=plays+1
end,emu.callbackType.exec,0x8644)
emu.addMemoryCallback(function(at,v)
 if done or inits~=1 then return end
 local pc=emu.getState()['cpu.pc']
 if not(pc>=0x8612 and pc<0xc018)then return end
 f:write(string.format('%d,%d,%d,%d\\n',plays-1,at,v,pc));writes=writes+1
end,emu.callbackType.write,0x4000,0x4017)
emu.addEventCallback(function()
 frames=frames+1;assert(frames<14000,'Original capture is bounded')
end,emu.eventType.endFrame)
'''
        script=d/'run.lua';script.write_text('SONG='+str(song)+'\n'+lua)
        z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(d),str(script),str(nsf),'--timeout','90'],capture_output=True,text=True)
        (d/'host.log').write_text(z.stdout+z.stderr)
        assert z.returncode==0,(song,z.stdout[-1000:],z.stderr[-1000:])
        data=(d/'calls.csv').read_bytes();packed=d/'calls.csv.gz';packed.write_bytes(gzip.compress(data,mtime=0))
        assert gzip.decompress(packed.read_bytes())==data
        return dict(song=song,source_NSF_sha256=digest,selected_header_NSF_sha256=hashlib.sha256(payload).hexdigest(),
                    CSV_sha256=hashlib.sha256(data).hexdigest(),packed_sha256=hashlib.sha256(packed.read_bytes()).hexdigest(),
                    result=json.loads((d/'result.json').read_text()))
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        for q in pool.map(run,a.songs):
            results.append(q);(a.output/'manifest.json').write_text(json.dumps(dict(passed=False,complete=False,runs=results),indent=2)+'\n')
            print(q['song'],q['result'],flush=True)
    report=dict(passed=True,complete=True,source_NSF_sha256=digest,runs=results,
                tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Original Mesen NSF hardware writes grouped by native init/play entry. Stops before any host song advancement; no game integration claim.')
    (a.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
