"""Prepare one cold-menu, input-only Chip audio observation; never launch here."""
from pathlib import Path
from collections import deque
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')

SCRIPT=r'''
local C=assert(CHIP_AUDIO_NATIVE)
local wall,entered,updates,dmas,sourceCalls,sourceStores,irqCount=0,false,0,0,0,0,0
local src,events,gold,song,index=nil,{},nil,nil,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==14 end
local function json(v)
 if type(v)=='table'then local q={};if #v>0 then for _,x in ipairs(v)do q[#q+1]=json(x)end;return'['..table.concat(q,',')..']'end;for k,x in pairs(v)do q[#q+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(q,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local log=assert(io.open(OUTPUT..'cadence.csv','w'))
log:write('wall,updates,dmas,sourceCalls,engine,x,y,camera,nmiSkipped\n')
local image={}
for _,range in ipairs({{0x4000,0x4013},{0x4015,0x4015},{0x4017,0x4017}})do
 emu.addMemoryCallback(function(a,v)image[a]=v end,emu.callbackType.write,range[1],range[2])
end
emu.addMemoryCallback(function()if entered then dmas=dmas+1 end end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()if active()and bank(C.loopReturn)==C.loopBank then updates=updates+1 end end,emu.callbackType.exec,C.loopReturn)
emu.addMemoryCallback(function()if entered then irqCount=irqCount+1 end end,emu.callbackType.exec,L.IrqScrollSplit)
local function start(kind)
 assert(bank(C.sourcePlay)==62 and not src,'Exclusive real source entry')
 if kind=='init'then
  song=r('RgAudioSong');index=0;if gold then gold:close()end
  gold=assert(io.open(C.gold..'song-'..song..'.bin','rb'))
 else index=index+1 end
 src=true;events={}
end
local function byte()local s=assert(gold:read(1),'Bound source record');return s:byte()end
local function sourceReturn()
 if not src or bank(C.sourceReturn)~=94 then return end
 local count=byte();assert(count==#events,'Original ordered APU count song'..song..' tick'..index)
 for i=1,count do local at=0x4000+byte();local v=byte();assert(events[i][1]==at and events[i][2]==v,'Original raw ordered source APU song'..song..' tick'..index..' write'..i)end
 local n=byte()
 for i=1,n do
  local at=byte()+256*byte();local v=byte()
  local mapped=at<256 and C.sourceZp+at-0xc0 or C.sourceRam+at-0x700
  assert(emu.read(mapped,emu.memType.nesDebug)==v,'Original source state '..at..' song'..song..' tick'..index)
 end
 sourceCalls=sourceCalls+1;sourceStores=sourceStores+count;src=nil
end
if C.candidate then
 emu.addMemoryCallback(function()if bank(C.sourceInit)==62 then start('init')end end,emu.callbackType.exec,C.sourceInit)
 emu.addMemoryCallback(function()if bank(C.sourcePlay)==62 then start('play')end end,emu.callbackType.exec,C.sourcePlay)
 emu.addMemoryCallback(function(a,v)if src then events[#events+1]={0x4000+a-C.apuImage,v}end end,emu.callbackType.write,C.apuImage,C.apuImage+15)
 emu.addMemoryCallback(function()if src and bank(L.GuestNativeStatusSTA)==127 then events[#events+1]={0x4015,emu.getState()['cpu.a']}end end,emu.callbackType.exec,L.GuestNativeStatusSTA)
 emu.addMemoryCallback(sourceReturn,emu.callbackType.exec,C.sourceReturn)
end
local function menu()
 if wall<180 or wall%12~=0 then return{}end
 if r('CrossoverMenuState')==2 then
  local i=r('CrossoverMenuIndex');if i==C.target then
   if r('CdVariant')~=0 then return{select=true}end
   return{a=true}
  end
  return{[assert(C.moves[i+1])]=true}
 end
 return{start=true}
end
emu.addEventCallback(function()emu.setInput(entered and{}or menu(),0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered and active()then
  assert(r('SelectedCharacter')==14 and r('CdVariant')==0 and r('CrossoverBehaviorVersion')==0,'Actual cold-menu Chip/Easy0')
  entered=true
 end
 if entered then
  log:write(table.concat({wall,updates,dmas,sourceCalls,r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),r('NmiSkipped')},',')..'\n')
 end
 if wall>=300 and wall%120==0 then local f=assert(io.open(OUTPUT..'ppu-'..wall..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
 if wall==1300 then
  assert(entered and updates>400 and dmas>400 and irqCount>400,'Sustained actual active-game observations')
  if C.candidate then assert(sourceCalls>500 and sourceStores>1000,'Sustained original driver output/state')end
  log:close();if gold then gold:close()end
  local f=assert(io.open(OUTPUT..'audio-native.json','w'))
  f:write(json({passed=true,candidate=C.candidate,wall_frames=wall,completed_active_updates=updates,DMA_starts=dmas,source_calls=sourceCalls,ordered_original_source_stores=sourceStores,IRQ_entries=irqCount,input_only=true,no_emulated_state_writes=true,scope='Cold menu followed by idle controller input. Natural contact/death remains possible. No campaign clear, forced item use or strict matched-cadence verdict.'}));f:close();emu.stop(0)
 end
 assert(wall<=1300,'Bounded native observation')
end,emu.eventType.endFrame)
'''


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--candidate',action='store_true');a=p.parse_args()
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True);b=load(a.rom)
    expected='f7cf83bb7b3bfd7ecc138dd3a7dcf2e8a3caa27bcece32ba89ef1fa6e958f7d2' if a.candidate else '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
    assert sha(a.rom)==expected
    count=address(b,'X5MenuPresent')-address(b,'X5MenuCharacters')
    def table(n):return list(b['raw'][location(b,n):location(b,n)+count])
    target=table('X5MenuCharacters').index(14);moves=[]
    maps={n.lower():table('X5Menu'+n)for n in ['Up','Down','Left','Right']}
    for start in range(count):
        queue=deque([(start,[])]);seen={start}
        while queue:
            node,path=queue.popleft()
            if node==target:moves.append(path[0]if path else'');break
            for direction,links in maps.items():
                if links[node]not in seen:seen.add(links[node]);queue.append((links[node],path+[direction]))
        else:raise AssertionError('Menu target unreachable')
    cfg=dict(candidate=a.candidate,target=target,moves=moves,
             loopReturn=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'],0)-1,
             loopBank=(location(b,'GameLoop')-16)//8192)
    if a.candidate:
        gold=a.output/'gold';gold.mkdir();cfg['gold']=gold.as_posix()+'/'
        for song in [2,4,5,8,10,11,12,13,14,15,16]:
            payload=bytearray()
            with gzip.open(D/f'root-chip-native-music-source-v1/song-{song:02d}.jsonl.gz','rt')as f:
                for tick,line in enumerate(f):
                    if tick>2000:break
                    row=json.loads(line);payload.append(len(row['writes']))
                    for at,v in row['writes']:payload.extend([at-0x4000,v])
                    payload.append(len(row['RAM']))
                    for at,v in row['RAM']:payload.extend([at&255,at>>8,v])
            (gold/f'song-{song}.bin').write_bytes(payload)
        for key,name in [('sourceInit','ChNativeSourceInit'),('sourcePlay','ChNativeSourcePlay'),
                         ('sourceZp','ChNativeZp'),('sourceRam','ChNativeRam'),('apuImage','GuestNativeApu')]:
            cfg[key]=address(b,name)
        cfg['sourceReturn']=address(b,'ChNativeBridgeReturn')
    smc=next(g for g in b['segs'].values()if g.get('name')=='"SMCCODE"')
    guard=ROOT/'tools/audit/vehicles_audio_wiring_guards.lua'
    gc=dict(nmi=address(b,'NonMaskableInterrupt'),nmi_return=address(b,'NonMaskableInterrupt')+int(b['syms']['NonMaskableInterrupt']['size'],0)-1,
            smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],
            stack_floor=(int(smc['start'],0)+int(smc['size'],0))&255,stack_start=int(smc['start'],0)&255,music=0)
    g=guard.read_text()
    line="local chr=dofile(C.chr_observer)({out=OUTPUT,character=19})"
    assert g.count(line)==1;g=g.replace(line,'-- CHR bytes are unchanged; no CHR observer or CHR verdict in this audio-only control.')
    line='  chr.finish();assert(not chr.failure(),chr.failure())'
    assert g.count(line)==1;g=g.replace(line,'')
    script=a.output/'run.lua';script.write_text('VEHICLE_AUDIO_CONFIG='+lua(gc)+'\n'+g+'\nCHIP_AUDIO_NATIVE='+lua(cfg)+'\n'+SCRIPT)
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'
    py=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    parse='import pathlib,sys;sys.path.insert(0,sys.argv[1]);from lupa.lua54 import LuaRuntime;LuaRuntime().eval("function(s)local f,e=load(s);assert(f,e);return true end")(pathlib.Path(sys.argv[2]).read_text());print("Lua54 parse PASS")'
    proc=subprocess.run([str(py),'-c',parse,str(parser),str(script)],capture_output=True,text=True)
    (a.output/'parse.log').write_text(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stderr
    assert 'emu.write('not in script.read_text() and SCRIPT.count('addMemoryCallback')==9
    files=[script,a.rom,a.rom.with_suffix('.dbg'),a.rom.with_suffix('.lbl'),guard,
           ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/run_mesen.py',Path(__file__),
           Path('C:/Mesen2/settings.json')]
    emulator=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'
    files += [emulator,emulator.with_name('MesenCore.dll'),emulator.with_name('settings.json')]
    manifest={str(x.resolve()):sha(x)for x in files}
    manifest.update({str(x.resolve()):sha(x)for x in a.output.glob('gold/*.bin')})
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    receipt=dict(prepared=True,native_run=False,ROM_sha256=expected,candidate=a.candidate,
                 input_only=True,source_original_calls_bound=2001 if a.candidate else 0,
                 script_sha256=sha(script),manifest_sha256=sha(a.output/'manifest.json'),
                 emulator=str(emulator),bounded_wall_frames=1300,timeout_seconds=180,
                 no_runtime_callback_registration=True,no_CHR_visibility_verdict=True,
                 limits='Unrun audio-only current-candidate observation. No campaign or strict cadence acceptance.')
    (a.output/'preparation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()
