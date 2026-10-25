"""Matched ordinary-input native V39/V42 parser cycles and physical-frame cadence."""
from pathlib import Path
import argparse,csv,json,subprocess,sys
from mmc3_native_v42_qualify import ROOT,D,V,sha,lua,hook,bind_guard
from check_tmnt_render_oa import address,location

OBSERVER=r'''
local C=PROFILE
local function r(n,i)return emu.read(C.ram[n]+(i or 0),emu.memType.nesDebug)end
local function state()return emu.getState()end
local function frame(s)return s['ppu.frameCount']end
local function actual(h)local p=emu.convertAddress(h.address);return p and p.address//8192==h.physical_bank end
local function install(h,fn)
 emu.addMemoryCallback(function()
  if not actual(h)then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Profile actual opcode')end
  fn(state())
 end,emu.callbackType.exec,h.address)
end
local interruptCycles=0;local starts={};local updates=0;local loops=0;local totalActive=0
local columns=assert(io.open(ROSTER_CONFIG.out..'parser-cycles.csv','w'))
columns:write('frame,x,page,column,metatiles,inclusiveCycles,interruptCycles,parserCycles,startCycle,endCycle\n')
local frames=assert(io.open(ROSTER_CONFIG.out..'cadence.csv','w'))
frames:write('frame,cycle,world,level,engine,x,y,completedUpdates,completedLoops\n')
for _,p in ipairs(C.interrupts)do
 local start
 install(p.entry,function(s)assert(not start,'Profile interrupt nesting');start=s['cpu.cycleCount']end)
 install(p.exit,function(s)assert(start,'Profile interrupt matching');interruptCycles=interruptCycles+s['cpu.cycleCount']-start+13;start=nil end)
end
local parser
install(C.column_start,function(s)
 if s['cpu.x']~=0 then return end
 assert(not parser,'Profile column not reentered')
 local bytes={};for i=0,12 do bytes[#bytes+1]=string.format('%02x',r('MetatileBuffer',i))end
 parser={cycle=s['cpu.cycleCount'],ints=interruptCycles,sp=s['cpu.sp'],frame=frame(s),x=r('Player_X_Position')+256*r('Player_PageLoc'),page=r('R7'),column=r('BlockBufferColumnPos'),tiles=table.concat(bytes)}
end)
install(C.column_end,function(s)
 if not parser or parser.sp~=s['cpu.sp']then return end
 local elapsed=s['cpu.cycleCount']-parser.cycle;local ints=interruptCycles-parser.ints
 columns:write(table.concat({parser.frame,parser.x,parser.page,parser.column,parser.tiles,elapsed,ints,elapsed-ints,parser.cycle,s['cpu.cycleCount']},',')..'\n');columns:flush();parser=nil
end)
install(C.loop_end,function()
 loops=loops+1
 if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('WorldNumber')==0 and r('LevelNumber')==0 then updates=updates+1;totalActive=totalActive+1 end
end)
emu.addEventCallback(function()
 local s=state();local f=frame(s)
 frames:write(table.concat({f,s['cpu.cycleCount'],r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),updates,loops},',')..'\n');frames:flush();updates=0;loops=0
 if f==C.limit or(C.active_limit and totalActive>=C.active_limit)then columns:close();frames:close();emu.stop(0)end
end,emu.eventType.endFrame)
'''

