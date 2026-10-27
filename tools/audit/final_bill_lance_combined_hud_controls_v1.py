"""Replay the additive Lua HUD observer on actual combined-ROM draw calls."""
from pathlib import Path
import argparse,json,sys,traceback
from final_bill_lance_combined_prepare_v2 import PARENT,SHA,D,ROOT,sha,put,OWNER_NAMES,EXTRA_OWNERS
from final_bill_lance_hard_gallery_source_v2 import BillArena
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from parodius_visibility_hud_static_startup_v1 import MOCK


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    original=NesMPU.step
    try:
        b=scoped_load(PARENT/'candidate.nes');assert sha(PARENT/'candidate.nes')==SHA
        for n in EXTRA_OWNERS:
            if n not in OWNER_NAMES:OWNER_NAMES.append(n)
        ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==SHA
        sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
        rows=[];finalizers=[]
        for variant in [0,1]:
            profile=ready['profiles'][variant];out=Path(profile['output']);script=(out/'run.lua').read_text();assert sha(out/'run.lua')==profile['script_sha256']
            rt=LuaRuntime(unpack_returned_tuples=True)
            rt.execute(MOCK+"\nL={};OUTPUT='mock/';emu.memType.nesPrgRom=6;emu.write=function()error('Observer never writes actual game state')end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end")
            rt.execute(script+"\nentered=true;done=false;phase='run';wall=500;updates=1;MODEL_HUD=function()return hudHelpers,hudReturns,hudScope~=nil end")
            callbacks=[v for _,v in rt.globals().callbacks.items()]
            assert int(callbacks[-1]['lo'])==0 and int(callbacks[-1]['hi'])==65535
            rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
            for item,case in [(4,2),(5,3),(2,4),(3,5),(1,6),(6,7)]:
                for face in [1,2]:
                    q=BillArena(b,variant)
                    for grant in ([4,1]if item==1 else[4,1,6]if item==6 else[item]):q.grant(grant)
                    q.put(PlayerFacingDir=face,Player_MovingDir=face,AvDrawIndex=20);q.buttons(64)
                    rt.globals().PY_READ=lambda at,kind:q.m[at]if kind==1 else b['raw'][16+at]if kind==6 else 0
                    rt.globals().PY_BANK=lambda at:q.m.banks[(at-32768)//8192]*8192+(at&8191)if at>=32768 else at
                    rt.execute("emu.read=function(a,k)return PY_READ(a,k)end;emu.convertAddress=function(a)return{address=PY_BANK(a)}end")
                    rt.execute(f"index={case};current={{q=C.cases[{case}],stage={{draws=0}}}}")
                    active=False
                    def step(c):
                        if not active:return original(c)
                        state=rt.globals().state
                        for k,v in {'cpu.pc':c.pc,'cpu.sp':c.sp,'cpu.a':c.a,'cpu.x':c.x,'cpu.y':c.y,'cpu.p':c.p,'cpu.ps':c.p,'cpu.cycleCount':c.processorCycles}.items():state[k]=v
                        for cb in callbacks:
                            if int(cb['kind'])==2 and int(cb['lo'])<=c.pc<=int(cb['hi']):cb['fn'](c.pc)
                        before=len(q.m.writes);original(c)
                        for at,value in q.m.writes[before:]:
                            for cb in callbacks:
                                if int(cb['kind'])==1 and int(cb['lo'])<=at<=int(cb['hi']):cb['fn'](at,value)
                    NesMPU.step=step;before=rt.globals().MODEL_HUD();cycles=[]
                    try:
                        for turn in range(4):
                            active=True;c,_=q.invoke('RemainingDraw');active=False;cycles.append(c.processorCycles)
                            assert not rt.globals().MODEL_HUD()[2]
                    finally:active=False;NesMPU.step=original
                    after=rt.globals().MODEL_HUD();assert after[0]>before[0] and after[1]>before[1]
                    rows.append(dict(variant=variant,item=item,face=face,actual_full_draw_calls=4,helper_returns=after[0]-before[0],qualified_HUD_returns=after[1]-before[1],cycles=cycles,scope_cleared=True))
            # Only the first, newly added endFrame observer is invoked here.
            # Original capture/terminal guards are separately unchanged, not
            # counterfeited by this isolated CPU/Lua finalizer model.
            rt.execute("done=true;events[emu.eventType.endFrame][1]()")
            finalizers.append(dict(variant=variant,original_generated_new_finalizer_passed_after_actual_all_six_case_observations=True))
        put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=SHA,cells=len(rows),actual_full_RemainingDraw_calls=4*len(rows),rows=rows,finalizer_models=finalizers,
            actual_compiled_instructions_pointers_OAM_and_helper_return_flags_never_stubbed=True,generated_observer_literal=True,runtime_callback_registration_forbidden=True,
            limits='Actual combined CPU/Lua observer replay, not native selection/controller/physical PPU/APU/DMA/cadence. Only added HUD observer finalizer modeled; original inherited native guards remain for future genuine native runs.'))
        files=[Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua',PARENT/'candidate.nes',PARENT/'candidate.dbg']
        put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in files]))
        print(json.dumps(dict(passed=True,cells=len(rows),actual_compiled_calls=4*len(rows),proof_sha256=sha(a.output/'proof.json'))))
    except Exception as e:
        put(a.output/'failure.json',dict(passed=False,native_run=False,error=str(e),traceback=traceback.format_exc()));raise
    finally:NesMPU.step=original


if __name__=='__main__':main()
