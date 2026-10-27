"""Actual ce635 callers through literal old/new generated Lua; no native run."""
from pathlib import Path
import argparse,json,sys,traceback
from final_bill_lance_combined_prepare_v3 import D,ROOT,PARENT,SHA,sha,put
from final_bill_lance_combined_prepare_v2 import OWNER_NAMES,EXTRA_OWNERS
from final_bill_lance_hard_gallery_source_v2 import BillArena
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from parodius_visibility_hud_static_startup_v1 import MOCK


class Replay:
    def __init__(self,b,script,variant=0):
        from lupa.lua54 import LuaRuntime
        self.b=b;self.rt=LuaRuntime(unpack_returned_tuples=True);self.q=BillArena(b,variant)
        self.rt.execute(MOCK+"\nL={};OUTPUT='mock/';emu.memType.nesPrgRom=6;emu.write=function()error('Observer never writes game state')end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end")
        self.rt.execute(script+"\nentered=true;done=false;phase='grant-drain';wall=500;updates=1;index=2;current={q=C.cases[2],stage={draws=0}};MODEL_HUD=function()return hudHelpers,hudReturns,hudScope~=nil,hudPending~=nil,hudForeign end")
        self.callbacks=[v for _,v in self.rt.globals().callbacks.items()]
        assert int(self.callbacks[-1]['lo'])==0 and int(self.callbacks[-1]['hi'])==65535
        self.rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
        self.rt.globals().PY_READ=lambda at,kind:self.q.m[at]if kind==1 else b['raw'][16+at]if kind==6 else 0
        self.rt.globals().PY_BANK=lambda at:self.q.m.banks[(at-32768)//8192]*8192+(at&8191)if at>=32768 else at
        self.rt.execute('emu.read=function(a,k)return PY_READ(a,k)end;emu.convertAddress=function(a)return{address=PY_BANK(a)}end')
        self.observed=[];self.active=False

    def counts(self):return tuple(self.rt.globals().MODEL_HUD())

    def invoke(self,name,x=0,y=0,a=0,stop=None):
        original=NesMPU.step;self.active=True;q=self.q;rt=self.rt
        watched={address(self.b,n):n for n in ['BillHudAnchor','RemainingDraw::ArtPointer','MetaspriteRenderLoop']}
        def step(c):
            state=rt.globals().state
            for k,v in {'cpu.pc':c.pc,'cpu.sp':c.sp,'cpu.a':c.a,'cpu.x':c.x,'cpu.y':c.y,'cpu.p':c.p,'cpu.ps':c.p,'cpu.cycleCount':c.processorCycles}.items():state[k]=v
            physical=q.m.banks[(c.pc-32768)//8192]if c.pc>=32768 else -1
            if c.pc in watched:
                ret=(q.m[256+((c.sp+1)&255)]+256*q.m[256+((c.sp+2)&255)]+1)&65535
                self.observed.append(dict(owner=watched[c.pc],pc=c.pc,bank=physical,sp=c.sp,return_pc=ret,
                    source_stack=[q.m[256+((c.sp+i)&255)]for i in range(1,6)],
                    R=[q.get('R'+str(i))for i in range(8)],AvDrawIndex=q.get('AvDrawIndex'),art=q.get('AvDrawArt')))
            for cb in self.callbacks:
                if int(cb['kind'])==2 and int(cb['lo'])<=c.pc<=int(cb['hi']):cb['fn'](c.pc)
            if stop and stop(c,physical):raise StopAtBoundary()
            before=len(q.m.writes);original(c)
            for at,value in q.m.writes[before:]:
                for cb in self.callbacks:
                    if int(cb['kind'])==1 and int(cb['lo'])<=at<=int(cb['hi']):cb['fn'](at,value)
        NesMPU.step=step
        try:return q.invoke(name,a=a,x=x,y=y)
        finally:self.active=False;NesMPU.step=original


class StopAtBoundary(Exception):pass


def foreign(q,b,kind):
    q.put(AvDrawIndex=20,CurrentOAMOffset=0,GuestOamRotationActive=0)
    if kind=='player-body':return 'DrawMetasprite',dict(x=q.get('ObjectMetasprite'),y=0)
    if kind=='enemy':
        q.set('Enemy_ID',6,0);q.set('Enemy_Flag',1,0)
        for n,v in [('SprObject_X_Position',176),('SprObject_PageLoc',0),('SprObject_Y_Position',176),('SprObject_Y_HighPos',1),('PlayerFacingDir',1)]:q.set(n,v,1)
        return 'DrawMetasprite',dict(x=address(b,'METASPRITE_GOOMBA_WALKING_1'),y=1)
    if kind=='legacy-projectile':q.buttons(64);return 'RosterDrawShots',{}
    if kind=='floatey-number':
        q.set('FloateyNum_Control',1,0);q.set('FloateyNum_X_Pos',143,0);q.set('FloateyNum_Y_Pos',160,0)
        return 'FloateyNumberRender',dict(x=0)
    if kind=='brick-debris':
        q.set('Block_State',2,0);q.set('Block_X_Position',144,0);q.set('Block_Y_Position',144,0)
        return 'DrawBrickDebris',{}
    raise AssertionError(kind)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    try:
        b=scoped_load(PARENT/'candidate.nes');assert sha(PARENT/'candidate.nes')==SHA
        for n in EXTRA_OWNERS+['BillHudAnchor','RemainingDraw::ArtPointer','MetaspriteRenderLoop','DrawMetasprite','RosterDrawShots','DrawBrickDebris','FloateyNumberRender']:
            if n not in OWNER_NAMES:OWNER_NAMES.append(n)
        oldroot=D/'final-bill-lance-combined-ce635-ready-v2';kinds=['player-body','enemy','legacy-projectile','floatey-number','brick-debris']
        oldfail=[];newpass=[];abi=[];rejects=[];boundary=[]
        for variant in [0,1]:
            name=('bill'if variant==0 else'lance')+'-hard'
            oldscript=(oldroot/'profiles'/name/'native/run.lua').read_text();newscript=(a.ready/'profiles'/name/'native/run.lua').read_text()
            for kind in kinds:
                for script,oldflag in [(oldscript,True),(newscript,False)]:
                    r=Replay(b,script,variant);r.q.grant(4);r.invoke('RemainingDraw')
                    initial=r.counts();assert initial[:2]==(1,1) and not initial[2] and not initial[3]
                    gateway,kwargs=foreign(r.q,b,kind);start=len(r.observed)
                    try:r.invoke(gateway,**kwargs)
                    except Exception as e:
                        assert oldflag and 'Only Bill/Lance capsule moved to the new screen anchor'in str(e),(kind,oldflag,str(e))
                        oldfail.append(dict(variant=variant,kind=kind,gateway=gateway,error=str(e).split('\n')[0],
                            actual_foreign_render=r.observed[start:],stale_index20_explicit_CPU_arrangement=True))
                    else:
                        assert not oldflag,(kind,'Old false admission must reproduce')
                        after=r.counts();assert after[:2]==initial[:2] and not after[2] and not after[3]
                        renders=[v for v in r.observed[start:]if v['owner']=='MetaspriteRenderLoop'];assert renders,kind
                        assert all(v['AvDrawIndex']==20 for v in renders)
                        newpass.append(dict(variant=variant,kind=kind,gateway=gateway,actual_foreign_render=renders,
                            unchanged_HUD_counts=True,scope_and_pending_cleared=True,actual_8bit_OAM_stores=sum(0x200<=at<0x300 for at,v in r.q.m.writes)))
            # Source CHR admission rejects a real HUD pointer on a different active
            # family. No pointer/carry stub or fake art is supplied.
            r=Replay(b,newscript,variant);r.q.grant(4);r.q.put(SsChrActive=1,SsChrPhysical=0)
            r.invoke('RemainingDraw');counts=r.counts();assert counts[:2]==(1,0) and not counts[2]and not counts[3]
            rejects.append(dict(variant=variant,genuine_ArtPointer_CHR_reject=True,helper_returns=counts[0],HUD_render_returns=counts[1],pending_cleared=True))
            # Stop only after the real helper AND successful real ArtPointer have
            # executed, then execute each genuine foreign caller on its own stack.
            # This is an adversarial CPU/Lua ownership model, not a possible native
            # interrupt/gameplay ordering or a new native outcome claim.
            for kind in kinds:
                r=Replay(b,newscript,variant);r.q.grant(4)
                cfg=json.loads((a.ready/'profiles'/name/'native/config.json').read_text())
                try:r.invoke('RemainingDraw',stop=lambda c,p:c.pc==cfg['hud_call_chain']['pointer_after'] and p==61)
                except StopAtBoundary:pass
                else:raise AssertionError('Actual successful pointer return boundary not reached')
                counts=r.counts();assert counts[:2]==(1,0) and counts[3] and not counts[2]
                gateway,kwargs=foreign(r.q,b,kind);start=len(r.observed);r.invoke(gateway,**kwargs)
                after=r.counts();assert after[:2]==(1,0) and not after[2]and not after[3]
                assert any(v['owner']=='MetaspriteRenderLoop'for v in r.observed[start:])
                boundary.append(dict(variant=variant,foreign=kind,pending_from_actual_successful_pointer=True,
                    genuine_foreign_caller_stack_rejected=True,cleanup_return_executed=True))
            r=Replay(b,newscript,variant);r.q.grant(4);r.invoke('RemainingDraw')
            abi.append(dict(variant=variant,actual_chain=r.observed,counts=r.counts()))
        put(a.output/'reproduced-old-false.json',dict(reproduced=True,native_run=False,cases=oldfail,
            native_failure_caller_was_not_recorded=True,scope='Actual compiled foreign callers with explicit stale20 arrangement. Reproduces the invalid v1 admission; does not identify the uncaptured native caller.'))
        put(a.output/'actual-source-chain.json',dict(passed=True,native_run=False,ROM_sha256=SHA,rows=abi,
            source_chain='helper $BFAE/bank61 return $B8EF; ArtPointer $B997/bank61 return $B907; renderer $A5BA/bank4, source-SP minus3/helper-SP minus3, stacked $016E / saved189 / outer $B922; real renderer return observed before future render.'))
        # Existing v1 strict coordinate/source/OAM assertion texts remain literal.
        before=(ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua').read_text()
        after=(ROOT/'tools/audit/final_bill_lance_combined_hud_v2.lua').read_text()
        guards=['Only Bill/Lance capsule moved to the new screen anchor','Actual source capsule pointer and physical C bank',
            'Actual three-sprite Bill capsule emits twelve OAM stores','Each actual capsule OAM field written once',
            'Native capsule OAM coordinates avoid WORLD/TIME','Actual native capsule tile/attributes/coordinates match complete compiled art']
        assert all(s in before and s in after for s in guards)
        proof=dict(passed=True,source_only=True,native_run=False,ROM_sha256=SHA,
            reproduced_original_generated_v1_FALSE_cases=len(oldfail),corrected_actual_foreign_caller_cases=len(newpass),
            successful_pointer_then_foreign_stack_cleanup_cases=len(boundary),genuine_source_CHR_rejection_cases=len(rejects),
            foreign_rows=newpass,adversarial_boundary_rows=boundary,genuine_rejection_rows=rejects,
            unchanged_strict_capsule_assertion_messages=guards,no_game_source_bytes_changed=True,
            source_pointers_carry_and_render_functions_not_stubbed=True,startup_static_registration_only=True,
            limits='Deterministic complete generated Lua on actual assembled CPU callers. No native execution/PPU/DMA/APU/cadence. Failure-time native R4/R6/return-stack were unavailable; this model is not a reconstruction of those unrecorded fields.')
        put(a.output/'proof.json',proof)
        files={Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',PARENT/'candidate.nes',PARENT/'candidate.dbg',
            ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua',ROOT/'tools/audit/final_bill_lance_combined_hud_v2.lua',
            ROOT/'tools/audit/final_bill_lance_combined_prepare_v3.py',a.output/'proof.json',a.output/'reproduced-old-false.json',a.output/'actual-source-chain.json'}
        for n in ['bill-hard','lance-hard']:
            files.update([a.ready/'profiles'/n/'native/run.lua',a.ready/'profiles'/n/'native/config.json',oldroot/'profiles'/n/'native/run.lua'])
        put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
        print(json.dumps(dict(passed=True,old_FALSEs=len(oldfail),foreign_pass=len(newpass),pending_foreign_cleanup=len(boundary),source_rejections=len(rejects),proof_sha256=sha(a.output/'proof.json'))))
    except Exception as e:
        put(a.output/'failure.json',dict(passed=False,native_run=False,error=str(e),traceback=traceback.format_exc()));raise


if __name__=='__main__':main()
