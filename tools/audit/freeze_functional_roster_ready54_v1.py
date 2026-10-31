"""Freeze the genuine source-linked 54-ready cart for root native review."""
from pathlib import Path
import json,re
import prepare_functional_roster_ready54_v1 as B
R=B.R;O=B.O;N=B.N
def main():
 assert not(O/'handoff.json').exists()
 for p in[O/'source-proof.json',O/'controls-v2/controls.json']:
  assert B.verify(p)['passed'],p
 B.verify(B.P.parent/'handoff.json');B.verify(B.P.parent/'native-qualified/handoff.json')
 assert not json.loads((O/'controls/controls.json').read_text())['passed']
 # Bind the actual ca65 full dependency record, including binary/CHR inputs.
 line=(N/'main.dep').read_text().split(':\t',1)[1].splitlines()[0]
 dependencies=set()
 for name in re.split(r'(?<!\\)\s+',line):
  if not name:continue
  path=Path(name.replace('\\ ',' '));path=(R/path).resolve()if not path.is_absolute()else path.resolve()
  assert path.is_file(),path
  dependencies.add(path)
 link=json.loads((O/'final-link.json').read_text())['command']
 dependencies.update(Path(x).resolve()for x in link if x.endswith('.o'))
 dependencies.add(N/'private.cfg')
 closure=dict(passed=True,actual_main_dependency_count=len(dependencies),actual_Main_reassembled=True,
  unchanged_components='Actual linked copied objects remain exact to parent c229 frozen source closure; no fictitious component recompile claim.',
  bindings={str(p):B.sha(p)for p in sorted(dependencies)})
 (O/'source-closure.json').write_text(json.dumps(closure,indent=2)+'\n',newline='\n')
 readme='''# Functional roster54 source candidate

Candidate `08f1a75fb13f1974270bf9c6732d050f778f7f5b8b8a3361683416c242a176f3`
is source-linked from native-qualified Quick UI v13 (`7a9e2cc1…`). It keeps
Arthur and Quick ready alongside all52 previously playable profiles.

Only three source files changed: root's two qualified RCR includes and
chip_dale_render.s. Exactly410 ROM bytes differ: ink moves from hardware
window1 to5 with408 matching ink tile LSBs, and CdSetPose changes BEQ to BNE.
All previous symbol addresses, header/CHR/otherPRG, Quick/Arthur/FF payloads,
and full cookies are exact. Actual fixed125 was regenerated from final127.

Current-image CPU checks pass all80 menu variants and10,240 Start/A cases,
actual Arthur/Quick post-Ic Fresh -> forced-blank load -> native entrance8,
and120 genuine Chip/Dale pose/facing selectors. Ready54/pending26 is measured
through actual linked menu code, not inferred from a display or stale ledger.

Root's RCR native source ancestor cleared1-1 plus25 controlled1-2 updates
with controller/gameplay trace equivalence. The current new image has not
been run natively. Root will coordinate its Chip/Dale native review. Inherited
native Lua files in joint are historical artifacts, not a prepared new run.

Arthur and Quick remain laggy WIPs. Their prior controller/graphics/cold/UI
smokes remain bound, with no complete campaign, all-upgrades, CXaudio, or
constant60Hz claim. No native launch, shared edit, new lease or Downloads
installation happened here. No v14/v15 performance experiment was adopted.

The first controls attempt completed its menu cases and reached only an
inherited receipt-path FileNotFoundError. The failed receipt is retained;
v2 fixes that read-only binding path with no behavior/assertion change.

Build recipes are compile-main.json and final-link.json, with exact outputs
validated before execution in output-preflight.json. source-closure.json
binds actual Main dependencies and linked objects; the parent source closure
remains the authority for unchanged component object derivations.
'''
 (O/'HANDOFF.md').write_text(readme,newline='\n')
 tools=[R/'tools/audit'/n for n in['prepare_functional_roster_ready54_v1.py','functional_roster_ready54_controls_v1.py','functional_roster_ready54_controls_v2.py','freeze_functional_roster_ready54_v1.py','private_build_outputs_v1.py']]
 receipts=[B.P.parent/'handoff.json',B.P.parent/'native-qualified/handoff.json',R/'build/arthur-quick-functional-admission-v1/handoff.json',B.RC/'source-proof.json',B.CD/'source-proof.json',R/'docs/qa/checkpoints/2026-10-30/current-rcr-native-misc-repair/receipt.json']
 files=[p for p in O.rglob('*')if p.is_file()]+tools+receipts
 h=dict(status='FROZEN_SOURCE_READY54_REQUIRES_ROOT_NATIVE_REVIEW',candidate=B.sha(N/'candidate.nes'),parent=B.sha(B.P/'candidate.nes'),ready=54,pending=26,source=True,native=False,installed=False,
  newly_ready=['Arthur (menu31/raw32)','Quick Man (menu9/variant2/raw9/bit20)'],previous_52_preserved=True,
  qualified_source_deltas=dict(RCR_bytes=409,Chip_facing_bytes=1,total=410),all_prior_symbol_values_header_CHR_and_other_PRG_exact=True,
  checks=dict(menu_profiles=80,Start_A_all64flags=10240,actual_dual_cold=True,Cd_selectors=120),
  limits=['No native of this final image yet; root coordinates Chip/Dale run.','Measured Arthur/Quick lag remains; functional WIP unlock policy applies.','Full1-1/earned-upgrades/CXaudio for newly unlocked profiles remain open.'],
  bindings={str(p.resolve()):B.sha(p)for p in files})
 (O/'handoff.json').write_text(json.dumps(h,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(candidate=h['candidate'],handoff=B.sha(O/'handoff.json'),bindings=len(h['bindings']),actual_source_inputs=len(dependencies),ready=54,pending=26)))
if __name__=='__main__':main()