def run(rom,route,out,limit,matched=False):
    out.mkdir(parents=True,exist_ok=False);(out/'frames').mkdir()
    b,guard=bind_guard(rom,out)
    text=(route/'policy.lua').read_text();_,body=text.split('\n',1)
    if matched:body='return function(c)return{right=true,b=true}end\n'
    policy=out/'policy.lua';policy.write_text('dofile('+lua(guard.as_posix())+')\n'+body)
    start=location(b,'ChkMTLow');tail=b['raw'].find(bytes([0xe0,0x0d,0x90]),start,start+100)
    assert tail>0 and b['raw'][tail+4]==0x60
    enddelta=tail+4-start
    ram=['Player_X_Position','Player_PageLoc','Player_Y_Position','R7','MetatileBuffer','BlockBufferColumnPos','OperMode','OperMode_Task','GameEngineSubroutine','WorldNumber','LevelNumber']
    interrupts=[]
    for n in ['NonMaskableInterrupt','IrqScrollSplit']:
        size=int(b['syms'][n]['size']);assert b['raw'][location(b,n)+size-1]==0x40
        interrupts.append(dict(entry=hook(b,n),exit=hook(b,n,size-1)))
    cfg=dict(ram={n:address(b,n) for n in ram},limit=limit,active_limit=128 if matched else None,
             column_start=hook(b,'ChkMTLow'),column_end=hook(b,'ChkMTLow',enddelta),
             loop_end=hook(b,'GameLoop',int(b['syms']['GameLoop']['size'])-1),interrupts=interrupts)
    observer=out/'observer.lua';observer.write_text('PROFILE='+lua(cfg)+'\n'+OBSERVER)
    runtext=(route/'run.lua').read_text()
    for old,new in [('out='+lua(route.as_posix()+'/'),'out='+lua(out.as_posix()+'/')),
                    ('policy='+lua((route/'policy.lua').as_posix()),'policy='+lua(policy.as_posix())),
                    ('replay=nil','replay=nil' if matched else 'replay='+lua((route/'inputs.csv').as_posix()))]:
        assert runtext.count(old)==1,(old,runtext[:1000]);runtext=runtext.replace(old,new)
    at=runtext.index('dofile(')
    script=out/'run.lua';script.write_text(runtext[:at]+'dofile('+lua(observer.as_posix())+')\n'+runtext[at:])
    cmd=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--emulator',str(D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'),
         '--output',str(out),str(script),str(rom),'--timeout','240','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    with (out/'host.log').open('w') as log:code=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
    columns=list(csv.DictReader((out/'parser-cycles.csv').open()))
    frames=list(csv.DictReader((out/'cadence.csv').open()))
    active=[r for r in frames if r['engine']=='8' and r['world']==r['level']=='0']
    result=dict(passed=code==0,exit=code,ROM_sha256=sha(rom),frame_limit=limit,
                actual_physical_frames=len(frames),native_columns=len(columns),active_physical_frames=len(active),
                completed_game_updates=sum(int(r['completedUpdates']) for r in active),
                active_frames_with_update=sum(int(r['completedUpdates'])>0 for r in active),
                updates_per_physical_frame=sum(int(r['completedUpdates']) for r in active)/max(1,len(active)),
                matched_constant_right_fire_scene=matched,final_native_position=[int(frames[-1][n])for n in ['x','y']],
                parser_exclusive_cycles_total=sum(int(r['parserCycles']) for r in columns),
                parser_inclusive_cycles_total=sum(int(r['inclusiveCycles']) for r in columns),
                guard_bindings_sha256=sha(out/'guard-bindings.json'),observer_sha256=sha(observer),
                parser_csv_sha256=sha(out/'parser-cycles.csv'),cadence_csv_sha256=sha(out/'cadence.csv'))
    (out/'proof.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
    assert code==0
    return result,columns

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--route',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--limit',type=int,default=2400);p.add_argument('--matched-scene',action='store_true');a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    assert sha(V/'baseline.nes')=='acebfc87a2cae899017f468bb4cedc539787dd510d9b3485caa49f3b6fd4f891'
    baseline,bcols=run(V/'baseline.nes',a.route.resolve(),out/'baseline',a.limit,a.matched_scene)
    candidate,ccols=run(V/'candidate.nes',a.route.resolve(),out/'candidate',a.limit,a.matched_scene)
    key=lambda r:(r['page'],r['column'],r['metatiles'])
    bm={key(r):r for r in bcols};cm={key(r):r for r in ccols}
    common=sorted(bm.keys()&cm.keys())
    rows=[]
    for k in common:
        x,y=bm[k],cm[k]
        rows.append(dict(page=k[0],column=k[1],metatiles=k[2],baseline_cycles=int(x['parserCycles']),candidate_cycles=int(y['parserCycles']),saved=int(x['parserCycles'])-int(y['parserCycles'])))
    (out/'matched-columns.json').write_text(json.dumps(rows,indent=2))
    matched=not a.matched_scene or (baseline['final_native_position']==candidate['final_native_position'] and baseline['completed_game_updates']==candidate['completed_game_updates']==128)
    q=dict(passed=bool(common) and baseline['passed'] and candidate['passed']and matched,goal_complete=False,adopted=False,
           baseline=baseline,candidate=candidate,matched_native_columns=len(rows),
           saved_cycles_per_matched_column=sorted(set(r['saved']for r in rows)),
           fixed_inputs_source_sha256=sha(a.route/'inputs.csv'),
           matched_same_final_position_and_128_updates=matched if a.matched_scene else None,
           scope='Same physical controller stream and cold deterministic startup, actual native13-row column cycles matched by native page/column/13tile buffer. Subtract measured NMI/IRQ body plus7-cycle hardware entry and6-cycle RTI; report inclusive separately. Actual completed GameLoop updates per actual physical frame. Whole-route positions/cadence can diverge with cost, so the frame-count comparison is bounded and does not establish constant60Hz.')
    if a.matched_scene:
        q['scope']='Same actual cold menu and constant ordinary Right+B inputs for exactly128 completed active native GameLoops. Final native position and update count must match. Actual13-row columns matched by page/column/13tile buffer; CPU kernel excludes measured interrupt body,7-cycle hardware entry and6-cycle RTI. Physical-frame cadence reported for that bounded common scene. No constant60Hz or campaign throughput claim.'
        q.pop('fixed_inputs_source_sha256')
    (out/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)

if __name__=='__main__':main()
