from pathlib import Path
import csv,gzip,hashlib,importlib.util,json,struct,subprocess,sys,time
import numpy as np
from PIL import Image,ImageDraw
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'legacy-physical-direct-v1';O.mkdir(exist_ok=False);ROM=P/'candidate.nes';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();HEADER=struct.Struct('<IIQQ')
sp=importlib.util.spec_from_file_location('image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(ROM)
summary=P/'legacy-physical-summary-v1/proof.json';q=json.loads(summary.read_text());assert q['passed']and q['ROM_sha256']==sha(ROM)
OBSERVER=r'''
local frame,nmis,updates=0,0,0
local raw=assert(io.open(OUTPUT..'direct.argb','wb'));local trace=assert(io.open(OUTPUT..'trace.csv','w'));local audio=assert(io.open(OUTPUT..'audio.csv','w'));local inputs=assert(io.open(OUTPUT..'inputs.csv','w'))
local fields={'FrameCounter','OperMode','OperMode_Task','GameEngineSubroutine','SelectedCharacter','PlayerStatus','GuestPowerupActive','Player_X_Position','Player_PageLoc','Player_Y_Position','ScreenLeft_X_Pos','ScreenLeft_PageLoc','NmiSkipped','TimerControl','InvRefill','InvRefillRemain','AvStopwatch','AvSlash','SsHeld','SmBall','InvDropKind','InvDropX','InvDropY'}
trace:write('frame,ppuFrame,cpuCycle,nmis,completedLoops,'..table.concat(fields,',')..',ownedLo,ownedHi,selected,ammo,shots,samusShots,enemies,pickupIDs,hearts,irqBankA,irqBankC\n')
audio:write('frame,address,value\n');inputs:write('frame,a,b,start,select,left,right,up,down\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function cells(n,count)local a={};for i=0,count-1 do a[#a+1]=r(n,i)end;return table.concat(a,':')end
local function actual(pc)local a=emu.convertAddress(pc);return a and a.address//8192 or -1 end
local function hook(h,f)emu.addMemoryCallback(function()if actual(h.address)~=h.physical_bank then return end;for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Exact capture NMI hook bytes')end;f()end,emu.callbackType.exec,h.address)end
local ctx;local smc
local function smcNow()local a={};for i=0,32 do a[#a+1]=emu.read(OBS_CFG.smc+i,emu.memType.nesDebug)end;return table.concat(a,':')end
hook(OBS_CFG.nmi,function()assert(not ctx,'No nested NMI');ctx={a=r('CurrentBank'),c=r('CurrentBankC')};smc=smcNow();nmis=nmis+1 end)
hook(OBS_CFG.nmi_end,function()assert(ctx and smc==smcNow(),'Inventory scene NMI preserves foreground SMC');assert(actual(0xa000)==(r('CurrentBank')&127)and actual(0xc000)==(ctx.c&127)and r('CurrentBankC')==ctx.c,'Inventory scene NMI restores actual native A/C banks');ctx=nil end)
hook(OBS_CFG.loop_end,function()updates=updates+1 end)
local input=emu.setInput;emu.setInput=function(b,p)local a={frame+1};for _,k in ipairs({'a','b','start','select','left','right','up','down'})do a[#a+1]=b[k]and 1 or 0 end;inputs:write(table.concat(a,',')..'\n');return input(b,p)end
emu.addMemoryCallback(function(a,v)if frame>=199 then audio:write(table.concat({frame+1,a,v},',')..'\n')end end,emu.callbackType.write,0x4000,0x4017)
emu.addMemoryCallback(function(a,v)if frame>=199 then audio:write(table.concat({frame+1,a,v},',')..'\n')end end,emu.callbackType.write,0x5000,0x5015)
local stop=emu.stop;local closed=false;emu.stop=function(code)if not closed then closed=true;raw:close();trace:close();audio:close();inputs:close();local f=assert(io.open(OUTPUT..'capture-native-guard.json','w'));f:write(string.format('{"passed":%s,"nmis":%d,"completedLoops":%d,"frames":%d,"observer_game_state_writes":false}',tostring(code==0 and nmis>100 and updates>100),nmis,updates,frame));f:close()end;stop(code)end
emu.addEventCallback(function()
 frame=frame+1;if frame<200 then return end
 local s=emu.getState();assert(s['ppu.frameCount']==frame,'Actual physical PPU frame ID')
 local buffer=emu.getScreenBuffer();assert(#buffer==61440,'Native256x240screen');local data={}
 for i=1,#buffer,8 do data[#data+1]=string.pack('<I4I4I4I4I4I4I4I4',buffer[i],buffer[i+1],buffer[i+2],buffer[i+3],buffer[i+4],buffer[i+5],buffer[i+6],buffer[i+7])end
 raw:write(string.pack('<I4I4I8I8',frame,#buffer,s['ppu.frameCount'],s['cpu.cycleCount']));raw:write(table.concat(data));raw:flush()
 local a={frame,s['ppu.frameCount'],s['cpu.cycleCount'],nmis,updates};for _,n in ipairs(fields)do a[#a+1]=r(n)end
 local c=r('SelectedCharacter');for _,n in ipairs({'InvOwnedLo','InvOwnedHi','InvSelected'})do a[#a+1]=r(n,c)end
 local ammo={};for i=0,15 do ammo[#ammo+1]=r('InvAmmo',c*16+i)end
 a[#a+1]=table.concat(ammo,':');for _,z in ipairs({{'RgShotType',10},{'SmShotType',3},{'Enemy_Flag',6},{'InvPickup',6}})do a[#a+1]=cells(z[1],z[2])end
 a[#a+1]=r('InvAmmo',80);a[#a+1]=actual(0xa000);a[#a+1]=actual(0xc000);trace:write(table.concat(a,',')..'\n')
end,emu.eventType.endFrame)
'''
import re
smc=int(re.search(r'al ([0-9A-Fa-f]+) \.__SMCCODE_RUN__',ROM.with_suffix('.lbl').read_text())[1],16)
report=dict(passed=False,complete=False,goal_complete=False,ROM_sha256=sha(ROM),source_summary_sha256=sha(summary),runs=[],scope='Independent exact frozen native staged item components; every actual physical PPU frame retained/indexed and PNG/RGB/gzip checked, native NMI/foreground SMC/bank restoration. Frozen behavior assertions retained. Not full natural block delivery or source-perfect graphics/audio certification. Human visual samples require review.')
for row in q['runs']:
 name=row['identity'];out=O/name;out.mkdir();(out/'frames').mkdir();fixture=out/'fixture.lua';fixture.write_bytes(Path(row['fixture']).read_bytes());assert sha(fixture)==row['fixture_sha256']
 source=Path(row['run']);assert sha(source)==row['run_sha256'];run=source.read_text();assert run.count(Path(row['fixture']).as_posix())==1;run=run.replace(Path(row['fixture']).as_posix(),fixture.as_posix())
 observer=out/'observer.lua';observer.write_text('OBS_CFG='+im.lua(dict(smc=smc,nmi=image.hook('NonMaskableInterrupt'),nmi_end=image.hook('NonMaskableInterrupt',delta='last'),loop_end=image.hook('GameLoop',delta='last')))+'\n'+OBSERVER)
 script=out/'run.lua';script.write_text('dofile('+im.lua(observer.as_posix())+')\n'+run)
 cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(ROM),'--timeout','180','--emulator',str(D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'),'--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 start=time.monotonic()
 with(out/'host.log').open('w')as log:child=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT,timeout=210)
 entry=dict(identity=name,exit=child.returncode,passed=False);report['runs'].append(entry);raw=out/'direct.argb';archive=out/'direct.argb.gz';h=hashlib.sha256();size=0;frames=[]
 if raw.exists():
  with raw.open('rb')as f,archive.open('xb')as zipped_file,gzip.GzipFile(fileobj=zipped_file,mode='wb',compresslevel=1,mtime=0)as zipped,(out/'direct-frame-index.csv').open('w',newline='')as index:
   writer=csv.writer(index);writer.writerow(['frame','ppuFrame','cpuCycle','RGB_sha256','PNG_sha256'])
   while header:=f.read(HEADER.size):
    assert len(header)==HEADER.size;frame,pixels,ppu,cycle=HEADER.unpack(header);assert frame==ppu==200+len(frames)and pixels==61440
    data=f.read(pixels*4);assert len(data)==pixels*4;h.update(header);h.update(data);size+=len(header)+len(data);zipped.write(header);zipped.write(data)
    argb=np.frombuffer(data,dtype='<u4').reshape(240,256);rgb=np.stack(((argb>>16)&255,(argb>>8)&255,argb&255),axis=2).astype(np.uint8);png=out/'frames'/('%06d.png'%frame);Image.fromarray(rgb).save(png)
    with Image.open(png)as saved:assert np.array_equal(np.asarray(saved.convert('RGB')),rgb)
    writer.writerow([frame,ppu,cycle,hashlib.sha256(rgb.tobytes()).hexdigest(),sha(png)]);frames.append(frame)
  rebuilt=hashlib.sha256();unpacked=0
  with gzip.open(archive,'rb')as f:
   while block:=f.read(1048576):rebuilt.update(block);unpacked+=len(block)
  assert unpacked==size==raw.stat().st_size and rebuilt.hexdigest()==h.hexdigest()==sha(raw)
  assert raw.resolve().is_relative_to(out.resolve())and archive.resolve().is_relative_to(out.resolve());raw.unlink()
 guard=out/'capture-native-guard.json';result=out/'native-legacy-items.json'
 if child.returncode==0:
  assert frames and json.loads(guard.read_text())['passed'];actual=json.loads(result.read_text());expected=json.loads(Path(row['source_result']).read_text());assert actual==expected,'Independent native fixture reproduces item timing, exact ownership and declared attack outcomes'
  sheet=Image.new('RGB',(1536,780),(24,28,36));draw=ImageDraw.Draw(sheet)
  for i in range(18):
   frame=frames[round(i*(len(frames)-1)/17)];sheet.paste(Image.open(out/'frames'/('%06d.png'%frame)),(i%6*256,i//6*260+20));draw.text((i%6*256+4,i//6*260+3),name+' '+str(frame),fill='white')
  overview=out/'overview.png';sheet.save(overview);entry.update(passed=True,direct_physical_frames=len(frames),actual_PPU_IDs_complete=True,every_saved_PNG_RGB_exact=True,raw_gzip_roundtrip_exact=True,raw_stream_sha256=h.hexdigest(),raw_stream_bytes=size,raw_archive_sha256=sha(archive),frame_index_sha256=sha(out/'direct-frame-index.csv'),fixture_sha256=sha(fixture),script_sha256=sha(script),observer_sha256=sha(observer),native_guard_sha256=sha(guard),result_sha256=sha(result),original_result_exact=True,overview=str(overview),overview_sha256=sha(overview))
 (out/'proof.json').write_text(json.dumps(entry,indent=2));(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(identity=name,exit=child.returncode,passed=entry['passed'],frames=len(frames),seconds=round(time.monotonic()-start,2))),flush=True)
report.update(complete=True,passed=all(z['passed']for z in report['runs']));(O/'proof.json').write_text(json.dumps(report,indent=2));(O/'progress.json').write_text(json.dumps(report,indent=2))
