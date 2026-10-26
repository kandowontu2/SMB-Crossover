"""Verify the frozen turtle source refinements and preserve the native lag hold."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT=ROOT/'docs/qa/checkpoints/2026-10-26/tmnt-parser-source-held'
PACKETS={
 'tmnt-sweep-composed-live-math-ready-v4':'27cde20ed7133a1bbddaf386453d9a756f227911320144f9adc7b4b94824ff3b',
 'tmnt-sweep-composed-native-negative-v1':'5c2064f59b7b2eaa0c37eeac50399dc97cff1bae94bf40b8c2bf0f3dfe2ccc7e',
 'tmnt-secondary-followup-ready-v1':'4a495015bd4f85d66337d861c776ca41acf0626b9eb6f1e0f3ba5340f8a9a06f',
 'tmnt-parser-math-next-ready-v1':'d756269ef8c3bc48e00737a71fa405b6878b616fdf65e0273556d0ff5f25bc64',
 'tmnt-parser-channels-ready-v1':'ba14ba40766b60f038a6de8782c0a088a4267c62c6b8a5c474b670a3aa8b1686',
 'tmnt-parser-unrolled-ready-v1':'b5342ee2b9ced30f296ea5accdfa4165d53bf1eaf0b50c6c1d633dc0b4f4e889',
 'tmnt-parser-tail-writers-ready-v1':'e7d765a47905533a28854507e2c7d5087d15c6a56a22a2b0fe0fa0fa4fd87fd3',
}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists();OUT.mkdir(parents=True)
    catalog={};counts={};tool_hashes={};extra_verified={}

    def copy(p,name):
        p=Path(p);q=OUT/name;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,q);assert sha(q)==sha(p)
        catalog[name]=dict(source=str(p),sha256=sha(p))

    def records(v):
        if isinstance(v,dict):
            if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str):
                p=Path(v['path']);assert sha(p)==v['sha256'],p
                extra_verified[str(p)]=v['sha256']
            for k,x in v.items():
                if isinstance(x,str)and len(x)==64 and Path(k).is_absolute():
                    assert sha(k)==x,k;extra_verified[k]=x
                else:records(x)
        elif isinstance(v,list):
            for x in v:records(x)

    for name,expected in PACKETS.items():
        p=D/name;assert sha(p/'receipt.json')==expected
        j=json.loads((p/'receipt.json').read_text());records(j)
        for tool,digest in j.get('tools',{}).items():
            file=Path(tool)if Path(tool).is_absolute()else ROOT/'tools/audit'/tool
            assert sha(file)==digest,file
            if str(file)in tool_hashes:assert tool_hashes[str(file)]==digest
            tool_hashes[str(file)]=digest
        if (p/'source.zip').exists():
            assert sha(p/'source.zip')==j['source_archive_sha256']
            assert sha(p/'source-bindings.json')==j['source_bindings_sha256']
            bindings=json.loads((p/'source-bindings.json').read_text())
            with zipfile.ZipFile(p/'source.zip')as z:
                assert set(z.namelist())==set(bindings)
                for n,h in bindings.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
            counts[name]=len(bindings)
        for f in p.iterdir():
            if f.suffix in ['.json','.patch','.txt']and f.name!='settings.json':
                copy(f,'packets/'+name+'/'+f.name)
        for title,record in j.get('proofs',{}).items():
            copy(record['path'],'source-proofs/'+name+'/'+title+'.json')
    last=D/'tmnt-parser-tail-writers-ready-v1'
    changed=json.loads((last/'changed-source-versus-50b5.json').read_text())
    with zipfile.ZipFile(last/'source.zip')as z:
        for n,record in changed.items():
            raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==record['after_sha256']
            assert Path(n).suffix not in ['.nes','.nsf','.dll','.dbg','.lbl','.map']
            q=OUT/'changed-source'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
            catalog['changed-source/'+n]=dict(source='source.zip:'+n,sha256=sha(q))
    for p,digest in tool_hashes.items():copy(p,'frozen-tools/'+Path(p).name)
    for name in ['tmnt-deadline-acceptance-erratum-v1','tmnt-parser-helper-size-erratum-v1']:
        for f in (D/name).iterdir():
            if f.suffix in ['.json','.txt']:copy(f,'errata/'+name+'/'+f.name)
    for name in ['tmnt_sweep_hardware_epochs_v1.py','tmnt_publication_acceptance_erratum_v1.py']:
        if str(ROOT/'tools/audit'/name)not in tool_hashes:copy(ROOT/'tools/audit'/name,'frozen-tools/'+name)
    for p,h in extra_verified.items():
        f=Path(p)
        if f.name=='proof.json'and not f.is_relative_to(ROOT):
            copy(f,'verified-extra-proofs/'+f.parent.name+'-'+h[:12]+'.json')
    reports=['tmnt-sweep-composed-live-math-2026-10-25.txt','tmnt-sweep-composed-native-2026-10-25.txt',
             'tmnt-secondary-followup-2026-10-25.txt','tmnt-parser-math-next-2026-10-26.txt',
             'tmnt-parser-channels-2026-10-26.txt','tmnt-parser-unrolled-2026-10-26.txt',
             'tmnt-parser-tail-writers-2026-10-26.txt','tmnt-parser-helper-size-erratum-2026-10-26.txt',
             'tmnt-publication-deadline-erratum-2026-10-25.txt']
    for name in reports:copy(ROOT/'docs/qa'/name,'reports/'+name)
    review=dict(accepted=False,production_adopted=False,performance_gate_passed=False,
                root_verified_complete_source_archive_members=counts,
                root_verified_extra_artifact_bindings=len(extra_verified),
                final_changed_production_sources=len(changed),
                actual_native_5373_secondary_extra_missed_draws=4,
                actual_first508_complete_DMA_images_and_PPU_epochs_exact=True,
                source_only_extra_hot533_saving=317,remaining_about418_is_model_only=True,
                no_native_followup_of_parser_refinements=True,copied_bindings=catalog)
    (OUT/'root-review.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUT),members=counts,copied=len(catalog),verified_extra=len(extra_verified))))


if __name__=='__main__':main()
