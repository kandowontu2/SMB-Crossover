"""Freeze the page-safe Ice aliases and bounded native A/B evidence."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/ice-pose-aliases-v2'
D=R/'docs/qa/checkpoints/2026-10-30/ice-pose-aliases'
sys.path.insert(0,str(R/'tools/audit'))
from verify_parodius_chr_compact_native_v1 import frames


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    bp=O/'build-proof.json';cp=O/'controls.json'
    build=json.loads(bp.read_text());controls=json.loads(cp.read_text())
    assert build['passed']and controls['passed']
    assert build['ROM_sha256']==controls['ROM_sha256']==sha(O/'candidate.nes')
    assert build['saved_PRG_bytes']==721 and controls['cases']==2160
    parent=R/'docs/qa/checkpoints/2026-10-30/parodius-dense-chr/root-review-and-reservations.json'
    prior=json.loads(parent.read_text());bindings=dict(prior['runtime_references'])
    bindings.update(build['source_bindings']);bindings.update(controls['source_bindings'])
    rows=[];total=0
    for variant in [0,1]:
        paths=[O/'native'/f'{role}-jump-then-hammer-v{variant}'for role in ['parent','aliased']]
        results=[json.loads((p/'result.json').read_text())for p in paths]
        for p,data,expected in zip(paths,results,[build['parent_ROM_sha256'],build['ROM_sha256']]):
            binding=json.loads((p/'binding.json').read_text())
            budget=json.loads((p/'capture-budget.json').read_text())
            assert binding['exit_code']==0 and data['passed']and data['ROM_sha256']==expected
            assert binding['controller_sha256']==sha(p/'controller.lua')
            assert binding['driver_sha256']==sha(R/'tools/audit/ice_pose_aliases_native_v1.py')
            assert binding['no_native_RAM_writes']and binding['normal_sprite_limit']
            assert budget['workspace_byte_cap']==70000000000 and budget['run_file_cap']==64
            assert data['jumped']and data['landed']and data['walked']==111 and data['rise']==67
            for f in p.iterdir():
                if f.is_file():bindings[str(f)]=sha(f)
        normalized=[{k:v for k,v in d.items()if k!='ROM_sha256'}for d in results]
        assert normalized[0]==normalized[1]
        for name in ['screens.bin','trace.csv','main-cycles.csv']:
            assert (paths[0]/name).read_bytes()==(paths[1]/name).read_bytes(),(variant,name)
        sequence=frames((paths[1]/'screens.bin').read_bytes())
        assert len(sequence)==results[1]['captured_screens']
        total+=len(sequence)
        rows.append(dict(character='Nana'if variant else'Popo',state=normalized[1],
                         exact_screen_pairs=len(sequence),screens_sha256=sha(paths[1]/'screens.bin')))
    assert total==1333
    # Preserve the rejected attack-before-jump fixture, without counting it as
    # a successful gameplay test. Only controller ordering changed afterwards.
    neg=[O/'native'/f'{role}-v0'for role in ['parent','aliased']]
    nr=[json.loads((p/'result.json').read_text())for p in neg]
    assert all(not d['passed']and not d['jumped']and d['walked']==6 for d in nr)
    assert (neg[0]/'screens.bin').read_bytes()==(neg[1]/'screens.bin').read_bytes()
    assert len(frames((neg[0]/'screens.bin').read_bytes()))==656
    for p in neg:
        for f in p.iterdir():
            if f.is_file():bindings[str(f)]=sha(f)
    for p in [bp,cp,parent,Path(__file__).resolve(),
              R/'tools/audit/ice_pose_aliases_native_v1.py',
              R/'tools/audit/verify_parodius_chr_compact_native_v1.py',
              O/'negative-controller-order.json',O/'negative-attack-controller-driver.py']:
        bindings[str(p)]=sha(p)
    for path,h in bindings.items():assert sha(path)==h,path
    D.mkdir(parents=True)
    archive=D/'frozen-source-and-native-evidence.zip';members={}
    exclude={'.nes','.dbg','.lbl','.map','.exe','.dll','.o','.zip','.mp4','.wav','.bin','.nesppuv1'}
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path,h in bindings.items():
            p=Path(path).resolve()
            # Binary source assets remain bound by the parent source packet;
            # the large six local screen streams stay in their bounded runs.
            if not p.is_relative_to(R)or p.suffix.lower()in exclude:continue
            name=p.relative_to(R).as_posix()
            zi=zipfile.ZipInfo(name,(2026,10,30,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,p.read_bytes());members[name]=h
    with zipfile.ZipFile(archive)as z:
        assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
    report=dict(passed=True,status='SOURCE_CPU_AND_NATIVE_ICE_ALIAS_EQUIVALENCE',
        ROM_sha256=build['ROM_sha256'],parent_ROM_sha256=build['parent_ROM_sha256'],
        saved_PRG_bytes=721,physical_bank=70,offset_start=0x58f,end_exclusive=0x860,
        native_serial_positive_runs=4,exact_native_screen_pairs=total,native_rows=rows,
        controls={k:v for k,v in controls.items()if k not in ['rows','source_bindings']},
        rejected_controller_pair=dict(runs=2,exact_screen_pairs=656,
            reason='Ground hammer locks movement for19updates. Initial controller attacked before its jump; corrected fixture jumps first. Engine unchanged.'),
        unchanged_all_CHR_and_runtime_instructions=True,no_added_RAM=True,
        source_closure=dict(parent_checkpoint=str(parent),parent_sha256=sha(parent),verified_bindings=len(bindings)),
        archive=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size,members=len(members)),
        members=members,runtime_references=bindings,lossless_streams_retained=True,
        shared_installation=False,
        limitations=['Native selection/lives/walking/jump/hammer equivalence only; no new1-1 or every-powerup pass.',
                     'Existing2lagframes per300updates unchanged, not a lag fix.',
                     'Arthur grant requires exact Ice aliases/wrapper; never restore original60-record producer over the freed interval.',
                     'Four-host parent performance qualification still pending before shared installation.'])
    (D/'root-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,positive_screen_pairs=total,source_members=len(members),archive_bytes=archive.stat().st_size)))


if __name__=='__main__':main()
