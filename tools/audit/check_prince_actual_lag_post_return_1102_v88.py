"""Actual GameLoop-negative NmiDisable convention, deepest native ISR proof."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_stack_1102_v80 as V
import check_prince_post_return_core_1102_v79 as A
import check_prince_native_stack_1102_v72 as S
O=A.O


def loaded():
 b,m,lab=A.loaded();S.N.put(m,NmiDisable=255)
 return b,m,lab


def fold_cuts(cuts):
 result={}
 for pc,sp,bank in cuts:
  key=(pc,bank)
  if key not in result or sp<result[key][1]:result[key]=(pc,sp,bank)
 return sorted(result.values())


def main():
 source=Path(V.__file__);text=source.read_text().replace('v80','v88')
 text=text.replace("target=='GameCoreRoutine'", "name=='fatal-kill'")
 marker=" env=dict(__file__"
 injection=" text=text.replace(\"cuts=sorted(ref['cuts'])\",\"cuts=fold_cuts(ref['cuts'])\")\n text=text.replace(\"or bank==2 and lab['PpNativeTick']\",\"or bank==2 and lab['PpNativeRoute']<=c.pc<lab['PpNativePublicEnd'] or bank==2 and lab['PpNativeTick']\")\n text=text.replace(\";minimum=min(minimum,ref['minSP'])\",\";print('Deepest actual-lag instructions',name,len(cuts),flush=True);minimum=min(minimum,ref['minSP'])\")\n text=text.replace(\"assert not c.p&4\\n\",\"assert not c.p&4;assert N.get(m,'NmiDisable')==255\\n\")\n text=text.replace(\"cuts=len(cuts)))\",\"cuts=len(cuts)))\\n  print('Completed actual-lag scenario',name,dict(counts),minimum,flush=True)\")\n"
 text=text.replace(marker,injection+marker)
 text=text.replace('CURRENT_LOADED=A.loaded)', 'CURRENT_LOADED=actual_loaded,fold_cuts=fold_cuts)')
 env=dict(__file__=str(Path(__file__)),__name__='prince_actual_lag_v88',actual_loaded=loaded,fold_cuts=fold_cuts);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'native-stack-CPU-v88.json';q=json.loads(path.read_text());q.update(actual_lag_NmiDisable=255,actual_lag_path_source='src/game.s GameLoop LDA#FF/STA NmiDisable; src/reset.s NMI BPL regular, negative branches lag without queue/OAM publication.',cut_domain='Every reached shared/hook/router/native-gateway PC/A-bank pair at deepest real SP in each scenario.',full_private_native_scratch_SMC_mapper_and_return_parity=True,regular_NMI_prior_labels_corrected=True,scope='Actual complete GameCore earned-death then post-resident native hook, row8 death update, native star/1up. Each deepest reached instruction runs real IRQ and genuine negative-flag lag-NMI; no VRAM/OAM difference is normalized or excluded. Initial1 earlier receipts exercised regular NMI; they are not lag qualification. Changed-source cold/auth/resources/menu/native emulator remain unqualified/ungranted.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,R/'src/game.s',R/'src/reset.s',O/'post-return-foreign-CPU-v81.json',O/'tag-transport-CPU-v84.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
