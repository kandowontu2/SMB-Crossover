"""Replay exact controls and save timestamped direct-console lossless frames.

The decoder screenshot API can lag behind emulation. This uses the public
getScreenBuffer API, then independently verifies each saved PNG's RGB pixels.
"""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import json
import struct
import subprocess
import sys
import time
import numpy as np
from PIL import Image

ROOT=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover')
HEADER=struct.Struct('<IIQQ')
OBSERVER=r'''
local frame=0
local stream=assert(io.open(DIRECT_CAPTURE_OUT..'direct.argb','wb'))
local closed=false
local stop=emu.stop
emu.stop=function(code)
 if not closed then closed=true;stream:close()end
 stop(code)
end
emu.addEventCallback(function()
 frame=frame+1
 if frame<200 or frame>=DIRECT_CAPTURE_LIMIT then return end
 local state=emu.getState();local size=emu.getScreenSize()
 assert(size.width==256 and size.height==240,'Pinned direct frame size')
 assert(state['ppu.frameCount']==frame,'Direct capture is tied to actual PPU frame count')
 local buffer=emu.getScreenBuffer();assert(#buffer==256*240)
 local packed={}
 for i=1,#buffer,8 do
  packed[#packed+1]=string.pack('<I4I4I4I4I4I4I4I4',buffer[i],buffer[i+1],buffer[i+2],buffer[i+3],buffer[i+4],buffer[i+5],buffer[i+6],buffer[i+7])
 end
 stream:write(string.pack('<I4I4I8I8',frame,#buffer,state['ppu.frameCount'],state['cpu.cycleCount']))
 stream:write(table.concat(packed));stream:flush()
end,emu.eventType.endFrame)
'''


