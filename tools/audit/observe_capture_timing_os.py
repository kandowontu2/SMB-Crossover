"""Compare decoder PNGs with the direct console screen buffer on one prefix."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import subprocess
import sys
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OBSERVER=r'''
local frame=0
local f=assert(io.open(CAPTURE_TIMING_OUT..'state.csv','w'))
f:write('frame,ppuFrame,scanline,cycle,camera,irqX,dmaCount\n')
local dma=0
emu.addMemoryCallback(function()dma=dma+1 end,emu.callbackType.write,0x4014)
local function r(n)if not L[n]then return -1 end;return emu.read(L[n],emu.memType.nesDebug)end
emu.addEventCallback(function()
 frame=frame+1
 if frame>=1996 and frame<=2010 then
  local s=emu.getState();local size=emu.getScreenSize()
  assert(size.width==256 and size.height==240)
  local buffer=emu.getScreenBuffer();assert(#buffer==256*240)
  local bytes={}
  for i=1,#buffer do bytes[i]=string.pack('<I4',buffer[i])end
  local out=assert(io.open(CAPTURE_TIMING_OUT..string.format('%06d',frame)..'.argb','wb'));out:write(table.concat(bytes));out:close()
  out=assert(io.open(CAPTURE_TIMING_OUT..string.format('%06d',frame)..'.png','wb'));out:write(emu.takeScreenshot());out:close()
  local palette={};for i=0,31 do palette[#palette+1]=string.format('%02x',emu.read(0x3f00+i,emu.memType.nesPpuDebug))end
  out=assert(io.open(CAPTURE_TIMING_OUT..string.format('%06d',frame)..'-palette.txt','w'));out:write(table.concat(palette));out:close()
  f:write(table.concat({frame,s['ppu.frameCount']or -1,s['ppu.scanline'],s['cpu.cycleCount']or -1,r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),r('IrqNewScroll'),dma},',')..'\n');f:flush()
 end
 if frame>=2012 then f:close();emu.stop(0)end
end,emu.eventType.endFrame)
'''


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--route',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);(a.output/'frames').mkdir()
    run=(a.route/'run.lua').read_text();anchor='out='+json.dumps(a.route.as_posix()+'/');assert run.count(anchor)==1
    run=run.replace(anchor,'out='+json.dumps(a.output.as_posix()+'/'))
    assert run.count('replay=nil')==1
    run=run.replace('replay=nil','replay='+json.dumps((a.route/'inputs.csv').as_posix())).replace('capture=12,','capture=0,')
    observer=a.output/'observer.lua';observer.write_text('CAPTURE_TIMING_OUT='+json.dumps(a.output.as_posix()+'/')+'\n'+OBSERVER)
    at=run.index('dofile(');script=a.output/'run.lua';script.write_text(run[:at]+'dofile('+json.dumps(observer.as_posix())+')\n'+run[at:])
    z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom.resolve()),
        '--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false',
        '--option=--nes.randomizeMapperPowerOnState=false'],cwd=ROOT,capture_output=True,text=True)
    (a.output/'host.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-3000:]
    for name in ['inputs.csv','trace.csv']:
        old=list(csv.DictReader((a.route/name).open()));new=list(csv.DictReader((a.output/name).open()))
        assert len(new)>1900 and new==old[:len(new)],name
    comparisons=[];direct={}
    for n in range(1996,2011):
        values=np.frombuffer((a.output/f'{n:06d}.argb').read_bytes(),dtype='<u4').reshape(240,256)
        rgb=np.stack(((values>>16)&255,(values>>8)&255,values&255),axis=2).astype(np.uint8)
        direct[n]=rgb;Image.fromarray(rgb).save(a.output/f'{n:06d}-direct.png')
        with Image.open(a.output/f'{n:06d}.png')as img:png=np.asarray(img.convert('RGB'))
        comparisons.append(dict(frame=n,direct_equals_new_decoder_PNG=bool(np.array_equal(rgb,png)),
            different_pixels=int(np.count_nonzero(np.any(rgb!=png,axis=2)))))
    matching=[]
    retained=a.route.parent/('replay-'+json.loads((a.route/'manifest.json').read_text())['config']['name']+'-hard-v1')
    assert retained.is_dir()
    for n in range(1998,2009):
        with Image.open(retained/'frames'/f'{n:06d}.png')as img:rgb=np.asarray(img.convert('RGB'))
        matches=[k for k,v in direct.items()if np.array_equal(rgb,v)]
        matching.append(dict(retained_frame=n,matches_direct_frames=matches))
    q=dict(probe_complete=True,accepted=False,ROM_sha256=sha(a.rom),read_only=True,inputs_and_trace_prefix_exact=True,
        comparisons=comparisons,retained_decoder_to_direct_matches=matching,driver_sha256=sha(Path(__file__)),observer_sha256=sha(observer),
        scope='Read-only exact recorded Mike Hard prefix. Direct console screen pixels and decoder PNGs are captured during the same endFrame callbacks1996..2010, alongside actual PPU frame/scroll and palette bytes. This investigates capture/renderer timing; no game change or scrolling repair is claimed.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
