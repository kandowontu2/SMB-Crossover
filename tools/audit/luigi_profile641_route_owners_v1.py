"""Source-only observer owner/rejection controls using exact generated641 module."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from mario_powerups_current3cee_static_v2 import runtime,symbols
from observe_chip_committed_write import lua
from check_tmnt_render_oa import load


def controls(LuaRuntime,packet,rom):
    b=load(rom);labels,banks=symbols(b,rom);cfg=json.loads((packet/'discovery/configuration.json').read_text())
    cases=[]
    def check(name,body,accept):
        rt=runtime(LuaRuntime,labels,banks)
        rt.execute('ROSTER_CONFIG='+lua(cfg['roster'])+';LUIGI_ROUTE_OBSERVER='+lua(cfg['observation']))
        rt.execute('''
mapBank=127
emu.convertAddress=function(a)return{address=mapBank*8192+a%8192}end
state['cpu.a']=167;state['cpu.x']=0;state['cpu.y']=19;state['cpu.sp']=250
function call(n)
 local h=LUIGI_ROUTE_OBSERVER.hooks[n];mapBank=h.bank;state['cpu.pc']=h.pc
 for i,v in ipairs(h.bytes)do mem[h.pc+i-1]=v end
 dispatch(emu.callbackType.exec,h.pc)
end
''')
        rt.execute((packet/'observer.lua').read_text())
        count=rt.eval('#callbacks')
        rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
        ok,e=rt.eval('function()local ok,e=pcall(function()'+body+' end);return ok,tostring(e)end')()
        assert bool(ok)==accept,(name,e)
        assert rt.eval('#callbacks')==count
        cases.append(dict(name=name,passed=True,expected_guard='accept'if accept else'reject',error=None if accept else e,startup_callbacks=count,runtime_registration_removal=0))
    check('NMI_exact_AXY_SP_fiveSMC_shadow',"call('NmiEntry');call('NmiReturn')",True)
    check('NMI_wrong_AXY',"call('NmiEntry');state['cpu.a']=1;call('NmiReturn')",False)
    check('NMI_wrong_SP',"call('NmiEntry');state['cpu.sp']=249;call('NmiReturn')",False)
    check('NMI_wrong_live_SMC',"call('NmiEntry');mem[LUIGI_ROUTE_OBSERVER.smc[1]]=1;call('NmiReturn')",False)
    check('NMI_wrong_bank_shadow',"call('NmiEntry');mem[L.CurrentBank]=129;call('NmiReturn')",False)
    check('IRQ_exact_AXY_SP_fiveSMC_shadow',"call('IrqEntry');call('IrqReturn')",True)
    active="mem[L.OperMode]=1;mem[L.OperMode_Task]=3;mem[L.GameEngineSubroutine]=8;mem[L.SelectedCharacter]=8;mem[L.MarioVariant]=1;mem[L.CrossoverBehaviorVersion]=0;"
    check('IRQ31_actual_visible_scope',active+"mem[L.Sprite0HitDetectFlag]=1;state['ppu.scanline']=31;call('IrqEntry');call('IrqReturn')",True)
    check('IRQ_wrong_visible_scanline',active+"mem[L.Sprite0HitDetectFlag]=1;state['ppu.scanline']=32;call('IrqEntry')",False)
    stomp=active+"mem[L.Enemy_ID]=6;mem[L.Enemy_Flag]=1;mem[L.Enemy_State]=0;mem[L.Player_Y_Speed]=2;mem[507]=255;mem[508]=90;call('EnemyStomped');"
    finish="mapBank=LUIGI_ROUTE_OBSERVER.hooks.EnemyStomped.bank;state['cpu.sp']=252;mem[L.Player_Y_Speed]=252;mem[L.FloateyNum_Control]=1;mem[L.FloateyNum_Timer]=48;dispatch(2,23296);"
    check('actual_stomp_return_score_and_bounce',stomp+finish,True)
    check('stomp_wrong_return_bank_ignored_then_genuine',stomp+"state['cpu.sp']=252;mapBank=1;dispatch(2,23296);"+finish,True)
    check('stomp_wrong_return_stack_ignored_then_genuine',stomp+"state['cpu.sp']=251;dispatch(2,23296);"+finish,True)
    check('stomp_no_bounce_rejected',stomp+finish.replace('mem[L.Player_Y_Speed]=252','mem[L.Player_Y_Speed]=0'),False)
    check('stomp_no_score_rejected',stomp+finish.replace('mem[L.FloateyNum_Control]=1','mem[L.FloateyNum_Control]=0'),False)
    check('stomp_wrong_selected_identity',stomp.replace('mem[L.SelectedCharacter]=8','mem[L.SelectedCharacter]=0'),False)
    return dict(passed=True,native_executed=False,cases=cases,source_module_sha256=hashlib.sha256((packet/'observer.lua').read_bytes()).hexdigest(),
                scope='Fourteen deterministic synthetic observer events/rejection controls. Genuine compiled hook metadata and guarded PC/SP/physical return-bank contracts, not actual native stomp/NMI/IRQ execution or timing.')
