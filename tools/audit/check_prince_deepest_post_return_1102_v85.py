"""Each reached transport/hook/router instruction at its deepest real stack."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_stack_1102_v80 as V
import check_prince_post_return_vblank_1102_v83 as D
O=V.O


def fold_cuts(cuts):
 selected={}
 for pc,sp,bank in cuts:
  key=(pc,bank)
  if key not in selected or sp<selected[key][1]:selected[key]=(pc,sp,bank)
 return sorted(selected.values())


def main():
 source=Path(V.__file__);text=source.read_text().replace('v80','v85')
 text=text.replace("try:env['main']()", "try:\n  env['state']=drained_state\n  env['main']()")
 marker=" env=dict(__file__"
 injection=" text=text.replace(\"cuts=sorted(ref['cuts'])\",\"cuts=fold_cuts(ref['cuts'])\")\n text=text.replace(\"or bank==2 and lab['PpNativeTick']\",\"or bank==2 and lab['PpNativeRoute']<=c.pc<lab['PpNativePublicEnd'] or bank==2 and lab['PpNativeTick']\")\n text=text.replace(\";minimum=min(minimum,ref['minSP'])\",\";print('Deepest IRQ instructions',name,len(cuts),flush=True);minimum=min(minimum,ref['minSP'])\")\n"
 text=text.replace(marker,injection+marker)
 text=text.replace('CURRENT_LOADED=A.loaded)', 'CURRENT_LOADED=A.loaded,fold_cuts=fold_cuts)')
 env=dict(__file__=str(Path(__file__)),__name__='prince_deepest_postreturn_v85',drained_state=D.drained_state,fold_cuts=fold_cuts);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'native-stack-CPU-v85.json';q=json.loads(path.read_text());q.update(cut_domain='Each reached instruction PC/A-bank pair at its deepest foreground SP in each actual scenario; repeated shallower contexts are deduplicated, never deeper contexts.',final_native_VRAM_and_queue_compared_after_equal_real_VBlank_drains=True,immediate_ISR_private_scratch_five_SMC_mapper_and_register_guards_unchanged=True,lag_NMI_native_VRAM_drain_negative_retained='post-return-boundary-v82.json')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,Path(D.__file__),O/'post-return-boundary-v82.json',O/'post-return-foreign-CPU-v81.json',O/'tag-transport-CPU-v84.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
