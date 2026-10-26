"""Freeze exact source/CPU protocol candidate; static observer/native budget still required."""
from pathlib import Path
import argparse,hashlib,json,py_compile,shutil
ROOT=Path(__file__).resolve().parents[2]
ROM='0c45ce16fa189debc2303f4df664a0e75f326a807a64bf23280797734615339c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);prepared=a.evidence/'candidate-v5';assert sha(prepared/'candidate.nes')==ROM
 names=['cpu-v1','public-v2','public-nmi-v4','cold-v1','lifecycle-v1','controls-v1','compat-v1','mute-v4','ram-v2','irq-v1','dmc-v1','cost-v1'];receipts={};data={}
 for n in names:
  f=prepared/n/'proof.json';r=json.loads(f.read_text());assert r['passed']and r['ROM_sha256']==ROM;receipts[str(f.relative_to(a.evidence))]=sha(f);data[n]=r
 qpath=a.evidence/'qualified-v3/qualification.json';q=json.loads(qpath.read_text());assert q['passed']and q['ROM_sha256']==ROM;receipts[str(qpath.relative_to(a.evidence))]=sha(qpath)
 hpath=a.evidence/'harness-audit-v1/proof.json';h=json.loads(hpath.read_text());assert h['passed']and not h['startup_static']and not h['native_executed'];receipts[str(hpath.relative_to(a.evidence))]=sha(hpath)
 cost=data['cost-v1'];triples=[r for r in cost['actual_delayed_release']if r['subweapon']in[2,3]];assert all(r['main_delta_vs50b']==51 and r['audio'][0]['delta_vs0802']==330 and r['total90_delta_vs0802']==1309 for r in triples)
 assert data['mute-v4']['callgraph_bound']['max_pending_valid_ingress']==21
 tools=list(sorted((ROOT/'tools/audit').glob('cv3_remaining_sfx_queue256_*.py')))
 tools +=[ROOT/'tools/audit'/n for n in ['cv3_remaining_sfx_queue_prepare_v8.py','cv3_remaining_sfx_complete_irq_v1.py','cv3_remaining_sfx_complete_cpu_v1.py','cv3_dmc_complete_cpu_v1.py','cv3_primary_sfx_source_v1.py','check_tmnt_render_oa.py','check_tmnt_audio_fallback_oc.py','verify_native_relocation.py','robots_weapon_cpu_v1.py','final_item_matrix.py']]
 frozen=a.output/'frozen-tools';frozen.mkdir();hashes={}
 for f in tools:
  py_compile.compile(str(f),cfile=str(frozen/(f.stem+'.pyc')),doraise=True);shutil.copyfile(f,frozen/f.name);hashes[f.relative_to(ROOT).as_posix()]=sha(f)
 negatives=[]
 for pattern in ['resume-negative-v1/proof.json','pause-image-negative-v1/proof.json','candidate-v5/public-nmi-v3/failure.json','candidate-v5/cold-v1/unsafe-first-write.json','candidate-v5/lifecycle-v1/retained-negatives.json','retained-fixture-failures/cv3_remaining_sfx_queue256_ram_v1.py.txt','candidate-v2/prepared.json','candidate-v3/prepared.json','candidate-v4/prepared.json']:
  f=a.evidence/pattern;assert f.exists();negatives.append(dict(path=pattern,sha256=sha(f)))
 report=ROOT/'docs/qa/cv3-remaining-sfx-queue256-2026-10-25.txt';assert not report.exists()
 report.write_text('''CV3 remaining source SFX:256 physical-slot / logical64 SPSC queue
Date:2026-10-25. SOURCE/CPU QUALIFIED; NATIVE/HARNESS/BUDGET UNQUALIFIED.
No production source/install/Git/Downloads mutation. No Mesen process launched.

Accepted deployment parent remains50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363.
Final private candidate0c45ce16fa189debc2303f4df664a0e75f326a807a64bf23280797734615339c.
Exact frozen source:external cv3-remaining-queue256-v1/qualified-v3/source-final.
Full8-file patch and636-deployable-file catalog are beside qualification.json.
Source parent is the HELD7b0 correct64-ring proposal, not a production install.

What changed:
- All main attack/transform/cancel cues remain on one atomic SPSC ring. Main
  owns slots/head and publishes head LAST. NMI alone drains/owns tail and all
  per-voice pending/ID/phase/Owned/Av state. Lag NMIs still advance active FX.
- Queue occupies existing CV1 upper channel RAM$703D..$713C,256 physical slots,
  with logical64 capacity retained. Head/tail/overflow stayRgAudioZp56..58.
  Existing CV3 DMC32..35 and every old shared alias remain unchanged.
- Imported pinned CV1 source directly addresses at mostRgAudioRam+142 even
  with arbitrary byte indices; no imported indirect store exists. All direct
  aliases and wrapper clears are cataloged. The Kind2 cold wrapper skips the
  unused upper clear using a genuine8-byte continuation in its old12-byte
  unreachable Save tail. Original callable Save entry/span stays intact.
- Actual partial-slot cold-NMI negative (unsafe upper clear):bank28 PC$DC18
  writes$713C from5 to0 at+5,193 NMI cycles, losing the next cue. Final has
  zero cold queue writes over1,728 actual full-NMI instruction boundaries.
- Sole real Cv3Spawn caller has literal types1..6 and directly uses a33-cycle
  fast producer. All other public calls keep a genuine checked full/type/world
  entry. That entry now restores originalA after savingY; the64-ring parent
  wrongly passedY as the type.18,432 all-byte/type/world/full/wrap/flag cases
  and1,872 complete real-NMI wrapper boundaries qualify the corrected entry.
- Unowned IDs are explicitly scratch: IDs are meaningful only with their
  Owned bit. Consumer zeros unowned IDs before priority admission. This restores
  the original short reset owner without clearing20 inactive bytes globally.
  Live source voice IDs/priority/APU/phase are exact, not normalized away.
- Mute/pause drains committed cues without ticking FX. No typed26 escapes into
  the common decoder while muted. Pending priorities survive direct resume;
  genuine new-song resume still cancels through the original music owner.

Finite private-caller capacity:
IdleLoop permits at most2 GameLoops between audio NMIs. One weapon dispatch
can emit at most3 shots. Both static movement sites are conservatively counted
(2 possible bat requests per loop; their normal exclusion is not assumed).
That bounds10 source cues plus11 separated CANCEL runs=21, below logical64.
Consecutive pending CANCEL only is idempotent; source events are never coalesced.
Menu has no attack producer and repeated scene cancels dedup;1,536 real menu
reset/vanilla-audio controls remain at occupancy<=2. Active and muted CV1 owners
both drain.1,024 worst21-ingress intervals pass with no overflow/source tick.
Future new producers require a renewed bound; arbitrary unchecked fast calls
are outside this private contract. The public compatibility entry is checked.

Original source and actual owner results on this exact hash:
-14 full original source schedules,343 priorities,512 continued mixed updates;
  raw400F and shared source-high low3 bits remain exact without masks.
-384 real full lag-NMI fast-producer boundaries,780 bat/cancel boundaries,
 1,728 cold boundaries,1,872 compatibility boundaries:4,764 total. Exact return
  AXYP/SP, all nonstack unrelated RAM, actual banks/shadows and five SMC slots.
-256 full64-slot counter/wrap controls.84 actual active lifecycle,70 pending,
 8 bat rejection/exit,60 pool/world,288 full native Cv3Spawn continuations.
-112 pending pause/silence cases and448 resumed frames compare ordered source
  image stores against the original executable. Every complete hardware stream
  also matches a composed pure replay from actual priorLast/image/dirty/mask
  plus the genuine status-owner calls. No resume-write or raw400F exclusion.
-9,472 whole ordinaryAudioUpdate cases across37 identities,80 real base-Simon
  CV1 cross updates,18 unrelated actual KillPlayer chains; ordinary APUs/AXYP/
  game RAM and banks exact except documented new private selected-family state.
-8,192 whole music updates cover every valid area/event/silence menu bit under
  two arbitrary upper-RAM patterns. Actual upper reads/writes=0, music output
  independent of ring data. This bounded indirect-read coverage is not an
  unbounded proof of every future song phase; static write exclusion is exact.
-42,266 actual IRQ/RTI instruction boundaries retain PC/AXYP/SP/R0/R1 and A/C/E
  banks/shadows across original127 and cloned125 resident-code aliases.
-DMC6,048 priorities,72 actual primary/injury owners,1,152 source held-DAC tails,
 5,024 ordinary whole updates; every original sample/rate/DAC/owner assertion
  retained. No source-DMC payload shortening, fixed Bass sample compromise or
  unsafe C-window sample is introduced. This layer does not emulate DMA steals.
-64 generic Fireball controls /6,400 whole updates keep complete output/ABI.
  Base Simon still has its genuine original CV1 cross cue; no existing CV3
  actor owns source14 cross (their third item is stopwatch), so no new cross
  ability/route was invented in this remaining-source-SFX proposal.

Layout and costs, explicitly retained:
-8 changed deployment files versus50b;3 incremental files versus7b. All original
  raw Git EOLs retained.23 genuine queue-private/data-alias symbol exceptions
  are listed,61,099 other7b qualified symbols retained. All original callable
  entry spans and285 source frame PCs retained; no fake callable aliases.
-Service, resident21/1E, unrolled Save/Restore and source frames stay byte exact.
  Versus7b only banks28/29/82/84 change (34/12/316/81 bytes). All other banks,
  header/CHR,125/127 samples/mirror, Mac/Mike/Roll/P-bar owners remain exact.
  Standard flag-off MMC3/MMC5 builds reproduce their original exact hashes.
-Actual triple ice/lightning MAIN release adds51 cycles versus50b, compared
  with141 for7b and519 for0802. This recovers468 of the old519 MAIN cycles.
  The prior73-cycle first-miss margin is only a local measurement;51 does not
  prove a new native deadline or leave a guaranteed22-cycle global margin.
-First triple audio still adds330 cycles versus0802 (104 less than7b), idle/
  steady adds11;90 audio updates add1,309 versus0802. These costs are NOT waived.
  Single release MAIN+17; first audio+214 and90-update+1,193 versus0802.
  Ordinary owner/cold/mute deltas are fully retained in compatibility receipts.
  Removing the old20-byte clear recovers191 cycles; CV1 cold skip recovers509.
  Actual source DMC active ordinary comparison adds28 versus7b; no timing claim.

Retained negatives and test corrections:
-All0802/2e/5ad/ece and64-ring native/cost rejections remain unchanged.
-Unsafe upper clear loses an actual uncommitted cue at the PC above.
-00976 initial protocol and public wrapper drafts remain separate; final0c45
  repairs the checked wrapper's real originalA/Y error without changing fast
  gameplay cost. The all-byte public test keeps its7b negative.
-Initial pause oracle compared the entire host resume hardware flush to an
  isolated original effect tick. That was wrong: GuestAudioFinish deliberately
  invalidatesLast toFF after4015 mute, requiring hardware register replay.
  Both speculative new-admission drafts are rejected and retained. Final
  unmodified source Service uses the corrected full composed hardware oracle.
-Public-NMI oraclev3 wrongly resampled foreignAv after NMI had consumed it.
  Genuine rejection linearizes at its actual LDY sample, retained by NMI;
  accepted cues linearize at head publication. v4 compares all state/APU using
  those real instruction events; v3's exact failing trace stays retained.
-Public-NMIv1 had a helper-keyword TypeError before ROM execution; RAMv1 had a
  Python parse error before ROM execution. Raw failed script retained externally,
  final runnable tools compile. These are fixture failures, not game defects.

Native prerequisite, NOT satisfied:
The historical v7/resident_v2 observer registers new memory callbacks inside
the4014 callback AND inside onReturn calls from executing callbacks. That is
not startup-static. No such harness was launched for this candidate. A new
fixed startup dispatcher needs exact synthetic old/new callback-stream proof
and native same-input observation equivalence before strict cadence tests.
Current native count for0c45 isZERO; no waveform, full campaign, PPU/OAM/CHR,
actual DMA, audible playback, native budget pass, lag-fixed or adoption claim.

Source-only readiness is complete within the stated finite component domain.
Parent review, a safe new observer and fresh native per-case deadline/cadence
qualification remain required before any production composition/adoption.
''',encoding='utf-8',newline='\n')
 nmi=data['cpu-v1']['real_full_lag_NMI_producer_instruction_boundaries']+data['lifecycle-v1']['actual_full_lag_NMI_command_boundaries']+data['cold-v1']['actual_cold_NMI_producer_boundaries']+data['public-nmi-v4']['actual_full_lag_NMI_genuine_checked_public_boundaries'];assert nmi==4764
 result=dict(passed=True,accepted=False,status='SOURCE_CPU_PROTOCOL_READY_STATIC_HARNESS_AND_NATIVE_BUDGET_REQUIRED',ROM_sha256=ROM,source=str(a.evidence/'qualified-v3/source-final'),source_files=q['source_files'],all_deployable_files=q['all_deployable_files'],all_deployable_manifest_sha256=q['all_deployable_files_sha256'],implementation_patch_sha256=q['implementation_patch_sha256'],incremental_patch_sha256=q['incremental_patch_sha256'],receipts=receipts,frozen_tools=hashes,retained_negative_bindings=negatives,report=dict(path=report.relative_to(ROOT).as_posix(),sha256=sha(report)),actual_NMI_boundaries=nmi,actual_IRQ_boundaries=42266,actual_checked_public_cases=18432,max_valid_private_ingress=21,logical_capacity=64,physical_slots=256,main_triple_extra_vs50b=51,first_triple_audio_extra_vs0802=330,steady_extra_vs0802=11,static_native_harness_ready=False,native_grant=False,native_executed=False,new_ROOT_game_source_Git_Downloads_mutations=False,tool_sha256=sha(__file__))
 (a.output/'readiness-source-only.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['source_files','frozen_tools','retained_negative_bindings','receipts']},indent=2))
if __name__=='__main__':main()
