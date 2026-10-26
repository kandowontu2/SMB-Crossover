"""Freeze source-built TMNT sweep proposal and honest CPU/native boundaries."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import zipfile
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,CURRENT,sha

PARENT='9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'
DIGEST='64504f58b7fee3382f9c661e0274c20f5ebdcb8ef0da8d59aae0fcc751629c5d'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['storage','experiment','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();d,s,out=a.experiment,a.storage,a.output
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    donor=s/'parser-ready-v1';v5=d.parent/'tmnt-sweep-fast-v5'
    assert sha(d/'candidate.nes')==sha(v5/'candidate.nes')==DIGEST and sha(donor/'candidate.nes')==PARENT
    proofs={}
    for label,path in {'math':v5/'cpu-full-v2/proof.json','outer37':v5/'outer-v1/proof.json',
                       'hot403':v5/'hot-cue403-v1/proof.json','hot404':v5/'hot-cue404-v1/proof.json','hot405':v5/'hot-cue405-v1/proof.json',
                       'edges':d/'edges-v1/proof.json','IRQ':d/'irq-v2/proof.json','songs':d/'songs-v1/proof.json',
                       'cues':d/'cues-v1/proof.json','builds':d/'build-controls-v1/proof.json'}.items():
        q=json.loads(path.read_text());assert q['passed']and q['candidate_ROM_sha256']==DIGEST
        proofs[label]=dict(path=str(path),sha256=sha(path),candidate_ROM_sha256=DIGEST)
    assert json.loads((v5/'cpu-full-v2/proof.json').read_text())['math_cases']==129920
    assert json.loads((d/'songs-v1/proof.json').read_text())['original_calls']==192016
    assert qualified(donor/'candidate.nes').items()<=qualified(d/'candidate.nes').items()
    assert qualified(v5/'candidate.nes')==qualified(d/'candidate.nes')
    b,c=load(donor/'candidate.nes'),load(d/'candidate.nes');before,after=b['raw'],c['raw']
    deltas={n:[i for i in range(8192)if before[16+n*8192+i]!=after[16+n*8192+i]]for n in range(128)}
    deltas={n:v for n,v in deltas.items()if v};assert {n:len(v)for n,v in deltas.items()}=={29:223,87:491}
    assert before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert before[16+87*8192+0x1500:16+88*8192]==bytes([255])*0xb00
    assert address(c,'GuestExpansionSweepClock')==address(b,'GuestExpansionSweepClock')
    start,end=location(b,'GuestExpansionSweepClock'),location(b,'GuestExpansionSweepTarget')+int(b['syms']['GuestExpansionSweepTarget']['size'],0)
    assert before[start:end]==after[start:end]
    out.mkdir(parents=True);source=out/'source';shutil.copytree(d/'source',source,ignore=shutil.ignore_patterns('__pycache__'))
    paths={p.relative_to(source).as_posix():p for p in source.rglob('*')if p.is_file()}
    allbindings={n:sha(p)for n,p in sorted(paths.items())};(out/'source-bindings.json').write_text(json.dumps(allbindings,indent=2)+'\n')
    manifests={}
    baselines={'9a791':{p.relative_to(donor/'source').as_posix():sha(p)for p in(donor/'source').rglob('*')if p.is_file()},
               '50b5':json.loads((s/'current-baseline-v1/frozen-source.json').read_text())['source_files']}
    for name,old in baselines.items():
        manifest={n:dict(before_sha256=old.get(n),after_sha256=allbindings[n])for n in allbindings if old.get(n)!=allbindings[n]}
        assert not(set(old)-set(allbindings)),('Removed source input',name)
        (out/f'changed-source-versus-{name}.json').write_text(json.dumps(manifest,indent=2)+'\n');manifests[name]=manifest
    assert set(manifests['9a791'])=={'src/mmc5_sfx.s','src/guest_audio.s','src/entrypoint.s','src/tmnt_sweep_fast.s','smb1base-mmc5-expanded.cfg'}
    patch=''
    for n in sorted(manifests['9a791']):
        p=donor/'source'/n
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True)if p.exists()else[],paths[n].read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (out/'review.patch').write_text(patch)
    for ext in['.nes','.lbl','.dbg','.map','.build.json','.cv3-mirror.json']:shutil.copyfile(d/('candidate'+ext),out/('candidate'+ext))
    shutil.copyfile(d/'preparation.json',out/'preparation.json')
    with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED)as z:
        for n,p in sorted(paths.items()):z.write(p,n)
    own=['tmnt_sweep_fast_source_v6.py','tmnt_sweep_fast_cpu_v2.py','tmnt_sweep_fast_outer_v1.py','tmnt_sweep_fast_hot_v1.py',
         'tmnt_sweep_fast_irq_v2.py','tmnt_sweep_fast_edges_v1.py','tmnt_sweep_fast_cues_v1.py','tmnt_sweep_fast_build_controls_v1.py','tmnt_sweep_fast_finalize_v1.py']
    (out/'tools').mkdir();toolbindings={}
    for n in own:
        p=ROOT/'tools/audit'/n;shutil.copyfile(p,out/'tools'/n);toolbindings[n]=sha(p)
    reused=['check_tmnt_render_oa.py','check_tmnt_audio_fallback_oc.py','verify_native_relocation.py','tmnt_native_storage_driver.py',
            'tmnt_native_storage_multiply.py','tmnt_native_storage_owners_cpu.py','tmnt_native_storage_irq_cpu.py','final_item_matrix.py',
            'tmnt_native_storage_multiply_cpu.py','tmnt_native_storage_linked_cpu.py','tmnt_native_storage_cpu.py']
    (out/'reused-checkers.json').write_text(json.dumps({n:sha(ROOT/'tools/audit'/n)for n in reused},indent=2)+'\n')
    # Extra status read is not claimed equivalent for arbitrary external APU
    # IRQ state. Bind cold-reset inhibit and complete original source schedule;
    # the later native qualifier still must observe the real hardware schedule.
    reset=source/'src/reset.s';text=reset.read_text()
    assert 'ldx #$ff' in text and 'stx APU_FRAMECOUNTER' in text
    start=location(c,'Start');assert bytes([0xa2,255,0x8e,0x17,0x40])in after[start:start+32]
    # Both real original-source golden streams and the exact preserved driver
    # establish no native4017 writes in this source workload.
    from tmnt_native_storage_driver import OB
    import gzip
    coverage=json.loads((OB/'probe-v2/coverage.json').read_text());frame_requests=0
    for song in coverage['songs']:
        for row in json.loads(gzip.decompress((OB/f'probe-v2/song-{int(song):02d}.json.gz').read_bytes())):
            frame_requests+=sum(reg==0x4017 for reg,v in row['writes'])
    assert frame_requests==0
    contracts=dict(cold_Reset_APU_frame_IRQ_inhibit_value=255,reset_source_sha256=sha(reset),
                   original16song_APU4017_requests=0,extra_owner0_4015_read_explicit=True,
                   arbitrary_external_frame_IRQ_state_not_qualified=True,
                   no_native_hardware_or_nested_NMI_claim=True,proofs=proofs)
    (out/'qualification.json').write_text(json.dumps(contracts,indent=2)+'\n')
    cost=json.loads((d/'cues-v1/proof.json').read_text())
    report=f'''TMNT SHARED-SWEEP / OUTER: PRIVATE SOURCE-ONLY IMPLEMENTATION
2026-10-25. No optimization native grant/run, production/Git/Downloads change.
Accepted production parent: {CURRENT}
Frozen parser donor: {PARENT}
New exact private ROM: {DIGEST}
Only223bytes in29 and491bytes in87 change. All other126banks/header/CHR,
all original native16songs/samples/driver/writers and every old genuine label
remain exact. Source658-plus-helper manifest and full archive are bound here.

Five source edits versus parser donor: guest_audio.s, mmc5_sfx.s, entrypoint.s,
new tmnt_sweep_fast.s and MMC5 expanded linker config. The linker splits only
87's genuine unused tail at physicalB500 into a real C-windowD500 run memory;
its first1500hex bytes retain all original positions and preserve reserved
rendererB020 and ammoB100..B4FF space. No E-mirror/LOW/fixed pad is consumed.
The new491-byte C87 body has a real entry, never a fake old symbol alias.

The shared original expansion output groups each channel's repeated mask test,
preserving ascending APU stores/dirty/change predicates/finalAXYP. It frees an
actual28-byte span after its realRTS, used by TnExpansionSweepCall. The public
371-byte flush, original Clock/Output entry PCs and Clock/Target bytes remain
genuine and fixed. New38-byte gate occupies originalFF A29BFDA..BFFF.
Only char19 +pulse1 +owner4(E-only original129-byte drum) or idleowner0 with
physicalDMCinactive may mapC87. Other owners and unowned active samples use
the original public function. The helper changes no SMC or borrowed RAM and
restores old C hardware/shadow and exact outer final A/X8/Y1/P via liveCPX8.

New guarded99 math requires dirty1/2/3zero, divider/reload0, unsigned period
18..2047 (UPPER BYTE<8). It preserves original two halfclock results, timer,
delta, flags and ordered sound writes; other inputs use literal original
Clock/Target calls. Original intermediate private scratch/tick stores differ,
but no IRQ reader observes them and complete final state remains exact.
ERRATUM to immutable old lead:129920cases are18..2047 x64physicalP contexts,
the bounded11-bit timer range, NOT the entire13-bit unsigned domain.

GuestAudioBegin additionally skips the first redundant non-Bass reset for
added characters; the real cached-character compare kills incoming C/N/Z,
and source reset/second real BassAudioBegin preserve all fields/final flags.
Its added-character tail uses JMP instead of JSR/RTS with the same4-byte span.
30720complete entry cases prove20IDs/64flags/4caches/6owners. No source ticks,
music channels, APU stores, pause updates, effects, sprites or pickups removed.

SOURCE/CPU COVERAGE on this exact ROM (v5 andv6 canonical bytes identical):
129920guarded math,5740fallback,17920physicalstatus,1280complete mixer cases;
3632outside-domain edges;30720complete queue-entry cases;12256full37identity
outer calls;554real compiled IRQ injections (max10stackbytes);3x506fullcalls
with actual188-byte native source-state binding and disclosed before-call
shared-cue/status inputs. Fresh192016original16song calls,549602ordered APU
requests and1099204writer returns pass exact ABI/state/foreground/ZP/banks.
Native music core costs are unchanged. Fresh canonical and ordinary flag-off
MMC3 d444cac8 /MMC5 f4ffd248 builds are byte-exact expected outputs.

Measured paired source AudioUpdate active-cue404/405 tick407:5736->5311,
425cycles saved INCLUDING mapper/helper/outer routing. Tick505 saves66.
The410-cycle reconstructed strict publication target is exceeded only in
this disclosed CPU mixer: historical capture did NOT save full mixer RAM.
Cue403 has already released pulse1 by407 and saves66 there. All3x506calls
improve14..425. No recovered draw, native deadline or universal no-harm claim.
Raw guarded fallback can add up96cycles; complete mixer component up65.
Additional2080full effect/retrigger callers preserve all outputs but expose
{cost['regression_calls']}small source cost regressions:18calls+1 and1call+6;
others save7..425. These negatives remain in the bound cues proof.

Extra owner0 physical4015 read is explicit: it can acknowledge frameIRQ in
arbitrary external APU states. Legal cold-reset source usesFF frameIRQinhibit;
all original16song captures contain no4017requests. Real hardware/frameIRQ,
DMC DMA/read timing/NMI/publication/OAM/CHR and unchanged600-update cadence
still require a new separately granted STATIC-observer native qualification.
The already qualified static observer retained old9a791's566draw negative;
it is not a native run of this optimization. No native worker is held.

Retained trials: v1 long-branch assembly error;v2 wrong linker segment ordering
overflow;v3/v4 preliminary positive source ROMs;v5 ordinaryMMC5 build exposed
missing conditional Output label. v6 fixes only that inactive source branch,
same canonical64504f58 bytes. Initial v5 songs harness lacked standalone_source
metadata (KeyError before source execution); v6 inherits bound donor metadata
and fresh complete original proof passes. No oracle was relaxed for failures.
No Parodius work/composition or adoption is included in this finite packet.
'''
    (out/'report.txt').write_text(report)
    doc=ROOT/'docs/qa/tmnt-sweep-fast-source-2026-10-25.txt';doc.write_text(report+'\nFrozen external packet: '+str(out)+'\n')
    receipt=dict(frozen=True,accepted=False,source_CPU_only=True,native_run=False,production_changes=False,
                 accepted_parent_ROM_sha256=CURRENT,donor_ROM_sha256=PARENT,candidate_ROM_sha256=DIGEST,
                 all_existing_qualified_symbols=len(qualified(donor/'candidate.nes')),source_files=len(paths),
                 changed_ROM_bytes={n:len(v)for n,v in deltas.items()},proofs=proofs,source_changes=manifests,
                 tools=toolbindings,source_archive_sha256=sha(out/'source.zip'),source_bindings_sha256=sha(out/'source-bindings.json'),
                 report_sha256=sha(doc),checker_sha256=sha(Path(__file__)),native_cadence_still_open=True,
                 complete_cue_cost_regressions=19,maximum_cue_added_cycles=6)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(frozen=True,receipt_sha256=sha(out/'receipt.json'),ROM_sha256=DIGEST,source_files=len(paths),report_sha256=sha(doc))))


if __name__=='__main__':main()