def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for data in iter(lambda:f.read(1048576),b''):h.update(data)
 return h.hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--route',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--timeout',type=int,default=240);a=p.parse_args()
    out=a.output.resolve();assert not out.is_relative_to(ROOT.resolve()),'Keep large capture evidence outside the30GB workspace'
    out.mkdir(parents=True,exist_ok=False);(out/'frames').mkdir()
    source=json.loads((a.route/'manifest.json').read_text())
    assert source['exit']==0 and source['result']['cleared']and source['result']['deaths']==0 and not source['fixed_replay']
    digest=sha(a.rom);assert source['ROM_sha256']==digest;limit=source['result']['frames']
    run=(a.route/'run.lua').read_text();old='out='+json.dumps(a.route.as_posix()+'/');assert run.count(old)==1
    run=run.replace(old,'out='+json.dumps(out.as_posix()+'/'))
    assert run.count('replay=nil')==1
    run=run.replace('replay=nil','replay='+json.dumps((a.route/'inputs.csv').as_posix()))
    assert run.count('capture=12,')==1;run=run.replace('capture=12,','capture=0,')
    observer=out/'observer.lua';observer.write_text('DIRECT_CAPTURE_OUT='+json.dumps(out.as_posix()+'/')+'\nDIRECT_CAPTURE_LIMIT='+str(limit)+'\n'+OBSERVER)
    at=run.index('dofile(');script=out/'run.lua';script.write_text(run[:at]+'dofile('+json.dumps(observer.as_posix())+')\n'+run[at:])
    command=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(a.rom.resolve()),
        '--timeout',str(a.timeout),'--emulator','C:\\Users\\kando\\Videos\\SMB Crossover Archive\\2026-10-24-native-rest-py\\mmc3-flag-fix-v23\\script-budget-probe-v2\\emulator\\Mesen.exe','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false',
        '--option=--nes.randomizeMapperPowerOnState=false']
    start=time.monotonic();raw=out/'direct.argb';archive=out/'direct.argb.gz';raw_hash=hashlib.sha256();raw_bytes=0
    with(out/'host.log').open('w')as log:
        child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        while not raw.exists():
            assert child.poll()is None,'Emulator ended before direct stream was opened'
            assert time.monotonic()-start<a.timeout+10
            time.sleep(.01)
        def read_exact(f,n):
            data=bytearray()
            while len(data)<n:
                chunk=f.read(n-len(data))
                if chunk:data.extend(chunk);continue
                assert child.poll()is None,'Direct stream ended before all expected PPU frames'
                assert time.monotonic()-start<a.timeout+10,'Direct capture host timeout'
                time.sleep(.002)
            return bytes(data)
        try:
            with raw.open('rb')as f,archive.open('xb')as zipped_file,gzip.GzipFile(fileobj=zipped_file,mode='wb',compresslevel=1,mtime=0)as zipped,(out/'direct-frame-index.csv').open('w',newline='')as index:
                writer=csv.writer(index);writer.writerow(['frame','ppuFrame','cpuCycle','RGB_sha256','PNG_sha256'])
                for expected in range(200,limit):
                    header=read_exact(f,HEADER.size);frame,pixels,ppu,cycle=HEADER.unpack(header)
                    assert frame==ppu==expected and pixels==256*240
                    data=read_exact(f,pixels*4);raw_hash.update(header);raw_hash.update(data);raw_bytes+=len(header)+len(data)
                    zipped.write(header);zipped.write(data)
                    values=np.frombuffer(data,dtype='<u4').reshape(240,256)
                    rgb=np.stack(((values>>16)&255,(values>>8)&255,values&255),axis=2).astype(np.uint8)
                    target=out/'frames'/f'{frame:06d}.png';Image.fromarray(rgb).save(target)
                    with Image.open(target)as saved:assert np.array_equal(np.asarray(saved.convert('RGB')),rgb)
                    writer.writerow([frame,ppu,cycle,hashlib.sha256(rgb.tobytes()).hexdigest(),sha(target)])
                code=child.wait(timeout=max(20,a.timeout+15-(time.monotonic()-start)))
                assert code==0,'See retained host log'
                assert f.read()==b'','Unexpected extra direct records'
        except BaseException:
            if child.poll()is None:child.terminate();child.wait(timeout=15)
            raise
    assert raw.stat().st_size==raw_bytes and sha(raw)==raw_hash.hexdigest()
    rebuilt=hashlib.sha256();size=0
    with gzip.open(archive,'rb')as f:
        while block:=f.read(1024*1024):rebuilt.update(block);size+=len(block)
    assert size==raw_bytes and rebuilt.hexdigest()==raw_hash.hexdigest()
    for name in ['inputs.csv','trace.csv']:assert(out/name).read_bytes()==(a.route/name).read_bytes(),name
    result=json.loads((out/'result.json').read_text());assert result==source['result']
    chr_proof=json.loads((out/'chr-commit.json').read_text());assert chr_proof['passed']
    # Only this newly generated temporary raw stream is removed. Every original
    # byte remains in the independently round-tripped lossless gzip archive.
    assert raw.resolve().is_relative_to(out)and archive.resolve().is_relative_to(out)
    raw.unlink()
    q=dict(passed=True,goal_complete=False,ROM_sha256=digest,identity=source['config']['name'],mode=source['config']['behavior'],
        source_discovery_manifest_sha256=sha(a.route/'manifest.json'),source_inputs_sha256=sha(a.route/'inputs.csv'),
        fixed_inputs_and_trace_exact=True,result=result,direct_frames=limit-200,
        actual_PPU_frame_ids_complete=True,every_saved_PNG_RGB_exact=True,frame_index_sha256=sha(out/'direct-frame-index.csv'),
        raw_stream_bytes=raw_bytes,raw_stream_sha256=raw_hash.hexdigest(),raw_lossless_archive=dict(path=str(archive),sha256=sha(archive)),
        raw_gzip_roundtrip_exact=True,temporary_raw_removed_after_exact_lossless_roundtrip=True,
        observer_sha256=sha(observer),driver_sha256=sha(Path(__file__)),body_chr=chr_proof,
        scope='Read-only public direct console screen buffer at each actual PPU endFrame, not asynchronous decoder PNG output. Complete200..endpoint-1PPU IDs, RGB-verified PNGs and full lossless raw record archive. Independent original inputs/trace and zero-death movable1-2result are exact. This repairs evidence capture only; lag, source fidelity, other graphic/ability defects, every-item and final mapper work remain open.')
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
