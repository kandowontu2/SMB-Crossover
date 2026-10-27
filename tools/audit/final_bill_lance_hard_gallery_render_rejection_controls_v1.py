"""Source-only false-type observation injection; compiled draws stay unchanged."""
from pathlib import Path
import argparse,ast,json,sys
from final_bill_lance_hard_gallery_source_v1 import ROOT,sha,put


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    path=ROOT/'tools/audit/final_bill_lance_hard_gallery_render_controls_v1.py'
    source=path.read_text();changes=[]
    def replace(before,after):
        nonlocal source
        assert source.count(before)==1,before
        source=source.replace(before,after);changes.append(dict(before=before,after=after))
    replace("     rt.globals().PY_READ=lambda at,kind:q.m[at] if kind==1 else b['raw'][16+at]if kind==6 else 0",
'''     def observed_read(at,kind):
      # Only the Lua observer sees the deliberately wrong live type exactly
      # at its render-entry check. Real NesMPU and ROM/RAM are unchanged.
      if kind==1 and cpu is not None and cpu.pc==address(b,'MetaspriteRenderLoop') and at==address(b,'RgShotType')+q.get('AvSlot'):return 0
      return q.m[at]if kind==1 else b['raw'][16+at]if kind==6 else 0
     rt.globals().PY_READ=observed_read''')
    replace("     assert total==len(actualshots)>0 and rejected and nonshots,(variant,item,face,mixed,total,len(actualshots),len(rejected),len(nonshots))",
            "     assert total==0 and len(actualshots)>0 and rejected and nonshots,(variant,item,face,mixed,total,len(actualshots),len(rejected),len(nonshots))")
    replace("observer_replayed_literal=True,legacy_stale_RgSlot_produced_by_complete_RosterDrawShots=True,",
            "observer_replayed_literal=True,synthetic_false_type_at_observer_read_only=True,compiled_ROM_RAM_pointer_carry_and_execution_unchanged=True,legacy_stale_RgSlot_produced_by_complete_RosterDrawShots=True,")
    replace("every_accepted_advanced_entry_counted=True,real_nonshot_and_CHR_rejection_not_counted=True,",
            "all_counterfactual_false_type_observations_rejected=True,real_nonshot_and_CHR_rejection_not_counted=True,")
    replace("'Literal generated v2 observer driven by actual compiled CPU entry/return state. No game instructions, pointers, source records or carry results stubbed; no NMI/PPU/native claim.'",
            "'Compiled RemainingDraw still executes exactly; only Lua live-type observation at real render entry is fault-injected to0. Expected rejection and actual compiled-return cleanup checked. Synthetic observer negative, never a game/NMI/PPU/native claim.'")
    assert source.count('synthetic_false_type_at_observer_read_only')==1
    ast.parse(source)
    sys.argv=[str(path),'--ready',str(a.ready),'--output',str(a.output)]
    env=dict(__file__=__file__,__name__='_finite_observer_negative')
    exec(compile(source,str(path)+'::<synthetic-observer-type-negative>','exec'),env)
    env['main']()
    put(a.output/'transformation.json',dict(passed=True,synthetic_observer_negative=True,native_run=False,
        original_tool=str(path),original_tool_sha256=sha(path),checker_sha256=sha(__file__),changes=changes,
        explanation='The qualified source/CPU positive trace stays separate and immutable. Game instructions/RAM/source-art/pointers/carry are never replaced. Only the observer read at actual render entry is intentionally wrong; all real render returns must clear its scope despite early rejection.'))


if __name__=='__main__':main()
