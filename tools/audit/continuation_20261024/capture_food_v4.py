"""Read-only direct-PPU observation of explicitly arranged native item fixtures."""
from pathlib import Path
import argparse,ast,csv,gzip,hashlib,json,struct,subprocess,sys,time
import numpy as np
from PIL import Image
ROOT=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover')
BASE=Path(__file__).resolve().parent
HEADER=struct.Struct('<IIQQ')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
OBSERVER=r"""
local frame=0
local raw=assert(io.open(OUTPUT..'direct.argb','wb'))
local trace=assert(io.open(OUTPUT..'trace.csv','w'))
local audio=assert(io.open(OUTPUT..'audio.csv','w'))
local inputs=assert(io.open(OUTPUT..'inputs.csv','w'))
local fields={'SelectedCharacter','CrossoverBehaviorVersion','CrossoverMenuState','GameEngineSubroutine','Player_PageLoc','Player_X_Position','Player_Y_Position','Player_State','PlayerStatus','TimerControl','GuestPowerupActive','Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue','PauseSoundQueue','AvStopwatch','AvSlash','SmBall','SmCrouch','SsHeld','SsFreeze','SsBodyStop','SsWaterExpand','InvDirty','InvHudActive','Cv3Variant','Cv3AttackAge','Cv3AttackKind','JnHealth','JnMaxHearts','JnOwnedTier','JnSelected','JnTier','JnAttack','DwHealth','DwGas','DwAdaptor','DwMode','M3Form','M3Growth','M3Poof','NativeTail','NativeStatue','KbHealth','KbCopy','KbMouth','KbAction','KbActionAge','KbFloat','KbDropKind','KbDropAge','KbMouthCopy','CdHealth','CdHeld','CdHide'}
local function r(n,i)if not L[n]then return -1 end;return emu.read(L[n]+(i or 0),emu.memType.nesDebug)end
local function cells(name,count,start)local a={};for i=start or 0,(start or 0)+count-1 do a[#a+1]=r(name,i)end;return table.concat(a,':')end
trace:write('frame,ppuFrame,cpuCycle,case,age,phase,'..table.concat(fields,',')..',selected,ownedLo,ownedHi,ammo,shots,beamTypes,enemyFlags,enemyIds,enemyStates,pickups,pickupOwners,enemyX,enemyY,blockStates,blockMetas,blockRep,popup,cv3Health,cv3Hearts,cv3Power,cv3Subweapon,cv3Shots,jnAmmo,jnShots,m3Shots\n')
audio:write('physicalFrame,address,value\n');inputs:write('physicalFrame,a,b,start,select,left,right,up,down\n')
local input=emu.setInput
emu.setInput=function(b,p)
 local a={frame+1};for _,k in ipairs({'a','b','start','select','left','right','up','down'})do a[#a+1]=b[k]and 1 or 0 end
 inputs:write(table.concat(a,',')..'\n');return input(b,p)
end
emu.addMemoryCallback(function(addr,value)if frame>=199 then audio:write(table.concat({frame+1,addr,value},',')..'\n')end end,emu.callbackType.write,0x4000,0x4017)
emu.addMemoryCallback(function(addr,value)if frame>=199 then audio:write(table.concat({frame+1,addr,value},',')..'\n')end end,emu.callbackType.write,0x5000,0x5015)
local closed=false;local stop=emu.stop
emu.stop=function(code)
 if not closed then closed=true;raw:close();trace:close();audio:close();inputs:close()end
 stop(code)
end
emu.addEventCallback(function()
 frame=frame+1;if frame<200 then return end
 local s=emu.getState();assert(s['ppu.frameCount']==frame,'Direct component capture physical frame')
 local size=emu.getScreenSize();assert(size.width==256 and size.height==240)
 local buffer=emu.getScreenBuffer();assert(#buffer==256*240)
 local packed={};for i=1,#buffer,8 do packed[#packed+1]=string.pack('<I4I4I4I4I4I4I4I4',buffer[i],buffer[i+1],buffer[i+2],buffer[i+3],buffer[i+4],buffer[i+5],buffer[i+6],buffer[i+7])end
 raw:write(string.pack('<I4I4I8I8',frame,#buffer,s['ppu.frameCount'],s['cpu.cycleCount']));raw:write(table.concat(packed));raw:flush()
 local row={frame,s['ppu.frameCount'],s['cpu.cycleCount'],COPY_CASE or HEALTH_CASE or -1,COPY_TICK or HEALTH_AGE or -1,COPY_PHASE or 'food'}
 for _,k in ipairs(fields)do row[#row+1]=r(k)end
 local c=r('SelectedCharacter');row[#row+1]=c<12 and r('InvSelected',c)or -1;row[#row+1]=c<12 and r('InvOwnedLo',c)or -1;row[#row+1]=c<12 and r('InvOwnedHi',c)or -1
 for _,v in ipairs({c<12 and cells('InvAmmo',16,c*16)or 'not-legacy',cells('RgShotType',10),cells('SmShotType',3),cells('Enemy_Flag',6),cells('Enemy_ID',6),cells('Enemy_State',6),cells('InvPickup',6),cells('InvPickupOwner',6),cells('Enemy_X_Position',6),cells('Enemy_Y_Position',6),cells('Block_State',4),cells('BlockMetasprite',4),cells('Block_RepFlag',2),cells('FloateyNum_Control',6),cells('Cv3Health',3),cells('Cv3Hearts',3),cells('Cv3Power',3),cells('Cv3Subweapon',3),cells('Cv3ShotType',4),cells('JnAmmo',10),cells('JnShotKind',6),cells('M3ShotKind',2)})do row[#row+1]=v end
 trace:write(table.concat(row,',')..'\n')
end,emu.eventType.endFrame)
"""
def run(name,source):
 out=BASE/(name+'-food-v3-direct-v1');out.mkdir(exist_ok=False);(out/'frames').mkdir()
 fixture=source/'run.lua';data=fixture.read_bytes();(out/'fixture.lua').write_bytes(data)
 observer=out/'observer.lua';observer.write_text(OBSERVER)
 wrapper=out/'run.lua';wrapper.write_text('dofile('+json.dumps(observer.as_posix())+')\ndofile('+json.dumps((out/'fixture.lua').as_posix())+')\n')
 rom=BASE/'food-candidate-v3/candidate.nes'
 cmd=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(wrapper),str(rom),'--timeout','180','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 t=time.monotonic()
 with(out/'host.log').open('w')as log:
  child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
  while child.poll()is None:
   if time.monotonic()-t>200:child.terminate();child.wait();raise RuntimeError('Capture child timed out')
   time.sleep(.1)
  code=child.returncode
 raw=out/'direct.argb';assert raw.exists(),(out/'host.log').read_text()
 archive=out/'direct.argb.gz';h=hashlib.sha256();size=0;frames=0
 with raw.open('rb')as f,archive.open('xb')as af,gzip.GzipFile(fileobj=af,mode='wb',compresslevel=1,mtime=0)as zipped,(out/'direct-frame-index.csv').open('w',newline='')as idx:
  writer=csv.writer(idx);writer.writerow(['frame','ppuFrame','cpuCycle','RGB_sha256','PNG_sha256'])
  while header:=f.read(HEADER.size):
   assert len(header)==HEADER.size
   frame,pixels,ppu,cycle=HEADER.unpack(header);assert frame==ppu==200+frames and pixels==256*240
   data=f.read(pixels*4);assert len(data)==pixels*4
   h.update(header);h.update(data);size+=len(header)+len(data);zipped.write(header);zipped.write(data)
   values=np.frombuffer(data,dtype='<u4').reshape(240,256);rgb=np.stack(((values>>16)&255,(values>>8)&255,values&255),axis=2).astype(np.uint8)
   target=out/'frames'/f'{frame:06d}.png';Image.fromarray(rgb).save(target)
   with Image.open(target)as saved:assert np.array_equal(np.asarray(saved.convert('RGB')),rgb)
   writer.writerow([frame,ppu,cycle,hashlib.sha256(rgb.tobytes()).hexdigest(),sha(target)]);frames+=1
 rebuilt=hashlib.sha256();rebuilt_size=0
 with gzip.open(archive,'rb')as f:
  while block:=f.read(1048576):rebuilt.update(block);rebuilt_size+=len(block)
 assert rebuilt_size==size==raw.stat().st_size and rebuilt.hexdigest()==h.hexdigest()==sha(raw)
 assert raw.resolve().is_relative_to(out.resolve())and archive.resolve().is_relative_to(out.resolve())
 raw.unlink()
 q=dict(passed=code==0,goal_complete=False,inventory_complete=False,exit=code,ROM_sha256=sha(rom),source_fixture=str(fixture),source_fixture_sha256=sha(fixture),immutable_fixture_copy_sha256=sha(out/'fixture.lua'),fixture_copy_exact=sha(fixture)==sha(out/'fixture.lua'),driver_sha256=sha(Path(__file__)),observer_sha256=sha(observer),harness_sha256=sha(wrapper),direct_physical_frames=frames,actual_PPU_frame_ids_complete=True,every_saved_PNG_RGB_exact=True,raw_stream_bytes=size,raw_stream_sha256=h.hexdigest(),archive_sha256=sha(archive),raw_gzip_roundtrip_exact=True,temporary_raw_removed_after_exact_lossless_roundtrip=True,trace_sha256=sha(out/'trace.csv'),inputs_sha256=sha(out/'inputs.csv'),audio_sha256=sha(out/'audio.csv'),frame_index_sha256=sha(out/'direct-frame-index.csv'),scope='Read-only direct actual PPU frames and hardware audio writes around a frozen fixture with declared map/ammo/pickup arrangements. Not an untouched campaign, source-perfect graphics/SFX proof or all-item coverage. Original fixture behavior assertions retained; physical component samples require review.')
 (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(name=name,exit=code,frames=frames,seconds=round(time.monotonic()-t,2))),flush=True)
 return q
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--version',default='1');a=p.parse_args()
 for name in a.names:
  source=(BASE/'kirby-copies-final-v3'/name.removeprefix('copies-')) if name.startswith('copies-')else BASE/'health-food-final-v3'/name.removeprefix('health-')
  run(name,source)
