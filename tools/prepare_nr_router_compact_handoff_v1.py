"""Freeze exact standalone current-semantics router; no native or adoption."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools/audit'))
import nr_router_compact_controls_v1 as C
from sunny_integrated_controls_v1 import *
B=R/'build';H=B/'nr_router_compact_handoff_v1.json'

def main():
    assert not H.exists()
    inputs=[B/'nr_router_compact_layout_v1.json',B/'nr_router_compact_controls_full_fast_v1.json',B/'nr_router_compact_ordered_smc_v1.json',B/'nr_router_compact_supplement_v1.json',B/'nr_router_compact_coherent_callers_v2.json']
    proofs=[json.loads(p.read_text())for p in inputs];assert all(p['passed']for p in proofs)
    for p in proofs:
        for f,h in p.get('bindings',{}).items():assert sha(f)==h,f
    old,new=[scoped_load(p)for p in[C.OLD,C.NEW]];raw,newraw=old['raw'],new['raw'];assert len(raw)==len(newraw)
    coherent=proofs[4]['checks'];whole_smc=coherent['coherent_actual_GameLoops']['cases'];menu_smc=coherent['coherent_actual_menu_life_callers']['calls']
    names=re.findall(r'^NrGate (\w+),',(R/'src/new_roster_dispatch.s').read_text(),re.M)
    allowed=set()
    for n in names:allowed.update(range(location(old,n),location(old,n)+97));assert address(old,n)==address(new,n)
    finish=location(new,'NrTableColdFinish');allowed.update(range(finish,finish+9));assert raw[finish:finish+101]==bytes([255])*101
    diffs=[i for i,(x,y)in enumerate(zip(raw,newraw))if x!=y];assert set(diffs)<=allowed and len(diffs)==1067
    runs=[]
    for i in diffs:
        if not runs or i!=runs[-1][-1]+1:runs.append([i])
        else:runs[-1].append(i)
    delta=[dict(file_offset=v[0],bank=(v[0]-16)//8192,CPU_address=0xa000+(v[0]-16)%8192,old=raw[v[0]:v[-1]+1].hex(),new=newraw[v[0]:v[-1]+1].hex())for v in runs]
    dp=B/'nr_router_compact_exact_byte_diff_v1.json';dp.write_text(json.dumps(dict(parent=sha(C.OLD),candidate=sha(C.NEW),changed=1067,bank124_only=True,ranges=delta),indent=2)+'\n')
    # Retain the ONLY historical source preimage, not a copied source tree.
    pre=R/'src/new_roster_dispatch.s';assert sha(pre)==proofs[0]['source_preimage_sha256']
    back=B/'nr_router_compact_preimage_v1.zip';assert not back.exists()
    with zipfile.ZipFile(back,'x',zipfile.ZIP_DEFLATED)as z:z.writestr('src/new_roster_dispatch.s',pre.read_bytes())
    # NrPrepare belongs to Rogue's distinct private work and stays byteexact.
    a=location(old,'NrPrepare');assert raw[a:a+74]==newraw[a:a+74]
    available=16+124*8192+0xda4;assert newraw[available:available+42]==bytes([255])*42
    report=R/'docs/qa/new-roster-router-compaction-2026-10-28.txt'
    report.write_text('''PRIVATE CURRENT-SEMANTICS ROUTER COMPACTION

Parent immutable f56a0e15. Candidate3d870a98 is actual full-source assembly,
not a binary patch or the earlier byte models. Only1067 ROMbytes change, all
bank124, within eleven original97B NrGate slots and one9B appended finish.
Header/CHR/RAM/allotherbanks exact. Every old public PC stays fixed; only33
real ToIce/ToCity/ToSunny internal branches disappear (three unqualified DBG
name aliases also disappear). No fake aliases, new segment, RAM/service flag,
reserved range or extra A-bank trip. Current20/21/23 semantics alone route
to their original targets.22/24/25/26..28 and ALL other IDs remain exact
legacy fallback; no new menu/family admission. NrAdder/Box not compacted.

Each slot contains80B plus17B unexecutedFF. Actual helper isAD9B..<ADA4.
It stores existing NextBank operand, restores savedY/P and enters genuine
FarCallCommon+3 LDA CurrentBank. CallerA/N/Z are overwritten by that exact
instruction; direct actual target-entry/return comparisons below require
full AXYP, not an A/flag mask. Existing SafecallA preserves incomingA before
Y indexes tables; X untouched. Saved stack peak remains two bytes, actual
target live return stack andSP exact. All five SMC ordered address/value
sequences are checked EXPLICITLY, including their page1 addresses.

Source qualification:180224 genuine complete caller pairs (all256 raw IDs,
all64physical flag combinations,11routes), real target entry+return, full
AXYP/SP/live stack/application RAM/OAM/CHR/banks/final5SMC exact. A separate
180224-pair pass compares the literal ordered5SMC writes through each full
target/caller. This second pass is the authority for ordered5SMC: the first
tool's generic stack filter excludes page1 and thus cannot establish that
sequence itself. Final fields were already compared explicitly; no game or
hardware assertion changed. Consumed stack slots carry originalA versusY;
only dead stack content is excluded, not live stack or SMC.

Corrected coherent-window actualGameLoops198 (current raw/bothmodes/3keys
and current alternates) preserve complete state, ordered nonstack writes
AND ordered5SMC.69 actual menu/life fresh/reset/portrait/colors/status/graphics
callers also compare ordered5SMC explicitly.2244 real
IRQ/lagNMI seams cover reached instructions of every router and sharedfinish,
including partial SafecallA/targetlow/targethigh/NextBank publication. Full
live context, R0..R7, physical/shadow banks and5SMC restore exactly; no mapper
normalization. ISR minimumSP209. RegularNMI/actualPPU/native scheduler is not
claimed by lag-NMI source arenas.

Measured complete-call CPU: visited raw0..19 legacy routes+1..2; direct
Ice/City/Sunny table routes generally+9..18. Actual Ice/City NrInjury reaches
a second router and totals+36/+28. Whole typedGameLoops0..+89; allroute
minimumSP196. These are bounded source costs, not native cadence/FPS or a
lag improvement. Existing ordinary MMC3d444/MMC5f4ffd freshly rebuilt exact.
471 actual ca65 ASM/incbin dependencies are bound; genuine full DBG/LBL/map
and exact changed-byte ranges retained. No copied source/runtime tree.

Retained preparation facts: first symbol check classified three unqualified
DBG To* aliases incorrectly; corrected by exact removed-label list with no
runtime aliases. One slow CPU-only matrix was stopped after its first16384
gate comparisons and retained as incomplete, then rerun with byteexact
fast state copying;48 oracle comparisons establish identical exclusions/order.
Earlier readonly89/80B model reports stay unchanged, separate from this proof.
The earlier direct-caller fixture incorrectly set CurrentBank to LOW126 for
GameLoop/GetPlayerColors while A hardware remained87. Its affected whole-LOW
caller claims are WITHDRAWN. Coherent-callers-v2 uses the established real
window-aware runner, preserving existing A shadow215/physical87 for LOW entry,
and proves coherence at entry/return. All180224 NrGate pairs and2244 ISR seams
start in A124 and are unaffected by this fixture correction. Final whole198
GameLoop/69menu evidence comes only from the coherent v2 proof.

Composition: frozen Rogue42B helper also startsAD9B, so these original
standalone packets cannot simply overlay. ROOT/z2 agreed next private union
can rehome ONLY Rogue's helper toADA4..<ADCE (verified42FF), keeping AE00 AUX
and public NrPrepare fixed. This router leaves NrPrepare74B byteexact; future
union needs fresh real source/link/control binding, not retagged proofs.

Install only after ROOT review: apply normalized nr_router_compact_v1.patch
to new_roster_dispatch.s preserving canonical newline format, or use the exact
private leaf for independent reconstruction. No other source required except
unchanged cfg staging. Standard expanded rebuild must reproduce3d870a98;
future Rogue composition must merge its separate change and rehome explicitly.
No source adoption, installed ROM/Downloads/settings writes or Mesen launch.
''',encoding='utf-8')
    files=set(Path(p)for p in proofs[0]['actual_ASM_dependencies'])
    files.update(Path(f)for p in proofs for f in p.get('bindings',{}))
    files.update(inputs+[dp,back,report,Path(__file__),B/'nr_router_compact_v1.patch',B/'nr_router_compact_build_v1.json',B/'nr_router_compact_v1.d',B/'nr_router_compact_matrix_interrupted_v1.json',B/'nr_router_compact_controls_slow_snapshot_v1.py',B/'nr_router_compact_controls_symbol_fixture_negative.py',B/'nr_router_compact_controls_quick_v1.json',B/'nr_router_compact_controls_quick_v2.json',B/'nr_router_compact_controls_quick_fast_v1.json'])
    files.update(B/('nr-router-compact-v1'+suffix)for suffix in['.nes','.dbg','.lbl','.map','.build.json','-mmc3.nes','-mmc3.build.json','-mmc5.nes','-mmc5.build.json'])
    files.update(R/'tools/audit'/n for n in['nr_router_compact_controls_v1.py','nr_router_compact_supplement_v1.py','nr_router_compact_ordered_smc_v1.py','nr_router_compact_coherent_callers_v2.py'])
    files.add(R/'tools/prepare_nr_router_compact_v1.py')
    bindings={str(p.resolve()):sha(p)for p in sorted(files)};assert all(sha(p)==h for p,h in bindings.items())
    rec=dict(passed=True,source_CPU_only=True,native_run=False,parent=str(C.OLD),parent_SHA256=sha(C.OLD),ROM=str(C.NEW),ROM_SHA256=sha(C.NEW),DBG_SHA256=sha(C.NEW.with_suffix('.dbg')),LBL_SHA256=sha(C.NEW.with_suffix('.lbl')),
             source_leaf=str(B/'nr-router-compact-v1-overlay/src/new_roster_dispatch.s'),source_SHA256=sha(B/'nr-router-compact-v1-overlay/src/new_roster_dispatch.s'),report=str(report),report_SHA256=sha(report),exact_byte_diff=str(dp),exact_byte_diff_SHA256=sha(dp),actual_ASM_dependencies=471,proofs={str(p):sha(p)for p in inputs},ordinary=proofs[0]['ordinary'],changed_bytes=1067,bank124_only=True,old_public_PC_RAM_CHR_exact=True,new_helper=[0xad9b,0xada4],gates_97B=11,pergate_unexecuted_slack=17,tail_free=92,
             Rogue_future_composition=dict(NrPrepare_current_exact=True,conflict='Original42B Rogue helper atAD9B overlaps. Rehome it toADA4..<ADCE in a separately qualified future union.',proposed42B_all_FF=True,no_aux_AE00_overlap=True),
             whole_GameLoop_explicit_ordered5SMC_pairs=whole_smc,menu_life_explicit_ordered5SMC_pairs=menu_smc,
             fixture_errata=dict(page1_SMC_order_authority=str(inputs[2]),LOW_caller_bank_authority=str(inputs[4]),old_incoherent_LOW_claims_withdrawn=True,all_gate_entries_A124_and_ISR_seams_unaffected=True),
             owned_files=['tools/prepare_nr_router_compact_v1.py','tools/audit/nr_router_compact_controls_v1.py','tools/audit/nr_router_compact_supplement_v1.py','tools/audit/nr_router_compact_ordered_smc_v1.py','tools/audit/nr_router_compact_coherent_callers_v2.py','tools/prepare_nr_router_compact_handoff_v1.py',str(report.relative_to(R))],bindings=bindings)
    H.write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(dict(handoff=str(H),SHA256=sha(H),bindings=len(bindings),ROM=rec['ROM_SHA256'],source=rec['source_SHA256']),indent=2))

if __name__=='__main__':main()
