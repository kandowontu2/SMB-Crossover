"""Record this terrain/caller progress without promoting a private build."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,stat
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:dict(path=Path(p).relative_to(R).as_posix(),bytes=Path(p).stat().st_size,sha256=sha(p))


def main():
 out=V/'root-current49-progress-as.json';assert not out.exists()
 checkpoint=R/'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json'
 cp=json.loads(checkpoint.read_text());assert len(cp['source_hashes'])==442
 for n,h in cp['source_hashes'].items():assert sha(R/n)==h,n
 for build in cp['builds']:
  for a in build['artifacts'].values():assert sha(R/a['path'])==a['sha256']
 d=V/'root49-sophia-source-terrain-ik'
 for n,h in json.loads((d/'preparation.json').read_text())['source_sha256'].items():assert sha(d/'source'/n)==h,n
 assert json.loads((d/'static-il.json').read_text())['status']=='PASS_PRIVATE_IK_STATIC_BASELINES_AUDIO_RAM_AND_RESIDENT_CONTINUATIONS'
 assert json.loads((V/'root49-bill-e-review-im.json').read_text())['status']=='PASS_FROZEN_PRIVATE_E_IDENTITY_INTEGRITY_REVIEW'
 counts={k:0 for k in ['root49-sophia-source-terrain-','root49-sophia-source-body-','agent-lsr-sophia-terrain-ib-native-a','agent49-e-sophia-union-a']};total=0;todo=[R]
 while todo:
  with os.scandir(todo.pop())as entries:
   for e in entries:
    try:s=e.stat(follow_symlinks=False)
    except FileNotFoundError:continue
    if getattr(s,'st_file_attributes',0)&0x400:continue
    if stat.S_ISDIR(s.st_mode):todo.append(e.path)
    elif stat.S_ISREG(s.st_mode):
     total+=s.st_size
     for k in counts:
      if k in e.path:counts[k]+=s.st_size
 assert total<60000000000 and counts['root49-sophia-source-terrain-']<500000000
 lsr=V/'agent-lsr-sophia-terrain-ib-native-a'
 current_native={p.name:rec(p)for p in lsr.glob('*.json')}
 union=V/'agent49-e-sophia-union-a'
 union_records={p.name:rec(p)for p in union.glob('*.json')}
 progress=dict(status='ACTIVE_GQ_PRIVATE_SOPHIA_TERRAIN_IK_AND_CONTEXTUAL_COMPOSITION',utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
  predecessor=rec(V/'root-current49-progress-ar.json'),
  previous_goal_turn='Progress: bound and froze private HS normal source body; retained old fixed-tape timing/shell failure and requested full Ryu relocation regression.',
  this_goal_turn='Progress: implemented normal Sophia source head/side queries, prior cache and half-pixel wall response; full caller exposed and corrected hover/underwater brick-none and C2/C3 coin false-ceiling bugs. Both-mapper baseline/audio/RAM/resident checks and96+132 compiled components pass. Contextual E composition compiles privately; no main install.',
  user_steering='Latest Contra backwards-slide message explicitly withdrawn as wrong chat. Subsequent sorry/thanks acknowledged; original goal remains active.',
  current_checkpoint=rec(checkpoint),main_GQ442_sources8_artifacts_exact=True,
  Sophia_IK=dict(preparation=rec(d/'preparation.json'),static=rec(d/'static-il.json'),compiled96=rec(d/'compiled-ig.json'),compiled132=rec(d/'brick-none-ik.json'),
   source_scope='Normal unrotated source19x15.5 head/side/direct-below and wall half-pixel response; cache uses existing character-owned Ryu storage; jumped uses existing Sophia-dormant RgDoubleJump. No added RAM.',
   retained_negatives=['HY long branches; HZ old span assert; IA NMI+7 placement; IC mapper5 BankShadow fixture; IE name-producer carry ABI; IF full-caller hover effects and coin geometry; IJ147-byte branch assembler failure; IK lifecycle fixture sampled cue at later epoch after02 to00; actual clearing writer still being bound before naming it. All retained.'],
   native_records_at_snapshot=current_native,
   native_scope='Original A+B plus wet-rise/hidden60 cases per mapper pass,58/map exact uninterrupted full-call reexecutions; NMI-interrupted cases remain explicit gaps. Additive next-AirSync/cache lifecycle check closure is tracked by the specialist receipt, not inferred from initial60.'),
  HS_Ryu_regression=dict(freeze=rec(V/'agent-lsr-sophia-body-hs-regression-a/freeze.json'),review=rec(V/'agent-lsr-sophia-body-hs-regression-a/final-review.json'),scope='1168 actual calls reexecuted exactly with all10240RAM/AXYP/SP/PC/ordered writes/native cycles and zero interrupted gaps. One obsolete foreign Sophia bbox oracle intentionally superseded; all Ryu/other foreign controls unchanged. No exhaustive interrupt-phase claim.'),
  frozen_E=rec(V/'agent49-gq-bill-union-a/freeze-final-e.json'),root_E_identity_review=rec(V/'root49-bill-e-review-im.json'),
  E_scope='447 source and21overlay files,1024 native receipt files and24 native groups independently rehashed. Identity review only. Scoped costs remain above EC; no universal lag improvement/full-route claim.',
  contextual_E_Sophia_records_at_snapshot=union_records,
  contextual_scope='Private449-source composition; SAMUS head bridge placed in old resident padding to retain bank fit, E spring gates preserved, original audio/RAM/NMI retained. Actual contextual native admission and moved spring caller still assigned; main remains GQ.',
  Samus=dict(stage='Current GQ MMC3 Easy AP observes actual SpringLaunch22189/X3008/Y116, slot1/compression4/forceF4, clears2-1 and enters2-2 at23472. Dies23711/X308/Y112 on Blooper overlap while supported by coral; source edge semantics still being checked, no source bug conclusion.',last_reported_AP_handle=59961,last_reported_AP_terminal=True,phase_ceiling_bytes=1250000000,final_audit_reserve_bytes=100000000,qualification='Prior nonfatal injury at2030 power1→0. No no-injury/small-only/all-upgrades/full-route claim. Next water continuation may be live; consult specialist allocation/actual receipt.'),
  root_live_handles=[],workspace_bytes=total,owned_buckets_bytes=counts,
  phase_ceilings_bytes=dict(global_workspace=60000000000,Sophia_terrain_aggregate=500000000,Sophia_body_aggregate=500000000,LSR_terrain=200000000,contextual_E_Sophia=350000000,Samus_GQ=1250000000,Samus_final_reserve=100000000),
  remaining_requirements=['Finish actual IK/cache lifecycle closure and contextual E full native/ABI/interrupt/moved spring admission.','Source corner calcAxis/order, complete foot span, rotated wall/ceiling/vine anchors and source/native firebar positive bitmap/phase parity remain open.','Fresh controller-only through2-2 routes on the final admitted runtime; all characters/alternates/weapons/upgrades, both mapper coverage and lag profiling remain required.','Final recorded playthroughs and lossless captures remain unfinished; retain all existing negatives/captures.'],
  accepted_release=False,goal_complete=False)
 out.write_text(json.dumps(progress,indent=2)+'\n')
 print(json.dumps(dict(progress=rec(out),workspace_bytes=total,main_GQ_unchanged=True)))


if __name__=='__main__':main()
