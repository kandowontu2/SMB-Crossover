"""Freeze fused renderer/source-owner proofs and one unrun matched native pair."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import zipfile
from check_tmnt_render_oa import load
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, CURRENT, sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
D9='d9d69ea1a8e6b4eee0f753fd4c33f9873f713a0bde35d2ce61c7ba24718dd523'
DIGEST='70ba4f682723e62b00ef4278c19e3b898383d2903ce6ad6b35199816748217de'


def archive(source,out,parents):
    out.mkdir(parents=True); target=out/'source';shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__'))
    paths={p.relative_to(target).as_posix():p for p in target.rglob('*')if p.is_file()}
    hashes={n:sha(p)for n,p in sorted(paths.items())}
    (out/'source-bindings.json').write_text(json.dumps(hashes,indent=2)+'\n');changes={}
    for name,parent in parents.items():
        old={p.relative_to(parent).as_posix():sha(p)for p in parent.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
        assert not(set(old)-set(hashes))
        changes[name]={n:dict(before_sha256=old.get(n),after_sha256=h)for n,h in hashes.items()if old.get(n)!=h}
        (out/f'changed-source-versus-{name}.json').write_text(json.dumps(changes[name],indent=2)+'\n')
    with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED)as z:
        for n,p in sorted(paths.items()):z.write(p,n)
    return paths,hashes,changes


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;scope=D/'tmnt-equipment-shot-scope-v1';trial=D/'tmnt-source-channel-owner-v1';base=D/'tmnt-parser-tail-writers-v2'
    ready=D/'tmnt-equipment-channel-native-ready-v1';scopefreeze=D/'tmnt-equipment-shot-scope-ready-v1'
    assert not out.exists()and not scopefreeze.exists()and not out.resolve().is_relative_to(ROOT)
    assert sha(scope/'candidate.nes')==D9 and sha(trial/'candidate.nes')==DIGEST
    assert sha(ROOT/'build/smb-crossover-mmc5-expanded.nes')==CURRENT
    proofs={}
    for name in ['owner-cpu-v1','source-goldens-v1','audio-outer-v1','hot404-v1','build-controls-v1',
                 'full-renderer-v1','caller-irq-v1','render-ownership-v1','nmi-liveness-v3']:
        path=trial/name/'proof.json';q=json.loads(path.read_text());assert q['passed']and q['candidate_ROM_sha256']==DIGEST
        proofs[name]=dict(path=str(path),sha256=sha(path))
    gold=json.loads((trial/'source-goldens-v1/proof.json').read_text())
    assert gold['original_calls']==192016 and not gold['regressions']and max(map(int,gold['cycle_delta_histogram']))==0
    read=json.loads((ready/'readiness.json').read_text());assert read['candidate_ROM_sha256']==DIGEST
    for label in ['baseline','candidate']:
        path=ready/(label+'-easy');assert not(path/'host.log').exists()
        assert sha(path/'binding.json')==read['case_bindings'][label]
        binding=json.loads((path/'binding.json').read_text());assert all(sha(Path(n))==h for n,h in binding['dependencies'].items())
        assert json.loads((path/'mock-proof.json').read_text())['passed']
    # The original full-ROM symbol set is real and fixed. Own earlier helpers
    # also remain at their genuine executable entries, without callable aliases.
    assert qualified(base/'candidate.nes').items()<=qualified(trial/'candidate.nes').items()
    assert qualified(scope/'candidate.nes').items()<=qualified(trial/'candidate.nes').items()
    paths,bindings,changes=archive(trial/'source',out,{
        'd9d69':scope/'source','1d741':base/'source',
        '5373':D/'tmnt-sweep-live-math-v1/source',
        '50b5':D/'tmnt-native-storage-current50b5-v1/current-baseline-v1/source'})
    assert set(changes['d9d69'])=={'src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_source_channel_owner.s'}
    assert len(changes['1d741'])==9
    patch=''
    for name in sorted(changes['1d741']):
        old=base/'source'/name
        patch+=''.join(difflib.unified_diff(old.read_text().splitlines(True)if old.exists()else[],paths[name].read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (out/'review.patch').write_text(patch)
    for ext in ['.nes','.lbl','.dbg','.map','.build.json','.cv3-mirror.json']:shutil.copyfile(trial/('candidate'+ext),out/('candidate'+ext))
    bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    old,new=load(base/'candidate.nes'),load(trial/'candidate.nes')
    deltas={n:sum(x!=y for x,y in zip(bank(old['raw'],n),bank(new['raw'],n)))for n in range(128)};deltas={n:v for n,v in deltas.items()if v}
    assert set(deltas)=={63,87}
    assert bank(new['raw'],87)[0x1500:0x1700]==bank(old['raw'],87)[0x1500:0x1700]
    # New original-source edits are exactly seven two-byte JSR operands and
    # the23-byte helper. Every remaining original instruction/data byte is exact.
    source_delta=[i for i,(x,y)in enumerate(zip(bank(load(scope/'candidate.nes')['raw'],63),bank(new['raw'],63)))if x!=y]
    prep=json.loads((trial/'channel-owner-preparation.json').read_text())
    allowed=set(range(0x2e0,0x2f7))
    for row in prep['replaced_real_direct_calls']:allowed|={row['runtime_PC']-0xa000+1,row['runtime_PC']-0xa000+2}
    assert set(source_delta)==allowed
    names=['tmnt_equipment_shot_scope_source_v1.py','tmnt_equipment_shot_scope_ownership_v1.py','tmnt_equipment_shot_scope_irq_v1.py',
           'tmnt_equipment_shot_scope_nmi_liveness_v1.py','tmnt_equipment_shot_scope_nmi_liveness_v2.py','tmnt_equipment_shot_scope_nmi_liveness_v3.py',
           'tmnt_source_channel_owner_source_v1.py','tmnt_source_channel_owner_cpu_v1.py','tmnt_source_channel_owner_render_ownership_v1.py',
           'tmnt_source_channel_owner_build_controls_v1.py','tmnt_equipment_channel_native_ready_v1.py','tmnt_equipment_channel_finalize_v1.py',
           'tmnt_equipment_empty_scans_cpu_v1.py','tmnt_parser_math_next_cpu_v1.py','tmnt_parser_math_next_outer_v1.py',
           'tmnt_parser_math_next_hot_v1.py','tmnt_static_observer_mock_v2.py']
    (out/'tools').mkdir();tools={}
    for name in names:
        p=ROOT/'tools/audit'/name;shutil.copyfile(p,out/'tools'/name);tools[name]=sha(p)
    scopes,scopebindings,scopedelta=archive(scope/'source',scopefreeze,{'8d602':D/'tmnt-equipment-cold-kind-v1/source','1d741':base/'source'})
    scopeproofs={}
    for name in ['full-renderer-v1','caller-irq-v1','ownership-v1']:
        path=scope/name/'proof.json';q=json.loads(path.read_text());assert q['passed']and q['candidate_ROM_sha256']==D9
        scopeproofs[name]=dict(path=str(path),sha256=sha(path))
    for ext in ['.nes','.lbl','.dbg','.map']:shutil.copyfile(scope/('candidate'+ext),scopefreeze/('candidate'+ext))
    scopeq=dict(frozen=True,source_CPU_only=True,native_run=False,accepted=False,ROM_sha256=D9,source_files=len(scopes),
                source_bindings_sha256=sha(scopefreeze/'source-bindings.json'),source_archive_sha256=sha(scopefreeze/'source.zip'),proofs=scopeproofs,
                changed_sources={n:len(v)for n,v in scopedelta.items()},preserved_cold_added_cycles=[2,7],actual_shape_saving_range=[393,402])
    (scopefreeze/'receipt.json').write_text(json.dumps(scopeq,indent=2)+'\n')
    negatives={}
    for name in ['nmi-liveness-v1','nmi-liveness-v2']:
        p=trial/name/'failure.json';assert json.loads(p.read_text())['fixture_invalid'];negatives[name]=dict(path=str(p),sha256=sha(p))
    negatives['previous_8d602_performance_HOLD']=dict(path=str(D/'tmnt-equipment-emitter-ready-v1/receipt.json'),sha256=sha(D/'tmnt-equipment-emitter-ready-v1/receipt.json'))
    negatives['cold_positives_d9_and70']=dict(path=str(trial/'render-ownership-v1/cases.json'),sha256=sha(trial/'render-ownership-v1/cases.json'),maximum_added_cycles=7)
    (out/'retained-negatives.json').write_text(json.dumps(negatives,indent=2)+'\n')
    erratum={'render_ownership_v1_limits':dict(path=str(trial/'render-ownership-v1/proof.json'),sha256=sha(trial/'render-ownership-v1/proof.json'),
        correction='The retained generic limits string incorrectly describes original audio goldens as inherited through exact core bytes. This final candidate changes37 bytes in bank63. Audio closure uses the FRESH192016 original-source comparison, owner domain/IRQ and fullAudio proof, not byte-exact inheritance for those37 bytes.'),
        'models':'441 primary acceptance erratum and735 secondary reconstruction remain models. Saving425 was not a recovery proof; first508actual DMA exact evidence remains additive. Native5373 four lost secondary drawings and all original strict-prefix failures remain untouched.'}
    (out/'reporting-errata.json').write_text(json.dumps(erratum,indent=2)+'\n')
    report=f'''TMNT FUSED SHOT CALLER + ORIGINAL CHANNEL-OWNER SOURCE CANDIDATE
2026-10-26. Accepted production remains {CURRENT}
Exact private candidate {DIGEST}
Exact drawing-only precursor {D9}
Source/CPU qualified; one matched Easy600 pair prepared but UNRUN/UNGRANTED.

The d9 caller replaces the genuine ShotPointer three-byte LDY with a same-size
JMP. It inlines original pointer/coordinate setup, removes only the discarded
initial R4/R5 input copies and two JSR/RTS pairs, and retains X=shot slot.
Y may temporarily hold pose instead of facing. Literal original TnWorldDraw
remains the uncommon/edge/full-capacity fallback. The six admitted original
two-layer shuriken records retain exact sprite X/Y/attribute/tile store order,
rotation, wrap/capacity/clipping, scratch, full final AXYP/SP/SMC/RAM and C88
publication. The real new646-byte scope is A87 BC8D..BF12, in declared FF tail;
all old entries and spans remain genuine/fixed. Icon/shuriken entries and their
655/766-byte spans remain exact. Shared C87 D500..D6FF is unchanged.

Scope qualification:5262 renderer cases/all168 original world entries;16384
full actual caller cases/all64P/icons/variants/capacity/rotation;1849 actual
compiled IRQ boundaries with all five IRQ hardware stores independently exact.
10000 expanded pending-kind/cold/fullflags/world-wrap cases pass. Full source
write/control closure contains944 reachable new rendering instructions.
538 actual compiled lag-NMI CPU injections at new scratch boundaries preserve
PC/AXYP/SP/banks/R0..R7 and exactly every ordered nonstack NMI store compared
with literal old setup. No unfinished OAM publication. Max total stack35.
This is CPU source liveness, not physical PPU/DMC/NMI scheduling qualification.

Additional source63 helper TnSourceChannelOwner is23 bytes A2E0..A2F6 of the
verified last32 bytes. Seven real original JSR operands are retargeted (14B).
Original ACE8 and raw-APU mode remain literal/executable. The old nonzero-X
path never changes A before PLA: preserve A directly, use ORA#0 to reproduce
its original final N/Z and retain the same LDX/CLC/V/D/I/Y. The entire original
X=0 PHA/PLA/conditional carry behavior remains. All1289 original instructions
and369 connected pointer words exclude replacement-interior entry.
691968 complete byte/flag/actual-caller cases pass; all64P/all256A/actual X0..5,
all256X with A edges, Y and stack edges. Only discarded stack writes differ.
208 real IRQ boundaries pass including exact five IRQ stores. Cost is exactly
0 for X=0 and minus5 for nonzeroX. No added source call cost.

Fresh full original executable comparison:192016 calls/all16songs;549602
ordered original requests and1099204 writer-return ABI checks; full188-byte
source state/foregroundZP/registers/stack/SMC/banks/source-owned product streams
pass. Every call delta0..minus40, no positive call. Original tracks, samples,
events, voices, stores and clocks are retained. Fresh602 actual native188-byte
inputs and every nonstack source write also pass. Actual source533 core2857
becomes2827 (minus30);5351641 becomes1621 (minus20). The remembered minus27
lead was unverified and is superseded by these exact measurements.

Fresh12256 complete37-identity AudioUpdate/ExpandedAudioUpdate comparisons
against1d741 pass. All36 foreign identities have exact outcomes and zero cost
change; coldTMNT0 and warmTMNT0..minus40. These are relative to1d741's already
composed source, including held0c45 CV3 work, not new acceptance claims versus
production50b5. Fresh602 wholeAudio calls with DISCLOSED arranged shared cue404
and physical4015 BEFORE-call status controls pass: extra savings20/35/30 at
407/505/533. No complete native mixer/Main RAM snapshot existed in old capture.

Constrained actual-shaped equipment1255/1256 ->853..863 saves393..402.
Combined source533 saving347 versus held5373 gives740..749 against735 model:
only5..14 modeled margin. This does NOT prove native draw recovery. Explicit
cold drawing positives remain:drop/private-only plus2, selected dense pose75
rejection up to plus7. Three ordinary boomerang/Kiai paths now SAVE55 rather
than add38; legal pending-kind/capacity domain saves2..672. All positives,
previous8d602 plus119, first-c195 plus191 and earlier native negatives remain.
No universal performance/no-harm claim is made.

Only63/87 change versus1d741 ({deltas}); all old1d741 symbols/header/CHR/other
banks are exact. No use of A62/C94/shared125 and no new RAM/math/DMC owner.
The previously reserved63 tail is now used by this separately authorized
source helper;9 bytes remain, no further reservation/availability claim.
Canonical rebuild reproduces this exact hash. Ordinary flagoffs remain
d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb(MMC3) and
f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833(MMC5).

Two invalid lag-NMI fixture attempts are retained: synthetic RAM copying
replayed mapper writes, then the old direct emitter bypassed the generic
world-draw checkpoint. v3 uses real bank state and actual old emitter entry;
same exact foreground/store assertions pass, without a ROM change.
render-ownership-v1's generic audio-inheritance sentence is explicitly corrected
in reporting-errata.json; fresh original-source music proofs are authoritative.

Unrun native readiness uses unchanged historical600 updates, numeric Easy0,
actual readback, source/APU/merged4015/DMC completion/owner/tail/preemption,
pause/events/reset, IRQ/NMI/5SMC/stack/banks/mirror/OAM/CHR and cumulative prefix
guards. Source inventory only BEFORE phases, identical paired controls; no
within-phase outcomes/cadence/RNG/resources/sample owner injection. Static
dispatcher preserves the qualified historical workload/import bodies exactly.
Current C:/Mesen2 runtime/settings are bound without modifying user settings.
Lua syntax/startup/order mocks passed; they are not native gameplay. Baseline
and candidate commands are frozen. No launch until ROOT explicitly grants.
No production source/config/Git/Downloads write or installed-build change.
'''
    (out/'report.txt').write_text(report)
    doc=ROOT/'docs/qa/tmnt-equipment-channel-2026-10-26.txt';doc.write_text(report+'\nFrozen packet: '+str(out)+'\n')
    qualification=dict(passed=True,source_CPU_only=True,native_run=False,accepted=False,ROM_sha256=DIGEST,proofs=proofs,
                       source_files=len(paths),source_bindings_sha256=sha(out/'source-bindings.json'),source_archive_sha256=sha(out/'source.zip'),
                       changed_PRG_bytes_versus1d741=deltas,changed_source_counts={n:len(v)for n,v in changes.items()},
                       all_old1d741_symbols_RAM_header_CHR_and_otherbanks_exact=True,reporting_errata_sha256=sha(out/'reporting-errata.json'),
                       source_goldens_fresh_not_inherited=True,renderer_positive_cold_costs=[2,7],source_every_call_nonpositive=True,
                       no_native_cadence_or_recovery_claim=True)
    (out/'qualification.json').write_text(json.dumps(qualification,indent=2)+'\n')
    receipt=dict(frozen=True,source_CPU_only=True,native_run=False,native_grant=False,accepted=False,ROM_sha256=DIGEST,
                 qualification_sha256=sha(out/'qualification.json'),tools=tools,source_archive_sha256=sha(out/'source.zip'),
                 source_bindings_sha256=sha(out/'source-bindings.json'),changed_sources={n:len(v)for n,v in changes.items()},
                 drawing_precursor_receipt_sha256=sha(scopefreeze/'receipt.json'),retained_negatives_sha256=sha(out/'retained-negatives.json'),
                 native_readiness=dict(path=str(ready/'readiness.json'),sha256=sha(ready/'readiness.json')),
                 commands=dict(path=str(ready/'commands.json'),sha256=sha(ready/'commands.json')),
                 report_sha256=sha(doc),checker_sha256=sha(Path(__file__)))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(frozen=True,ROM_sha256=DIGEST,source_files=len(paths),changed_source_counts=receipt['changed_sources'],
                         receipt_sha256=sha(out/'receipt.json'),qualification_sha256=sha(out/'qualification.json'),
                         report_sha256=sha(doc),native_readiness_sha256=sha(ready/'readiness.json'))))


if __name__=='__main__':main()
