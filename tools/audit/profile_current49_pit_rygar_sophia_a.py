"""Run previously unregistered full-pool performance arenas on frozen O2.

Seeded component measurements, never ordinary route or source-parity proof.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49o2-pit-rygar-sophia-performance-b'
CHECKPOINT=ROOT/'build/checkpoints/roster-audit-v49-provisional-o2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+1_000_000<30_000_000_000
    sys.path.insert(0,str(ROOT/'tools'));import run_mesen
    helper=ROOT/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    spec=importlib.util.spec_from_file_location('profile_image',helper)
    image=importlib.util.module_from_spec(spec);spec.loader.exec_module(image)
    inputs={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [
        Path(__file__),ROOT/'tests/menu-bootstrap.lua',ROOT/'tests/roster-pit-rygar-sophia-performance.lua',
        ROOT/'tools/run_mesen.py',helper]}
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for q in [provenance['wheel']]+provenance['extracted']:
        assert sha(Path(q['path']))==q['sha256'] and Path(q['path']).stat().st_size==q['bytes']
    sys.path.insert(0,str(parser/'runtime'));import lupa.lua54 as native
    vm=native.LuaRuntime(unpack_returned_tuples=True)
    parse=vm.eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    manifest=json.loads((CHECKPOINT/'manifest.json').read_text())
    assert all(sha(ROOT/n)==h for n,h in manifest['source_hashes'].items())
    OUT.mkdir()
    cases=[]
    for mapper in ('mmc3','mmc5'):
        im=image.Image(CHECKPOINT/f'smb-crossover-{mapper}.nes')
        functions=['ExpandedMovement','ExpandedWeapons','ExpandedDrawShots','RemainingWeapons','RemainingDraw']
        guards={n:im.hook(n) for n in functions}
        # Overrides only function labels with scoped compiled globals; no flat-local alias.
        overrides={n:im.sym(n)['val'] for n in functions}
        for c in (6,7,11):
            name=f'profile-o2-b-{mapper}-c{c}'
            folder=OUT/name;folder.mkdir()
            script=folder/(name+'.lua')
            prelude='OUTPUT='+image.lua(folder.as_posix()+'/')+'\n'
            prelude+='TEST_DIR='+image.lua((ROOT/'tests').as_posix()+'/')+'\n'
            prelude+='PROFILE_CHARACTER='+str(c)+'\n'
            for n,v in overrides.items():prelude+='L['+image.lua(n)+']='+str(v)+'\n'
            # Hardware mapping guard supplements the original fixture's timing hooks.
            prelude+='local H='+image.lua(guards)+'\n'
            prelude+='''local regs,sel,mode={},7,0
local function rd(a)return emu.read(a,emu.memType.nesDebug)end
local function phys(pc)
 if pc>=0xe000 then return 63 elseif pc>=0xc000 then return mode==0 and 62 or(regs[6]or-1)
 elseif pc>=0xa000 then return regs[7]or-1 elseif pc>=0x8000 then return mode==0 and(regs[6]or-1)or 62 end
 return -1
end
'''
            if mapper=='mmc3':
                prelude+='emu.addMemoryCallback(function(_,v)sel=v&7;mode=(v>>6)&1 end,emu.callbackType.write,0x8000)\n'
                prelude+='emu.addMemoryCallback(function(_,v)if sel==6 or sel==7 then regs[sel]=v&63 end end,emu.callbackType.write,0x8001)\n'
            else:
                prelude+='emu.addMemoryCallback(function(_,v)regs[6]=v&63 end,emu.callbackType.write,0x5114)\n'
                prelude+='emu.addMemoryCallback(function(_,v)regs[7]=v&63 end,emu.callbackType.write,0x5115)\n'
            prelude+='''local counts={}
for n,h in pairs(H)do
 counts[n]=0
 emu.addMemoryCallback(function()
  if phys(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(rd(h.address+i-1)==v,'Compiled actual-bank profile guard '..n)end
  counts[n]=counts[n]+1
 end,emu.callbackType.exec,h.address)
end
local originalStop=emu.stop
function emu.stop(code)
 local f=assert(io.open(OUTPUT..'actual-hook-counts.json','w'))
 local a={};for n,v in pairs(counts)do a[#a+1]='"'..n..'":'..v end
 f:write('{'..table.concat(a,',')..'}');f:close();originalStop(code)
end
'''
            prelude+='dofile(TEST_DIR.."menu-bootstrap.lua")\n'
            prelude+='dofile(TEST_DIR.."roster-pit-rygar-sophia-performance.lua")\n'
            script.write_text(prelude)
            for check in (script,ROOT/'tests/menu-bootstrap.lua',ROOT/'tests/roster-pit-rygar-sophia-performance.lua'):
                ok,error=parse(check.read_text(),str(check));assert ok,(str(check),error)
            code=run_mesen.run(script,im.path,timeout=45,emulator_options=[
                '--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false',
                '--nes.randomizeMapperPowerOnState=false'])
            log=ROOT/'build/verification'/f'{im.path.stem}-{name}.log'
            case={'character':c,'mapper':mapper,'native_exit':code,'ROM':im.metadata(),
                  'guarded_hooks':guards,'script_sha256':sha(script),'log_sha256':sha(log)}
            if (folder/'actual-hook-counts.json').exists():case['actual_hook_counts']=json.loads((folder/'actual-hook-counts.json').read_text())
            csv=folder/f'{im.path.stem}-roster-profile-{c}.csv'
            if csv.exists():case.update(profile_sha256=sha(csv),profile_bytes=csv.stat().st_size)
            cases.append(case)
            (OUT/'progress.json').write_text(json.dumps(cases,indent=2)+'\n')
            assert code==0,('Retained native profile negative',mapper,c,log)
    assert all(sha(ROOT/n)==h for n,h in inputs.items())
    assert all(sha(ROOT/n)==h for n,h in manifest['source_hashes'].items())
    report={'status':'PASS_SIX_SEEDED_FULL_POOL_PERFORMANCE_ARENAS_ONLY',
            'accepted_release':False,'goal_complete':False,'source409_exact':True,
            'inputs':inputs,'cases':cases,'workspace_after':workspace_bytes(ROOT),
            'qualification':'Original interrupt-exclusive fixture; no source trajectory, ordinary acquisition, route or fidelity proof. Physical guarded entry counts supplement software-bank timing hooks.'}
    assert report['workspace_after']<30_000_000_000
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(OUT/'report.json'),'sha256':sha(OUT/'report.json')},indent=2))


if __name__=='__main__':main()
