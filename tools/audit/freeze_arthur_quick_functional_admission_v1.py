"""Freeze the read-only dual-ready composition proposal and exact negatives."""
from pathlib import Path
import json,hashlib
import arthur_quick_functional_admission_v1 as A
R=A.R;O=A.O;N=A.N
def main():
 assert not(O/'handoff.json').exists()
 for p in [O/'proposal.json',O/'actual-menu-readiness.json',O/'cold-v2/actual-cold-chains.json']:
  d=json.loads(p.read_text());assert d['passed'],p
  for name,digest in d.get('bindings',{}).items():assert A.sha(name)==digest,name
 # The prior count mistake is corrected by actual ROM table plus actual CPU
 # results. The Select publication negative is kept, not silently overwritten.
 assert not json.loads((O/'cold/actual-cold-chains.json').read_text())['passed']
 preserve=[]
 for p in sorted((N/'src').glob('river_city*')):
  old=A.P/'src'/p.name;assert old.is_file()and A.sha(old)==A.sha(p)
  preserve.append(dict(relative=p.relative_to(N).as_posix(),sha256=A.sha(p)))
 # Names/pending portraits are genuine retained source tables, independent of
 # the intentional two ready-predicate changes earlier in the same module.
 old=(A.P/'src/full_roster_menu.s').read_text();new=(N/'src/full_roster_menu.s').read_text()
 marker='; Handle the newly visible alternate families before legacy Select handlers.'
 assert old.split(marker,1)[1]==new.split(marker,1)[1]
 summary=dict(passed=True,river_city_sources_byte_exact=preserve,full_roster_all_Select_handlers_name_portrait_color_tables_exact=True,scope='Only FmPending has intended Quick/Arthur predicate changes; source tables/Select ordering remain identical to installed a7cc.')
 (O/'frontend-preservation.json').write_text(json.dumps(summary,indent=2)+'\n',newline='\n')
 text='''# Arthur and Quick functional WIP admission proposal

Use the already source-linked, native-qualified Quick UI v13 cart as the
private combined base. It already exposes Arthur and Quick: no additional
pending-gate edit is needed. This packet changes no source or ROM.

| Item | Exact result |
|---|---|
| Installed parent | a7ccbaaa7aab598d36e8806e30475eab36174ee1948f25f90ae72e6640f43f48 |
| Proposed base | 7a9e2cc1246d590bebe2acd5451267894f39cdac75cd528e20109de01753d760 |
| Actual menu readiness | 80 profiles, 54 ready / 26 pending; previous 52 retained |
| Quick identity | cell9, third Select variant, raw9 + FmAlts bit20 |
| Arthur identity | cell31, raw32; cell25 is Gimmick raw26 |
| Menu launch CPU proof | 10,240 actual Start/A prefix cases, all64 flags |
| Actual source cold paths | native menu/Start, post-Ic Fresh, forced-blank InitScreen, native entrance8 for both |
| Quick native evidence | same7a9e, 220 gameplay frames; loader/fullcookie/HP40/UI/body/fan/scroll pass |
| Arthur native evidence | source ancestor1437, 400 gameplay frames; original20Hz clock/doublejump/lance/body pass |

The actual constructor chains preserve native IcGlobalInit and SunnyGlobalInit
once. Quick menu retirement precedes ArGenResolve. QwSceneInit chains through
ArGenSceneInit and FwSceneInit to the native screen callback. Each source owner
loads only at forced blank, verifies its full16-byte C2 cookie, and publishes
ready last. Current-source cold receipts exercise these paths together.

The source inventory and shared-source-overlaps.patch describe the genuine
delta from installed a7cc. They include current Quick movement/terrain/UI
gates, Arthur physical-clock/mailbox and fair renderer, plus still-pending FF
source. They are an inventory, not a patch to apply blindly to another branch.
The exact compiler and link recipes remain bound by v13's source handoff;
validate all outputs beneath a NEW private root before any replay.

Root's RCR window repair must be source-composed into a new successor. All
current RCR source files are byte-exact to a7cc and remain untouched here.
Peer FF lifecycle must retire before genuine QwMenuResolve; its scene worker
must preserve QwSceneInit -> ArGenSceneInit -> FwSceneInit. SMB2/Roll producers
are not present and need genuine source integration. Existing common/A79
capacity must be retained, rather than copying a predecessor shared segment.

Measured lag remains substantial (Arthur266/400 observed; Quick137 additional
lag NMIs/220). It is disclosed rather than used as a lock under the current
functional WIP policy. Full1-1, earned powerups, complete CX audio, all native
abilities, and sustained60Hz are not established by these smoke witnesses.
No native process, installation, shared edit, or new allocation occurred.

The v1 cold fixture's Select C-publication assertion failure is retained.
The v2 fixture permits this documented native callback publication while
continuing to check restored A/low/fixed maps and C hardware/shadow agreement.
The v13 observer's unused strengthened UI hook is also retained: root's
independent exact-interval review proved one QhUi in all122 actual Main spans.
'''
 (O/'HANDOFF.md').write_text(text,newline='\n')
 tools=[R/'tools/audit'/n for n in ['arthur_quick_functional_admission_v1.py','arthur_quick_functional_cold_v1.py','arthur_quick_functional_cold_v2.py','freeze_arthur_quick_functional_admission_v1.py']]
 files=[p for p in O.rglob('*')if p.is_file()]+tools
 for name in ['handoff.json','native-qualified/handoff.json']:
  files.append(N.parent/name)
 files.extend([R/'build/arthur-physical-clock-v2/handoff.json',R/'build/arthur-physical-clock-v2/native-handoff-v3.json'])
 h=dict(status='FROZEN_FUNCTIONAL_WIP_DUAL_READY_PROPOSAL_NO_INSTALL',candidate=A.sha(N/'candidate.nes'),source_handoff=A.sha(N.parent/'handoff.json'),ready=54,pending=26,all_previous_52_ready=True,source_edits=False,native_launch=False,performance='Lag disclosed; not a readiness lock under current user priority',unimplemented_performance_proposals=['v14 is source-only and not adopted','v15 constant-query adapter is proposal-only and stopped'],bindings={str(p.resolve()):A.sha(p)for p in files})
 (O/'handoff.json').write_text(json.dumps(h,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(handoff=A.sha(O/'handoff.json'),bindings=len(h['bindings']),candidate=h['candidate'],ready=54,pending=26)))
if __name__=='__main__':main()
