"""Prepare one native-boundary ARM/question control; never launch an emulator."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from final_item_abilities_run import lua
from final_item_abilities_current731_prepare_v1 import protocol, dma_mocks
from final_item_abilities_static_prepare_v2 import core_tests, old_core
from parodius_visibility_hud_static_startup_v1 import MOCK
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'root-current-roster-composition-v1'
OLD=D/'current3b112-bass-gallery-ready-v1/profiles/bass-easy/native'
SHA='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(path,value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    assert not a.output.exists() and not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True)
    native=a.output/'native';native.mkdir()
    assert sha(B/'candidate.nes')==SHA
    b=scoped_load(B/'candidate.nes')
    source=json.loads((B/'source-manifest.json').read_text())
    for rel,h in source.items():assert sha(B/'source'/rel)==h,rel
    original=(OLD/'run.lua').read_text()
    old_cfg=json.loads((OLD/'config.json').read_text())
    header='FINAL_ITEM_PROGRESSIVE='+lua(old_cfg)+'\n'
    assert original.startswith(header)
    body=original[len(header):]
    begin=body.index('-- Controlled B-only gallery.')
    end=body.index('\nlocal saved=nil',begin)
    prefix,tail=body[:begin],body[end:]
    mechanics=R/'tools/audit/bass_arm_question_boundary_v1.lua'
    module=mechanics.read_text()
    # This is a separate one-case fixture, not a claimed passing rerun of
    # the old sixteen-case gallery. All inherited hardware guard code stays.
    assert tail.count("assert(wall<22000,'Bounded controlled Bass gallery '")==1
    tail=tail.replace("assert(wall<22000,'Bounded controlled Bass gallery '","assert(wall<1800,'Bounded ARM question control '")
    cfg=json.loads(json.dumps(old_cfg))
    cfg['cases']=[dict(name='arm-question-face1',lane='B initialized resources/arena',acquisition=False)]
    cfg.update(hard=False,mode_value=0,ROM_sha256=SHA)
    for name in ['MegaManSuperArmThrow','MegaManWeapons::Blocks','PlayerHeadCollision','InventoryPreparePickup']:
        off=location(b,name)
        cfg['hooks'][name]=dict(address=address(b,name),physical_bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]))
    for name,h in cfg['hooks'].items():
        owner='GameLoop' if name=='finish' else 'NonMaskableInterrupt' if name=='NmiReturn' else name
        off=location(b,owner)
        if name in ['finish','NmiReturn']:off+=int(b['syms'][owner]['size'],0)-1
        expected=dict(address=address(b,owner)+(int(b['syms'][owner]['size'],0)-1 if name in ['finish','NmiReturn'] else 0),physical_bank=(off-16)//8192,bytes=list(b['raw'][off:off+len(h['bytes'])]))
        assert h==expected,(name,h,expected)
    for name in re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",module):
        if name in b['syms']:cfg['ram'][name]=address(b,name)
    assert cfg['dma_protocol']==protocol(b)
    script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+prefix+module+tail
    direct=set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",script))
    assert not direct-set(cfg['ram']),direct-set(cfg['ram'])
    assert "w('InvSelected'" not in module and "w('CrossoverBehaviorVersion'" not in module
    assert not re.search(r'\b(?:removeMemoryCallback|removeEventCallback)\b',script)
    (native/'run.lua').write_text(script)
    put(native/'config.json',cfg)
    sys.path.insert(0,str(D/'final-tmnt-items-v1/lua-parser-deps-v1'))
    from luaparser import ast
    ast.parse(script)
    sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    rt=LuaRuntime(unpack_returned_tuples=True)
    rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.write=function()error("Unexpected startup write")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end')
    rt.execute(script)
    count=rt.eval('#callbacks')
    assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==0xffff')
    rt.execute('emu.addMemoryCallback=function()error("Runtime callback registration")end;emu.removeMemoryCallback=function()error("Runtime callback removal")end')
    for frame in [1,2,3]:
        rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
    assert rt.eval('#callbacks')==count
    returns=core_tests(LuaRuntime,old_core((R/'tools/audit/final_item_abilities_native.lua').read_text()),(R/'tools/audit/final_item_abilities_static_return_v1.lua').read_text())
    dma=dma_mocks(LuaRuntime,(R/'tools/audit/final_item_abilities_dma731_v1.lua').read_text(),dict(dma_protocol=cfg['dma_protocol']))
    # The new throw observer is exercised through the actual generated
    # callback and qualified Lua-only return dispatcher. A wrong cost must
    # fail; these synthetic outcomes are not native evidence.
    observed=[]
    for after_stock,should_pass in [(104,True),(105,False)]:
        mock=MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;MEM={};MAP={};emu.read=function(a)return MEM[a]or 0 end;emu.write=function(a,v)MEM[a]=v end;emu.convertAddress=function(a)return{address=(MAP[a]or 0)*8192+a%8192}end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end'
        test='''
entered=true;phase='exercise';updates=80
local function set(n,v,i)MEM[L[n]+(i or 0)]=v end
set('InvAmmo',112,145);set('SsHeld',10)
local h=C.hooks.MegaManSuperArmThrow
for i,v in ipairs(h.bytes)do MEM[h.address+i-1]=v end
MAP[h.address]=h.physical_bank;state['cpu.pc']=h.address;state['cpu.sp']=240
local ret=0x9200;MEM[0x1f1]=0xff;MEM[0x1f2]=0x91;MAP[ret]=4
local before=#callbacks
for _,q in ipairs(callbacks)do if q.kind==2 and q.lo==h.address and q.hi==h.address then q.fn(h.address)end end
assert(#callbacks==before,'Return registration remains Lua-only')
set('InvAmmo',AFTER_STOCK,145);set('SsHeld',0);set('RgShotType',9,9);set('SsMode',0,9)
set('RgShotVXLo',0x55,9);set('RgShotVXHi',2,9);set('RgShotVYLo',0x55,9);set('RgShotVYHi',0xfd,9)
state['cpu.pc']=ret;state['cpu.sp']=242
callbacks[#callbacks].fn(ret)
assert(record.throws==1,'Actual synthetic return observed once')
'''.replace('AFTER_STOCK',str(after_stock))
        rr=LuaRuntime(unpack_returned_tuples=True)
        rr.execute(mock+'\n'+script)
        rr.execute('emu.addMemoryCallback=function()error("Runtime callback mutation")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
        ok,error=rr.eval('function()local ok,e=pcall(function()'+test+' end);return ok,tostring(e)end')()
        assert bool(ok)==should_pass,(after_stock,error)
        observed.append(dict(name='throw_cost_'+str(after_stock),expected_accept=should_pass,mock_control_passed=True,error=None if should_pass else error))
    put(a.output/'source-controls.json',dict(passed=True,native_run=False,Lua='5.4',script_parsed=True,static_callbacks=count,dispatcher_last=True,no_runtime_registration=True,inactive_mock_frames=3,all_direct_RAM_reads_writes_bound=True,return_controls=returns,DMA_controls=dma,new_throw_callback_controls=observed,limits='Synthetic parser/startup/return/rejection controls only. Real lift/head/creation/rise/continued GameLoop are unrun. The source11-call ARM question transaction is separately scoped.'))
    env=json.loads((D/'current3b112-bass-gallery-ready-v1/environment.json').read_text())
    emulator=Path(env['emulator']);worker=emulator.parent/'settings.json';user=Path('C:/Mesen2/settings.json')
    assert sha(emulator)==env['emulator_sha256'] and sha(emulator.parent/'MesenCore.dll')==env['core_sha256']
    assert sha(worker)==env['worker_settings_sha256'] and sha(user)==env['user_context_sha256']
    command=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(native),'--emulator',str(emulator),str(native/'run.lua'),str(B/'candidate.nes'),'--timeout','600']+['--option='+x for x in env['actual_command_overrides']]
    put(a.output/'command.json',command)
    plan='''ONE prepared BassEasy right-facing ARM versus nativeC1 mushroom/flower question cell. No grant or launch. Initial poweredtier1/ARM ownership3/ammo112 and complete logical+visible arena are declared B-only seeds at actual GameLoop boundary; selection is realcontrollerSelect, then native heldB lifts masonry and freshB throws. No rawselection/mode/RNG/HP/contact/reward/fragment/result writes. The powered character's C1 reward is adaptively a native inventory upgrade, not a falsely asserted literal mushroom. Observe native PlayerHeadCollision at exact64/144, player-field restoration, native InventoryPreparePickup/actor creation/fullrise, four independent fragments, adjacentbrick preservation and250continued GameLoop updates. Original full E008/all256disabledOAM/CHR/IRQ31/5SMC/bank/stack/APU/PPU guards remain unchanged. One case only, no everymode/page/lowstock/missingmusic/acquisition/campaign claim. Legacy endFrame-seeded tests are references, not retagged current results. Stopfirstfailure/no retry; later launch requires separateROOTgrant and one worker slot.'''
    (a.output/'PLAN.txt').write_text(plan+'\n')
    deps={Path(__file__),mechanics,OLD/'run.lua',OLD/'config.json',B/'candidate.nes',B/'candidate.dbg',B/'candidate.lbl',B/'candidate.map',B/'source-manifest.json',B/'ROOT-source-readiness.json',B/'ROOT-bindings.json',D/'bass-arm-question-boundary-v1/source-control-v1/proof.json',R/'tools/audit/bass_arm_question_boundary_source_v1.py',R/'tools/audit/final_item_abilities_static_return_v1.lua',R/'tools/audit/final_item_abilities_dma731_v1.lua',R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py',Path(sys.executable),emulator,emulator.parent/'MesenCore.dll',worker,user}
    deps|={B/'source'/rel for rel in source}
    deps|={p for p in a.output.rglob('*')if p.is_file()}
    put(a.output/'bindings.json',{str(p.resolve()):sha(p)for p in sorted(deps)})
    proof=dict(prepared=True,source_only=True,native_run=False,native_grant=False,ROM_sha256=SHA,mode_numeric=0,cases=1,maximum_launches=1,maximum_workers=1,wall_frame_bound=1800,source_controls_sha256=sha(a.output/'source-controls.json'),bindings=len(deps),bindings_sha256=sha(a.output/'bindings.json'),script_sha256=sha(native/'run.lua'),unchanged_hardware_guard_prefix=True,unchanged_hardware_guard_tail_except_stricter_wall_bound=True,command=command,limitations=plan,preparer_sha256=sha(__file__))
    put(a.output/'readiness.json',proof)
    print(json.dumps({k:v for k,v in proof.items()if k not in ['command','limitations']},indent=2))


if __name__=='__main__':
    main()
