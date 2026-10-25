"""Replay a real Darkwing prefix with passive pickup stamps and call logging."""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

OBSERVER = r'''
local frame=0
local out=assert(DW_PICKUP_OUTPUT)
local f=assert(io.open(out..'pickup-calls.csv','w'))
f:write('frame,event,pc,sp,a,x,y,hp,adaptor,slot,item,owner,type,state,px,py,ex,ey\n')
local samples=assert(io.open(out..'pickup-samples.csv','w'))
samples:write('frame,slot,hp,adaptor,item,owner,type,state,px,py,ex,ey,playerBox,enemyBox\n')
local function r(n,i)return emu.read(assert(DW_L[n],n)+(i or 0),emu.memType.nesDebug)end
local function row(event,slot)
 local s=emu.getState();slot=slot or s['cpu.x']
 if slot>5 then return end
 f:write(table.concat({frame,event,s['cpu.pc'],s['cpu.sp'],s['cpu.a'],s['cpu.x'],s['cpu.y'],r('DwHealth'),r('DwAdaptor'),slot,r('InvPickup',slot),r('InvPickupOwner',slot),r('PowerUpType',slot),r('Enemy_State',slot),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot),r('Enemy_Y_Position',slot)},',')..'\n');f:flush()
end
for _,name in ipairs({'DwPreparePickup','DwCollectPickup','DwGiveItem','DwPrivatePickup'})do
 local hook=DW_HOOKS[name]
 emu.addMemoryCallback(function()
  if emu.convertAddress(hook.pc).address//8192~=hook.bank then return end
  if name~='DwPrivatePickup' or r('Enemy_ID',emu.getState()['cpu.x'])==0x2e then row(name)end
 end,emu.callbackType.exec,hook.pc)
end
emu.addMemoryCallback(function(address,value)row('stamp_'..tostring(value),address-DW_L.InvPickup)end,emu.callbackType.write,DW_L.InvPickup,DW_L.InvPickup+5)
emu.addEventCallback(function()
 frame=frame+1
 for slot=0,5 do
  if r('Enemy_Flag',slot)~=0 and r('Enemy_ID',slot)==0x2e then
   local pb,eb={},{}
   for i=0,3 do pb[#pb+1]=r('BoundingBox_UL_Corner',i);eb[#eb+1]=r('EnemyBoundingBoxCoord',slot*4+i)end
   samples:write(table.concat({frame,slot,r('DwHealth'),r('DwAdaptor'),r('InvPickup',slot),r('InvPickupOwner',slot),r('PowerUpType',slot),r('Enemy_State',slot),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot),r('Enemy_Y_Position',slot),table.concat(pb,':'),table.concat(eb,':')},',')..'\n')
  end
 end
 samples:flush()
 if frame>=1400 then f:close();samples:close();emu.stop(0)end
end,emu.eventType.endFrame)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--route',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'frames').mkdir()
    f=a.rom.with_suffix('.dbg')
    debug=f.read_text() if f.exists() else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    segments={};syms={}
    for line in debug.splitlines():
        if not line.startswith(('sym\t','seg\t')):continue
        q=dict(t.split('=',1)for t in line.split('\t',1)[1].split(',')if '='in t)
        if line.startswith('seg\t'):segments[q['id']]=q
        elif 'val'in q and q.get('type')in ('lab','equ'):syms[q['name'].strip('"')]=q
    names=['DwHealth','DwAdaptor','InvPickup','InvPickupOwner','PowerUpType','Enemy_State',
        'Enemy_Flag','Enemy_ID','Player_X_Position','Player_PageLoc','Player_Y_Position',
        'Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','BoundingBox_UL_Corner','EnemyBoundingBoxCoord']
    labels={n:int(syms[n]['val'],0)for n in names}
    hooks={}
    for n in ['DwPreparePickup','DwCollectPickup','DwGiveItem','DwPrivatePickup']:
        q=syms[n];s=segments[q['seg']];pc=int(q['val'],0)
        offset=int(s['ooffs'],0)+pc-int(s['start'],0)
        hooks[n]=dict(pc=pc,bank=(offset-16)//8192)
    def lua(value):
        if isinstance(value,dict):return '{'+','.join(k+'='+lua(v)for k,v in value.items())+'}'
        return str(value)
    observer=a.output/'observer.lua'
    observer.write_text('DW_PICKUP_OUTPUT='+json.dumps(a.output.as_posix()+'/')+'\nDW_L='+lua(labels)+'\nDW_HOOKS='+lua(hooks)+'\n'+OBSERVER)
    original=a.route/'run.lua';run=original.read_text()
    anchor='out='+json.dumps(a.route.as_posix()+'/');assert run.count(anchor)==1
    run=run.replace(anchor,'out='+json.dumps(a.output.as_posix()+'/'))
    assert run.count('replay=nil')==1
    run=run.replace('replay=nil','replay='+json.dumps((a.route/'inputs.csv').as_posix()))
    at=run.index('dofile(')
    script=a.output/'run.lua';script.write_text(run[:at]+'dofile('+json.dumps(observer.as_posix())+')\n'+run[at:])
    z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom),
        '--timeout','80','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false',
        '--option=--nes.randomizeMapperPowerOnState=false'],cwd=ROOT,capture_output=True,text=True)
    (a.output/'host.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-3000:]
    source=list(csv.DictReader((a.route/'inputs.csv').open()))
    actual=list(csv.DictReader((a.output/'inputs.csv').open()))
    assert actual==source[:len(actual)] and len(actual)>800
    q=dict(passed=True,ROM_sha256=sha(a.rom),read_only=True,prefix_inputs_exact=len(actual),metadata=labels,hooks=hooks,
        original_script_sha256=sha(original),observer_sha256=sha(observer),driver_sha256=sha(Path(__file__)),
        scope='Passive real cold-menu Darkwing prefix through frame1400. Logs actual item preparation, physical actor stamps and pickup bounds; no equipment, position or ability is granted. Not a campaign clear.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
