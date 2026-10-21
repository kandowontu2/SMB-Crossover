"""Root native inclusive/exclusive Sophia cost and ratio qualification profile.

Seeded arenas. Private ratio B target; shared current Pit correction is untouched.
"""
from pathlib import Path
import csv,difflib,hashlib,importlib.util,json,sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49o2-sophia-ratio-b-profile-e'
PARENT=ROOT/'build/verification/root49o2-sophia-ratio-private-build-b/source/build'
CURRENT=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    assert workspace_bytes(ROOT)+20_000_000<50_000_000_000
    sys.path.insert(0,str(ROOT/'tools'));import run_mesen
    helper=ROOT/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    spec=importlib.util.spec_from_file_location('deep_image',helper)
    image=importlib.util.module_from_spec(spec);spec.loader.exec_module(image)
    current=json.loads((CURRENT/'manifest.json').read_text())['source_hashes']
    assert all(sha(ROOT/n)==h for n,h in current.items())
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    pr=json.loads((parser/'provenance.json').read_text())
    for q in [pr['wheel']]+pr['extracted']:assert sha(Path(q['path']))==q['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    parse=LuaRuntime().eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    OUT.mkdir()
    base=ROOT/'tests/roster-pit-rygar-sophia-performance.lua'
    text=base.read_text()
    old="if PROFILE_DEEP then hook('HomingMotion',6);hook('HomeDamping',6);hook('DampX',6);hook('Blocks',8);hook('Enemies',8)end"
    assert text.count(old)==1
    additions=";hook('DampY',6);hook('SophiaHomingVector',36);hook('AvHomeFriction',6);hook('AvFanFriction',6)"
    deep=text.replace(old,old[:-3]+additions+'end')
    routine_marker="'HomingMotion','HomeDamping','DampX','Blocks','Enemies','NMI'"
    assert deep.count(routine_marker)==1
    deep=deep.replace(routine_marker,"'HomingMotion','HomeDamping','DampX','DampY','SophiaHomingVector','AvHomeFriction','AvFanFriction','Blocks','Enemies','NMI'")
    core=OUT/'performance-deep.lua';core.write_text(deep)
    (OUT/'performance-deep.diff').write_text(''.join(difflib.unified_diff(text.splitlines(True),deep.splitlines(True),fromfile='original-performance',tofile='deep-timing-only')))
    ok,error=parse(deep,str(core));assert ok,error
    cases=[]
    for mapper in ('mmc3','mmc5'):
        im=image.Image(PARENT/f'smb-crossover-{mapper}.nes')
        folder=OUT/mapper;folder.mkdir()
        scopes={n:None for n in ('ExpandedMovement','ExpandedWeapons','ExpandedDrawShots','RemainingWeapons','RemainingDraw','SophiaHomingVector','AvHomeFriction','AvFanFriction')}
        scopes.update({n:'RemainingWeapons' for n in ('HomingMotion','HomeDamping','DampX','DampY')})
        scopes.update({'Blocks':'MegaManWeapons','Enemies':'MegaManWeapons'})
        hooks={n:im.hook(n,scope) for n,scope in scopes.items()}
        hooks.update({'Ratio':im.hook('Ratio','SophiaHomingVector'),'Project':im.hook('Project','SophiaHomingVector')})
        for n,source in [('NMI','NonMaskableInterrupt'),('IRQ','IrqScrollSplit')]:
            hooks[n]=im.hook(source);hooks[n+'End']=im.hook(source,delta='last')
            assert hooks[n+'End']['bytes'][0]==0x40
        s='OUTPUT='+image.lua(folder.as_posix()+'/')+'\nTEST_DIR='+image.lua((ROOT/'tests').as_posix()+'/')+'\nPROFILE_CHARACTER=11\nPROFILE_DEEP=true\n'
        for n,h in hooks.items():
            if n in scopes:s+='L['+image.lua(n)+']='+str(h['address'])+'\n'
        s+='local H='+image.lua(hooks)+'\nlocal A='+image.lua(im.ram)+'\n'
        s+='local IS_MMC5='+image.lua(mapper=='mmc5')+'\n'
        s+='''local regs,sel,mode,depth={},7,0,0
local frame,irqStart,irqCycles=0,0,0
local counts,entry={},nil
local f=assert(io.open(OUTPUT..'ratio.csv','w'))
f:write('phase,frame,cyclesExclusive,R0,R1,R2,R3,R4,fastQualified,afterR0,afterR1,afterR2,afterR3,afterR4\\n')
local function rd(a)return emu.read(a,emu.memType.nesDebug)end
local function r(n)return rd(assert(A[n],n))end
local function cycle()return emu.getState()['cpu.cycleCount']end
local function physical(pc)
 if IS_MMC5 then
  if pc>=0x8000 then return regs[pc&0xe000]or-1 end
  return -1
 end
 if pc>=0xe000 then return 63 elseif pc>=0xc000 then return mode==0 and 62 or(regs[6]or-1)
 elseif pc>=0xa000 then return regs[7]or-1 elseif pc>=0x8000 then return mode==0 and(regs[6]or-1)or 62 end
 return -1
end
'''
        if mapper=='mmc3':
            s+='emu.addMemoryCallback(function(_,v)sel=v&7;mode=(v>>6)&1 end,emu.callbackType.write,0x8000)\n'
            s+='emu.addMemoryCallback(function(_,v)if sel==6 or sel==7 then regs[sel]=v&63 end end,emu.callbackType.write,0x8001)\n'
        else:
            s+='regs[0xe000]=63\n'
            s+='emu.addMemoryCallback(function(_,v)assert(v==3,"Actual MMC5 eight-kilobyte PRG mode")end,emu.callbackType.write,0x5100)\n'
            for port,window in ((0x5114,0x8000),(0x5115,0xa000),(0x5116,0xc000),(0x5117,0xe000)):
                s+=f'emu.addMemoryCallback(function(_,v)regs[{window}]=v&63 end,emu.callbackType.write,{port})\n'
        s+='''for name,h in pairs(H)do
 counts[name]=0
 emu.addMemoryCallback(function()
  if physical(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(rd(h.address+i-1)==v,'Actual mapped eight-byte deep hook '..name)end
  counts[name]=counts[name]+1
  if name=='NMI'or name=='IRQ'then
   if depth==0 then irqStart=cycle()-7 end;depth=depth+1
  elseif name=='NMIEnd'or name=='IRQEnd'then
   depth=depth-1;assert(depth>=0,'Balanced deep profile interrupt nesting')
   if depth==0 then irqCycles=irqCycles+cycle()+6-irqStart end
  elseif depth==0 and frame>=550 and frame<1630 then
   if name=='Ratio'then
    assert(not entry,'Nonrecursive actual ratio');local v={}
    for k=0,4 do v[k+1]=r('R'..k)end
    entry={cycle(),irqCycles,math.floor((frame-550)/180),frame,v}
   elseif name=='Project'and entry then
    local v=entry[5];local row={entry[3],entry[4],cycle()-entry[1]-(irqCycles-entry[2])}
    for _,b in ipairs(v)do row[#row+1]=b end
    row[#row+1]=(v[2]==0 and v[4]==0 and v[5]==0 and v[1]<v[3])and 1 or 0
    for k=0,4 do row[#row+1]=r('R'..k)end
    f:write(table.concat(row,',')..'\\n');f:flush();entry=nil
   end
  end
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
local stop=emu.stop
function emu.stop(code)
 f:close();local o=assert(io.open(OUTPUT..'hook-counts.json','w'))
 local a={};for n,v in pairs(counts)do a[#a+1]='"'..n..'":'..v end
 o:write('{'..table.concat(a,',')..'}');o:close();stop(code)
end
'''
        s+='dofile(TEST_DIR.."menu-bootstrap.lua")\ndofile('+image.lua(core.as_posix())+')\n'
        script=folder/('sophia-ratio-b-e-'+mapper+'.lua');script.write_text(s)
        ok,error=parse(s,str(script));assert ok,error
        code=run_mesen.run(script,im.path,timeout=60,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
        log=ROOT/'build/verification'/f'{im.path.stem}-{script.stem}.log'
        assert code==0,str(log)
        ratio=list(csv.DictReader((folder/'ratio.csv').open()))
        assert ratio and all(int(r['phase'])==4 for r in ratio)
        case={'mapper':mapper,'target':im.metadata(),'hooks':hooks,'actual_counts':json.loads((folder/'hook-counts.json').read_text()),
              'ratio_samples':len(ratio),'fast_qualified':sum(int(r['fastQualified']) for r in ratio),
              'ratio_cycles_average':sum(int(r['cyclesExclusive'])for r in ratio)/len(ratio),
              'ratio_cycles_min':min(int(r['cyclesExclusive'])for r in ratio),'ratio_cycles_max':max(int(r['cyclesExclusive'])for r in ratio),
              'ratio_sha256':sha(folder/'ratio.csv'),'profile_sha256':sha(folder/f'{im.path.stem}-roster-profile-11.csv'),
              'log_sha256':sha(log),'script_sha256':sha(script)}
        assert case['actual_counts']['Ratio']>0 and case['actual_counts']['SophiaHomingVector']>0
        old_profile=ROOT/'build/verification/root49o2-pit-rygar-sophia-performance-b'/f'profile-o2-b-{mapper}-c11'/f'{im.path.stem}-roster-profile-11.csv'
        old_rows=list(csv.DictReader(old_profile.open()))
        new_rows={(r['ability'],r['routine']):r for r in csv.DictReader((folder/f'{im.path.stem}-roster-profile-11.csv').open())}
        controls=[r for r in old_rows if r['ability'] in ('normal-cannon','hyper-cannon','crusher-cannon','missile-triplet')]
        assert len(controls)==24
        assert all(new_rows[(r['ability'],r['routine'])]==r for r in controls),'Inactive-ratio control profiles must remain exact'
        case['inactive_ratio_control_rows_literal']=len(controls)
        case['changed_shallow_rows']=[{'before':r,'after':new_rows[(r['ability'],r['routine'])]} for r in old_rows if new_rows[(r['ability'],r['routine'])]!=r]
        case['original_shallow_profile_sha256']=sha(old_profile)
        cases.append(case)
        (OUT/'progress.json').write_text(json.dumps(cases,indent=2)+'\n')
    assert all(sha(ROOT/n)==h for n,h in current.items())
    report={'status':'PASS_TWO_NATIVE_RATIO_B_PROFILES_SEEDED_ARENAS_ONLY','accepted_release':False,'goal_complete':False,
            'source_fixture_sha256':sha(base),'derived_timing_fixture_sha256':sha(core),
            'script_sha256':sha(Path(__file__)),'cases':cases,'workspace_bytes':workspace_bytes(ROOT),
            'qualification':'Private arithmetic optimization only. Actual guarded ratio duration excludes nested interrupts. Complete-vector and motion durations are inclusive. Hardware-frame pacing changes update counts; this fixture is not an independent trajectory, ordinary playthrough or source-fidelity proof.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json'),'cases':[{k:c[k]for k in ('mapper','ratio_samples','fast_qualified','ratio_cycles_average')}for c in cases]},indent=2))


if __name__=='__main__':main()
