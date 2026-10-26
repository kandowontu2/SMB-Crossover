"""Freeze a bounded private renderer optimization and all source-only limits."""
from pathlib import Path
from collections import Counter
import argparse
import csv
import difflib
import json
import shutil
import subprocess
import sys
import zipfile
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,CURRENT,sha


PARENT='9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'
DIGEST='eedf07f7c63f2a2ad286d389a2bfe855dafdd0529bc09f1588476ac5f70c0d47'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['experiment','storage','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();d,s,out=a.experiment,a.storage,a.output
    assert not out.exists() and not out.resolve().is_relative_to(ROOT)
    donor=s/'parser-ready-v1';candidate=d/'current-9a791-v3'
    assert sha(donor/'candidate.nes')==PARENT and sha(candidate/'candidate.nes')==DIGEST
    assert sha(ROOT/'build/smb-crossover-mmc5-expanded.nes')==CURRENT
    proofs={}
    for label in ['cpu-v1','irq-tail-v1','audio-outer-v1']:
        path=d/label/'proof.json';q=json.loads(path.read_text())
        assert q['passed'] and q['candidate_ROM_sha256']==DIGEST and q['baseline_ROM_sha256']==PARENT
        proofs[label]=dict(path=str(path),sha256=sha(path))
    assert json.loads((d/'cpu-v1/proof.json').read_text())['cases']==5262
    assert json.loads((d/'irq-tail-v1/proof.json').read_text())['actual_compiled_IRQ_injections']==68
    assert json.loads((d/'audio-outer-v1/proof.json').read_text())['total_calls']==12256
    before,after=(donor/'candidate.nes').read_bytes(),(candidate/'candidate.nes').read_bytes()
    changes={n:[i for i in range(8192) if before[16+n*8192+i]!=after[16+n*8192+i]] for n in range(128)}
    changes={n:v for n,v in changes.items() if v}
    assert set(changes)=={87} and len(changes[87])==61
    assert set(changes[87]) <= set(range(0xad0,0xad6))|set(range(0x1020,0x1058))
    assert before[16+87*8192+0x1020:16+88*8192]==bytes([255])*(8192-0x1020)
    assert before[:16]==after[:16] and before[1048592:]==after[1048592:]
    assert qualified(donor/'candidate.nes').items()<=qualified(candidate/'candidate.nes').items()
    out.mkdir(parents=True)
    source=out/'source';shutil.copytree(candidate/'source',source,ignore=shutil.ignore_patterns('__pycache__'))
    paths={p.relative_to(source).as_posix():p for p in source.rglob('*') if p.is_file()}
    frozen=json.loads((s/'current-baseline-v1/frozen-source.json').read_text())['source_files']
    manifests={}
    for key,lookup in [('9a791',{p.relative_to(donor/'source').as_posix():sha(p) for p in (donor/'source').rglob('*') if p.is_file()}),('50b5',frozen)]:
        m={n:dict(before_sha256=lookup.get(n),after_sha256=sha(p)) for n,p in paths.items() if lookup.get(n)!=sha(p)}
        manifests[key]=m;(out/('changed-source-versus-'+key+'.json')).write_text(json.dumps(m,indent=2)+'\n')
    assert len(paths)==659 and set(manifests['9a791'])=={'src/entrypoint.s','src/tmnt_equipment_draw.s','src/tmnt_empty_equipment_scans.s'}
    patch=''
    for name in sorted(manifests['9a791']):
        p=donor/'source'/name
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True) if p.exists() else [],paths[name].read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (out/'review.patch').write_text(patch)
    (out/'source-bindings.json').write_text(json.dumps({n:sha(p) for n,p in sorted(paths.items())},indent=2)+'\n')
    for ext in ['.nes','.dbg','.map','.lbl','.build.json','.cv3-mirror.json']:
        shutil.copyfile(candidate/('candidate'+ext),out/('candidate'+ext))
    for name in ['preparation.json','scan-preparation.json']:shutil.copyfile(candidate/name,out/name)
    builds={}
    for name,flag,expected in [('roundtrip',None,DIGEST),('flagoff-mmc3','mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('flagoff-mmc5','mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        command=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/(name+'.nes'))]
        if flag:command+=['--flag-off',flag]
        r=subprocess.run(command,cwd=source,capture_output=True,text=True)
        (out/(name+'-build.log')).write_text(r.stdout+r.stderr)
        assert r.returncode==0 and sha(out/(name+'.nes'))==expected,(name,r.stdout[-2000:],r.stderr[-2000:])
        builds[name]=expected;print(name,expected,flush=True)
    with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,p in sorted(paths.items()):archive.write(p,name)
    tools={};(out/'tools').mkdir()
    for name in ['tmnt_equipment_empty_scans_v3.py','tmnt_equipment_empty_scans_cpu_v1.py','tmnt_equipment_empty_scans_irq_v1.py','tmnt_equipment_empty_scans_finalize_v2.py']:
        p=ROOT/'tools/audit'/name;shutil.copyfile(p,out/'tools'/name);tools[name]=sha(p)
    reused=['check_tmnt_render_oa.py','check_tmnt_audio_fallback_oc.py','verify_native_relocation.py','tmnt_native_storage_driver.py',
            'tmnt_native_storage_multiply_outer.py','tmnt_native_storage_multiply.py','tmnt_native_storage_owners_cpu.py','tmnt_native_storage_irq_cpu.py','final_item_matrix.py']
    (out/'reused-checkers.json').write_text(json.dumps({n:sha(ROOT/'tools/audit'/n) for n in reused},indent=2)+'\n')
    # Frozen observer reliability audit. These are historical immutable scripts;
    # no Mesen launch, callback edit, pass substitution or verdict relabeling.
    native=s/'parser-native-pilot-v1/candidate-easy'
    observer={}
    for name in ['run.lua','performance-observer.lua']:
        p=native/name;lines=p.read_text().splitlines()
        markers=['if not installed[key]then','if not returnHooks[key]then','if not instructionHooks[key]then','if not returns[pc]then']
        sites=[dict(line=i+1,text=line.strip()) for i,line in enumerate(lines) if any(q in line for q in markers)]
        assert len(sites)==(4 if name=='run.lua' else 1)
        observer[name]=dict(path=str(p),sha256=sha(p),runtime_registration_guards=sites)
    reliability=dict(frozen_observers=observer,runtime_registration_present=True,old_native_negative_unchanged=True,
        future_native_requires_startup_static_dispatcher_and_independent_trace_equivalence=True,
        limits='Historical scripts register DMA completion, source/function returns and post-DMC-STA callbacks inside running callbacks. This overlaps the known Mesen host vector-growth risk. Existing completed timing negatives remain retained; this audit does not establish a host failure or change any ROM verdict.')
    (out/'observer-reliability.json').write_text(json.dumps(reliability,indent=2)+'\n')
    rows=list(csv.DictReader((native/'tmnt-performance-calls.csv').open()))
    projection={}
    for phase in ['idle','walk','enemies','primary','secondary']:
        rr=[r for r in rows if r['name']=='TnDrawEquipment' and r['phase']==phase]
        counts=Counter(int(r['enemies']) for r in rr)
        projection[phase]=dict(recorded_equipment_calls=len(rr),recorded_enemy_counts=dict(counts),
            reconstructed_saved_CPUcycles=sum(140+25*int(r['enemies']) for r in rr) if phase=='secondary' else 0)
    assert projection['secondary']['reconstructed_saved_CPUcycles']==15855
    (out/'phase-source-cost-projection.json').write_text(json.dumps(dict(phases=projection,
        measured_new_native=False,assumptions='Same captured invocations; both groups empty, gear selected only in secondary, active enemies retain ordinary first-ID rejection. This is source-cost reconstruction from captured counts, not literal RAM replay or a new native cadence measurement.',
        source_fixture_sha256=sha(native/'performance-fixture.lua'),captured_calls_sha256=sha(native/'tmnt-performance-calls.csv')),indent=2)+'\n')
    report=f'''TMNT EMPTY RENDER SCANS: PRIVATE SOURCE/CPU ONLY
2026-10-25. No native launch/grant, production, Git or Downloads change.
Accepted production {CURRENT}
Frozen parser donor {PARENT}
New private candidate {DIGEST}

Three changed/new source files versus donor: entrypoint.s appends an MMC5-only
include after every old TMNT_CORE contributor, tmnt_equipment_draw.s replaces
the genuine six-byte NextShot entry with JMP/three NOPs and names two actual
resume instructions, and tmnt_empty_equipment_scans.s adds the real56-byte
helper at bank87 B020..B057. All old qualified labels remain true live entries
and exact PCs; no fake aliases. No new RAM, foreground hardware math or audio
changes. Only61 ROM bytes in bank87 differ. Other127banks, complete CHR,
header, all music/sample/dispatch bytes and copied SMC code remain exact.
659-file archive; fresh canonical rebuild and both flag-off builds exact.

The helper reproduces LDX/DEX/loop branch. Only after the last shot, all four
drop-kind flags and all six private pickup stamps must be zero to skip both
loops. Every nonzero path resumes original LDX3 and unchanged loop bodies.
Final DrawSlot0/XFF and all original icon/ammo behavior are retained. Icon-tail
A/C/N/Z may differ because they are dead before actual LDA/CMP/CLC;384 cases
prove live X/Y/V/D/I/SP/scratch/ordinary RAM/banks exact there and complete final
ABI exact. This is explicit liveness, not weakened final-state equality.

5,262 complete renderer CPU cases pass exact final A/X/Y/P/SP, all ordinary
RAM and SMC bytes, PRG banks, ordered OAM/hardware/CHR publications; only upper
discarded stack01A0..01FF differs. Includes168 world entries/both facings,
clipping/OAM rotation/overload,1,024 actual caller/farcall cases with all64flag
contexts, every drop slot, private owner/stamp/state controls and HUD queues.
68 real compiled IRQ injections at every reached helper instruction preserve
interrupted state and final draw; IRQ-owned hardware cells are explicitly
listed, no emulated state is restored. No real PPU/NMI/DMA claim.
12,256 full audio calls over37identities and all four turtle variants pass
with exact outcomes and zero cycle changes, including ordinary/SMC/APU/banks.

Measured arranged CPU savings: empty groups with0/2/6ordinary enemies save
140/190/290cycles per reached draw. Populated drop paths cost+36cycles; stamp-
only populated paths cost+62. Original scan counts and visible work stay exact.
Recorded9a secondary's87draw invocations imply15,855cycles saved in source
reconstruction (60with2enemies,27with1). No primary saving: its renderer's
existing broad empty-admission gate bypasses this hook. This does NOT close
the primary miss, six native lost draws, or establish recovered native draws.

Both initial private builds retained: v1 included helper too early; v2 fixed
contributor order but incorrectly expanded old jpl2B into5B. Strict B020 linker
assertions stopped both. No candidate fixture or oracle weakening used them.

Observer reliability: historical run.lua dynamically registers DMA/source-return/
component-return/post-DMC-STA callbacks; performance-observer.lua registers
returns dynamically too. Exact hashes/sites are bound separately. Future native
work needs a startup static dispatcher with independent trace equivalence before
any launch. Frozen completed native negatives and all old receipts stay intact.
No ammo-HUD optimization, song/rate/channel/sample removal, Parodius change,
campaign/native/audio acceptance or whole-goal completion is claimed.
'''
    (out/'report.txt').write_text(report)
    receipt=dict(ready=True,accepted=False,source_only=True,native_run=False,production_parent_ROM_sha256=CURRENT,
        donor_ROM_sha256=PARENT,candidate_ROM_sha256=DIGEST,changed_PRG_bytes={87:61},source_files=len(paths),
        source_changes_versus_donor=manifests['9a791'],source_changes_versus_production=len(manifests['50b5']),
        canonical_and_flagoff=builds,proofs=proofs,tools=tools,source_archive_sha256=sha(out/'source.zip'),
        report_sha256=sha(out/'report.txt'),observer_reliability_sha256=sha(out/'observer-reliability.json'),
        projection_sha256=sha(out/'phase-source-cost-projection.json'),original_native_negative_preserved=True,
        primary_native_miss_still_open=True,populated_path_regressions_cycles=[36,62])
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(ready=True,accepted=False,native_run=False,candidate=DIGEST,receipt_sha256=sha(out/'receipt.json'))))


if __name__=='__main__':main()
