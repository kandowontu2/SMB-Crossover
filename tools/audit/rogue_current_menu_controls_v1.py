"""Check current roster menu and genuine Rogue callers after backend composition."""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import sys
import traceback

R=Path(__file__).resolve().parents[2]
O=R/'build/rogue-current-menu-v5'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
import rogue_dawn_victory_pose_controls_v1 as victory


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not(O/'controls.json').exists()
    build=json.loads((O/'build-proof.json').read_text())
    assert sha(O/'candidate.nes')==build['ROM_sha256']
    for p,h in build['source_bindings'].items():assert sha(p)==h,p
    # The exploratory builder used KmBodyDraw as a sentinel, but that symbol
    # does not exist even in the authentic installed Kamikaze implementation.
    # Verify real consumed entrypoints against that exact reference instead.
    assert build['existing_backend_parity_unproven']==['KmBodyDraw']
    frozen=R/'build/full-menu-source-controls-v2/check.py'
    source=frozen.read_text()
    original='''    return ((slot == 0 and variant == 2)
            or (slot in (2,7,11) and variant == 1)'''
    replacement='''    return ((slot == 0 and variant == 2)
            or (slot in (7,11) and variant == 1)'''
    assert source.count(original)==1
    source=source.replace(original,replacement)
    assert source.count('pending_indices == set(range(33))')==1
    source=source.replace('pending_indices == set(range(33))','pending_indices == set(range(33))-{1}')
    source=source.replace('len(ready_reselects) == 47','len(ready_reselects) == 48')
    adapter=O/'menu-controls-adapter.py';adapter.write_text(source,newline='\n')
    spec=importlib.util.spec_from_file_location('rogue_current_menu_adapter',adapter)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.ROOT=R;m.NEW=O/'candidate.nes';m.NEW_SHA=sha(m.NEW);m.OUT=O
    report=dict(passed=False,source_CPU_only=True,native_run=False,ROM_sha256=sha(m.NEW),checks={})
    try:
        old=scoped_load(R/'build/rogue-dawn-victory-pose-v4/candidate.nes')
        b=scoped_load(m.NEW)
        current=scoped_load(R/'build/full-roster-menu-v5/candidate.nes')
        required=['GbPitPose','GbPitMenuNavigate','GbPitQueueName','KmGraphics','KmPortrait','KmNmiSlot0']
        assert 'KmBodyDraw'not in current['syms']
        for name in required:assert name in current['syms']and name in b['syms'],name
        report['checks']['actual_existing_backend_entrypoints']=dict(passed=True,names=required,
            corrected_invalid_builder_sentinel='KmBodyDraw is absent in the original implementation; real renderer is KmGraphics/KmPortrait.')
        rows,restores=m.source_cases(b)
        assert len(rows)==80 and len(restores)==48
        report['checks']['all80profiles_pending_gates_preview_and_48ready_CHR_restores']=dict(
            passed=True,profiles=rows,ready_reselects=restores)
        report['checks']['actual1024byte_menu_RLE_and_variant_reset']=dict(passed=True,result=m.rle_case(b))
        report['checks']['six_A_C_CHR_restore_contexts']=dict(passed=True,cases=m.prepare_map_cases(b))
        vrows=[]
        for engine,frame,face,alt in itertools.product([4,5,8],[8,16,20,26],[0,1],[0,1]):
            pair=[]
            for bundle in [old,b]:
                mem,cpu,trace,output=victory.graphics(bundle,engine,frame,face,alt)
                pair.append((output,(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp),victory.state(mem)))
            assert pair[0]==pair[1],('Rogue body graphics',engine,frame,face,alt,pair)
            vrows.append(dict(engine=engine,frame=frame,facing=face,alternate_palette=alt))
        assert len(vrows)==48
        report['checks']['48genuine_Rogue_body_graphics_ABI_and_state_pairs']=dict(passed=True,cases=vrows)
        q=victory.q;get=victory.get;put=victory.put;base=victory.base
        callers=[]
        for mode,center,flags in itertools.product([0,1],[343,344,599,600],[0x30,0x31,0x70,0x71,0x34,0xf3]):
            pairs=[]
            for bundle in [old,b]:
                mem=base.fixture(bundle,center=center,mode=mode)
                put(mem,SavedJoypadBits=0,RdGravity=0,Player_X_Speed=0)
                cpu,trace=q.invoke(mem,'PlayerCtrlRoutine',a=54,x=13,y=87,p=flags)
                assert get(mem,'GameEngineSubroutine')==4
                assert sum(pc==address(bundle,'RdBoxOrExit')and bank==95 for pc,bank,sp in trace['trace'])==2
                assert any(pc==address(bundle,'FlagpoleCollision')for pc,bank,sp in trace['trace'])
                pairs.append((base.registers(cpu),base.application(mem),q.physical(mem)))
            assert pairs[0]==pairs[1],('actual Rogue flagpole caller',mode,center,flags)
            callers.append(dict(mode=mode,center=center,input_flags=flags))
        report['checks']['48actual_Rogue_PlayerCtrl_flagpole_callers']=dict(passed=True,cases=callers)
        report.update(passed=True,ready=48,pending=32,
            limits=['Finite linkedCPU menu/graphics/caller checks only; actual native PPU/NMI/audio/routes still required.',
                    'No every-character1-1 or all-upgrade claim; four-host/Quick/Arthur branches not included.'])
    except Exception as e:
        report.update(error=repr(e),traceback=traceback.format_exc())
        i=1
        while(O/f'controls-negative-{i}.json').exists():i+=1
        (O/f'controls-negative-{i}.json').write_text(json.dumps(report,indent=2)+'\n')
        raise
    dependencies=[Path(__file__).resolve(),frozen,adapter,O/'build-proof.json',O/'candidate.nes',
        O/'candidate.dbg',R/'tools/rogue_dawn_victory_pose_controls_v1.py',
        R/'tools/rogue_dawn_flagpole_controls_v1.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',
        R/'tools/audit/check_tmnt_render_oa.py']
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            p=Path(name).resolve()
            if p.is_file()and p.suffix=='.py'and p.is_relative_to(R):dependencies.append(p)
    report['source_bindings']={str(p):sha(p)for p in dependencies}
    (O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,ROM_sha256=report['ROM_sha256'],ready=48,pending=32)))


if __name__=='__main__':main()
