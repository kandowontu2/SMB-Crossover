"""Immutable64-ring source/protocol/cost packet, explicitly HELD without native launch."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
ROM='7b0a2cbdd806ff057d86c1af1834ecac5d34e1bb1747852e93d6ca2ec3d2fec2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert sha(a.prepared/'candidate.nes')==ROM;a.output.mkdir(parents=True,exist_ok=False)
 paths=['cpu-v2/proof.json','lifecycle-v2/proof.json','controls-v1/proof.json','compat-v1/proof.json','irq-v1/proof.json','dmc-v1/proof.json','cost-v1/proof.json','qualified-v1/qualification.json'];receipts={};data={}
 for name in paths:
  q=json.loads((a.prepared/name).read_text());assert q['passed']and q['ROM_sha256']==ROM;receipts[name]=sha(a.prepared/name);data[name]=q
 q=data['qualified-v1/qualification.json'];cost=data['cost-v1/proof.json'];triple=[r for r in cost['actual_delayed_releases']if r['subweapon']==3];assert all(r['main_extra_vs50b']==141 and r['audio_delta_range']==[11,434]for r in triple)
 tools=['cv3_remaining_sfx_queue_'+n+'.py'for n in['prepare_v8','cpu_v2','lifecycle_v2','controls_v1','compat_v1','dmc_v1','cost_v1','qualify_v1','freeze_v1']]+['cv3_remaining_sfx_complete_irq_v1.py','cv3_remaining_sfx_complete_cpu_v1.py','cv3_dmc_complete_cpu_v1.py','cv3_primary_sfx_source_v1.py','check_tmnt_render_oa.py','check_tmnt_audio_fallback_oc.py','verify_native_relocation.py','robots_weapon_cpu_v1.py','final_item_matrix.py'];frozen=a.output/'frozen-tools';frozen.mkdir();tool_hashes={}
 for name in tools:
  f=ROOT/'tools/audit'/name;tool_hashes[f.relative_to(ROOT).as_posix()]=sha(f);shutil.copyfile(f,frozen/name)
 report=ROOT/'docs/qa/cv3-remaining-sfx-queue-2026-10-25.txt';assert not report.exists()
 report.write_text('''CV3 remaining source SFX: atomic64-request ring, source-only HELD packet
Date:2026-10-25. No native worker used; no production source/install/Git mutation.

Parent is the rejected0802 source candidate; deployment parent remains accepted
50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363.
Private candidate7b0a2cbdd806ff057d86c1af1834ecac5d34e1bb1747852e93d6ca2ec3d2fec2.
Exact source:cv3-remaining-queue-v8/qualified-v1/source-final under the external
2026-10-24-native-rest-py evidence directory. No adoption or lag-fixed claim.

Implemented protocol:
- Main exclusively writes cue slots and its8-bit head, publishing head LAST.
  NMI exclusively drains committed entries and writes tail. Reset flushes
  tail=head without rewriting an interrupted producer's head or slot.
- All main effects1..6, bat7 and cancel8 use the same ring. No main-side Av26,
  voice-ID, Owned, active or per-voice pending publication remains. The NMI
  consumer chooses the existing source1F legacy path or the complete per-voice
  source owner; old FX continue on lag NMIs. Full rejects without overwrite.
- Only consecutive pending CANCEL commands are idempotently deduplicated.
  No attack/transform source-effect request is dropped/coalesced. A consumed
  earlier cancel cannot be followed by a main producer while the main CPU is
  suspended; every dedup producer boundary was tested with the actual NMI.
- Off-game menu resets no longer accumulate64 cancels while vanilla audio
  bypasses the CV3 consumer.1,536 real scene-reset/vanilla-update controls stay
  within2 slots and genuine new-music resume flushes them.
- Sole gameplay Cv3Spawn JSR directly targets the new producer. Old genuine
  compatibility entry remains with saved AXYP. Full caller continuation
  preserves all gameplay RAM and A/X/Y/P/stack; no artificial callable aliases.

Ownership/layout:
- Existing160-byte selected-family slab only; no new SRAM allocation or CHR.
  Old wrappers use0..23(CV1),0..16(Contra/Zelda),0..6(Gradius); old CV3 aliases
  stop at55. New head56,tail57,overflow58,slots64..127. Full source mentions,
  all numeric aliases and dynamic wrapper bounds are in lane-ownership.json.
- Final8 deployable files are independently enumerated, with original Git raw
  EOL bindings. Increment from0802 is3 files.17 genuine private branch labels
  move/disappear;61,086 other qualified0802 symbols and285 frame PCs remain.
- Existing Service, resident source21/1E path and unrolled Save/Restore bytes
  remain exact. Only banks28/29/82/84 differ from0802(127/14/451/248 bytes).
  All other banks/header/CHR, fixed127/mirror125, DMC samples, Mac/Mike/Roll
  and P-meter owners are exact. Normal MMC3/MMC5 flag-off hashes are exact.

Fresh CPU/source results, all bound to this exact hash:
-14 original schedules,343 independent voice-priority cases,512 continued
  mixed original updates; raw400F retained without masking.
-256 full64-slot/wrap cases;960 real full lag-NMI shot-producer boundaries
  plus832 full lag-NMI bat/cancel-command boundaries. AXYP/SP/banks and all
  nonstack unrelated state compared. Ring sequence counts may differ only for
  proved idempotent CANCEL; subsequent exact source/phase/APU results match.
-84 active lifecycle,70 pending lifecycle,8 bat exit/rejection,60 pool/world,
 288 full Cv3Spawn successful/failed caller continuations.
-9,472 ordinary wholeAudioUpdate across37 identities,80 base-Simon cross
  updates,18 unrelated actual KillPlayer chains retain APU/RAM/AXYP/banks.
-42,334 actual IRQ/RTI instruction boundaries cover source requests/FX and
  both125/127 E-window code aliases. No physical DMC bus or PPU claim.
-DMC:6,048 priorities,72 actual primary/injury owners,1,152 held-DAC source
  completion tails,5,024 ordinary updates; source samples/rates/DAC remain.
  Only new-family state and verified pending-CANCEL Av26 transient differ in
  the old direct-scene RAM comparator; every original DMC/APU assertion stays.
-64 generic-Fireball/control cases (6,400 updates) keep exact APU/outerAXYP.
  The shared world mixer excludes generic Fireball for the native CV1 family;
  no bank7 helper was added, and bank7 is exact.

HELD for explicit cost:
- Actual Sypha delayed ice/lightning release adds141 MAIN cycles versus50b,
  compared with519 for0802. This is378 cycles recovered, still exceeding the
  measured first-miss73-cycle baseline margin before earlier phase costs.
- First request audio update adds434 cycles versus0802; idle/steady adds11.
 90 audio updates add1,413 cycles for triple releases. No padding/phase tricks.
- Cold/mute owner clearing also adds191 cycles for many unrelated guests;
  Simon-family first-update maxima220 are disclosed. Ordinary output equality
  does not imply zero scheduling cost. The64-ring is NOT native-ready.
- The next source-only lead is256 physical slots in authenticated unused CV1
  upper channel RAM, bounded private producer + checked compatibility entry,
  and safe cold-reset publication. Full owner/reset reachability and actual
  partial-write NMI proof are required before implementation acceptance.

Scope limits:
The global maximum gameplay producer count and all cross-family stale-world
admission domains are not certified by these component tests. Full64/overflow
behavior is defensive and exact; it is not evidence of a complete campaign.
No new emulator, actual controller playthrough, hardware DMA/PPU, waveform,
native deadline or source remaining-SFX adoption is claimed.

Retained failures:
v1/v2 assembler long-branch failures;v3 bank7 helper placement rejection;
v4 old legacy-bypass actual-NMI race;v6 repeated-menu cancel overflow;v7 Y
clobber on Samus/Ryu/Sophia mute. CPUv1 misclassified a repeated Av26 store as
unpublished;v2 uses actual write events. Lifecyclev1 incorrectly compared the
old main-owned NoiseActive marker;v2 declares its moved NMI ownership. All old
files/results retained. Original0802/2e/etc native cadence failures unchanged.
''',encoding='utf-8',newline='\n')
 result=dict(passed=True,accepted=False,status='SOURCE_PROTOCOL_QUALIFIED_COMPONENTS_CPU_BUDGET_HELD_NO_NATIVE',ROM_sha256=ROM,held_parent_ROM_sha256=sha(a.prepared/'baseline.nes'),source=str(a.prepared/'qualified-v1/source-final'),source_files=q['source_files'],implementation_patch_sha256=q['implementation_patch_sha256'],incremental_patch_sha256=q['incremental_patch_sha256'],all_deployable_files=q['all_deployable_files'],all_deployable_manifest_sha256=q['all_deployable_files_sha256'],receipts=receipts,frozen_tools=tool_hashes,report=dict(path=report.relative_to(ROOT).as_posix(),sha256=sha(report)),protocol_NMI_boundaries=1792,real_IRQ_boundaries=42334,main_three_release_extra_vs50b=141,held0802_main_three_release_extra_vs50b=519,first_audio_extra_vs0802=434,idle_extra_vs0802=11,unrelated_cold_mute_extra_max=191,native_grant=False,native_executed=False,global_gameplay_capacity_proof_complete=False,no_ROOT_source_Git_Downloads_mutation=True,tool_sha256=sha(__file__))
 (a.output/'readiness-held.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['source_files','frozen_tools']},indent=2))
if __name__=='__main__':main()
