"""Prune superseded generated output after verifying a compact source recovery ZIP."""
from pathlib import Path
import argparse
from functools import lru_cache
import hashlib
import json
import os
import stat
import zipfile

ROOT=Path(__file__).resolve().parents[2]
BUILD=(ROOT/'build').resolve()
REPORT=ROOT/'docs/qa/workspace-cleanup-2026-10-31'
RECOVERY=BUILD/'_recovery/legacy-sources-2026-10-31.zip'
ROOTS=[
 ROOT/'docs/qa/checkpoints/2026-10-31/contra-force-projectile-contact-source-v1/handoff.json',
 BUILD/'smb2j-cache-loader-source-1031-v3/source-stage.json',
 BUILD/'thomas-natural-host-1031-v6/source-stage.json',
 BUILD/'wwf-hogan-natural-source-v15/source-stage.json',
 ROOT/'docs/qa/checkpoints/2026-10-31/doki-original-physics-source-v1/handoff.json',
]
ACTIVE=[
 'contra-force-projectile-contact-1031-v3','smb2j-cache-loader-source-1031-v3',
 'thomas-natural-host-1031-v6','wwf-hogan-natural-source-v15',
 'smb2j-original-source-1031-v1','smbann-original-source-1031-v1',
 'doki-original-rebuild-1031-v1','thomas-original-camera-trace-1031-v1',
 'thomas-progression-analysis-1031-v2',
]
SOURCE_EXT={'.s','.asm','.inc','.cfg','.py','.lua','.json','.md','.txt',
            '.chr','.pal','.yaml','.yml','.toml','.c','.h','.bat','.ps1','.sh',
            '.patch','.diff','.xml','.html','.css','.js'}
sha=lambda data:hashlib.sha256(data).hexdigest()
LINKS=set()
ARCHIVE_DEBUG=set()


@lru_cache(maxsize=None)
def checked_parent(p):
    resolved=p.resolve()
    assert resolved==p and (resolved==BUILD or resolved.is_relative_to(BUILD)),p
    return resolved


def checked(p):
    p=Path(p)
    assert p.is_absolute() and p.is_relative_to(BUILD) and p!=BUILD,p
    checked_parent(p.parent)
    st=p.stat(follow_symlinks=False)
    assert not stat.S_ISLNK(st.st_mode),p
    attrs=st.st_file_attributes if os.name=='nt' else 0
    assert not attrs&0x400,('reparse point',p)
    return p


def files():
    count=0
    for dp,ds,fs in os.walk(BUILD,followlinks=False):
        for d in ds[:]:
            p=Path(dp)/d
            if p.is_symlink() or (os.name=='nt' and p.stat(follow_symlinks=False).st_file_attributes&0x400):
                LINKS.add(p);ds.remove(d)
        for f in fs:
            p=Path(dp)/f
            if p==RECOVERY or p==RECOVERY.with_suffix('.partial'):continue
            count+=1
            if count%100000==0:print(json.dumps(dict(inventory_paths=count)),flush=True)
            yield checked(p)


def keep_set():
    # Keep actual current input manifests and their explicitly bound build files.
    # Do not recursively expand historical proof graphs into every old build.
    keep=set()
    for p in ROOTS:
        q=json.loads(p.read_text(encoding='utf-8'))
        if p.is_relative_to(BUILD):keep.add(p)
        for n,digest in q['bindings'].items():
            a=Path(n).resolve()
            if a.is_relative_to(BUILD) and a.is_file():
                assert sha(a.read_bytes())==digest,a
                keep.add(a)
    for name in ACTIVE:
        d=BUILD/name
        if not d.is_dir():continue
        for dp,ds,fs in os.walk(d,followlinks=False):
            ds[:]=[n for n in ds if n not in ['.git','__pycache__']]
            keep.update((Path(dp)/f).resolve() for f in fs)
    # Preserve canonical root build products and the Lua runtime used by QA.
    for name in ['smb-crossover-mmc5-expanded.nes','smb-crossover-mmc5-expanded.build.json']:
        p=BUILD/name
        if p.is_file():keep.add(p)
    d=BUILD/'smb2-final62-observer-lua-deps-v1'
    if d.is_dir():keep.update(p.resolve()for p in d.rglob('*')if p.is_file())
    # Huge debug files for ancestor comparison builds are restored one at a
    # time if needed; keep only current debug files expanded.
    for p in list(keep):
        if p.suffix.lower()=='.dbg' and p.relative_to(BUILD).parts[0] not in ACTIVE:
            ARCHIVE_DEBUG.add(p);keep.remove(p)
    return keep


def recoverable(p):
    rel=p.relative_to(BUILD)
    if '.git' in rel.parts or '__pycache__' in rel.parts:return False
    if p in ARCHIVE_DEBUG:return True
    if p.suffix.lower() in SOURCE_EXT:return True
    # Small generated source data outside capture forests can contain unique
    # donor extraction work. Retain it, without archiving frame-dump payloads.
    return p.suffix.lower()=='.bin' and p.stat().st_size<=1048576 and not any(
        n in {'verification','capture','frames','video-review','reference-frames'}
        for n in rel.parts)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply',action='store_true')
    args=ap.parse_args()
    assert BUILD==Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover/build').resolve()
    assert BUILD.is_dir() and not RECOVERY.exists()
    keep=keep_set()
    allfiles=list(files())
    remove=[p for p in allfiles if p not in keep]
    archive=[p for p in remove if recoverable(p)]
    before_bytes=sum(p.stat().st_size for p in allfiles)
    keep_bytes=sum(p.stat().st_size for p in allfiles if p in keep)
    plan=dict(build=str(BUILD),before_files=len(allfiles),before_bytes=before_bytes,
              kept_files=len(allfiles)-len(remove),kept_bytes=keep_bytes,
              recovery_source_paths=len(archive),removed_files=len(remove),
              removed_bytes=before_bytes-keep_bytes,
              skipped_directory_links=sorted(str(p)for p in LINKS),
              active_inputs=[str(p)for p in ROOTS],active_roots=ACTIVE,
              keep=sorted(p.relative_to(BUILD).as_posix()for p in keep),
              policy='Current actual input closure remains expanded. Superseded source/recipes/JSON receipts are content-deduplicated in one verified ZIP. Superseded ROM/object/debug/listing/capture/log copies are disposable. Source, docs/checkpoints, Git, Downloads and original donors are not deleted.')
    REPORT.mkdir(exist_ok=True)
    (REPORT/'compaction-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in plan.items()if k not in['keep','active_inputs','active_roots','skipped_directory_links']},indent=2),flush=True)
    if not args.apply:return
    assert keep_bytes<4_000_000_000 and len(keep)<15000,('Active input set unexpectedly large',keep_bytes,len(keep))
    RECOVERY.parent.mkdir(exist_ok=True)
    temporary=RECOVERY.with_suffix('.partial')
    index=[];objects=set()
    with zipfile.ZipFile(temporary,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for i,p in enumerate(archive):
            data=p.read_bytes();digest=sha(data)
            index.append(dict(path=p.relative_to(BUILD).as_posix(),sha256=digest,bytes=len(data)))
            if digest not in objects:
                z.writestr('objects/'+digest,data);objects.add(digest)
            if i and i%10000==0:print(json.dumps(dict(recovery_archived_paths=i,unique_objects=len(objects))),flush=True)
        z.writestr('index.json',json.dumps(index,separators=(',',':')).encode('utf-8'))
    with zipfile.ZipFile(temporary)as z:
        assert len(json.loads(z.read('index.json')))==len(archive)
        for digest in objects:assert sha(z.read('objects/'+digest))==digest,digest
    assert keep_bytes+temporary.stat().st_size<5_000_000_000
    os.replace(temporary,RECOVERY)
    print(json.dumps(dict(recovery_verified=True,archive_bytes=RECOVERY.stat().st_size,source_paths=len(index),unique_objects=len(objects))),flush=True)
    removed_bytes=0
    for i,p in enumerate(remove):
        p=checked(p);size=p.stat().st_size
        try:p.unlink()
        except PermissionError:
            os.chmod(p,stat.S_IWRITE);p.unlink()
        removed_bytes+=size
        if i and i%50000==0:print(json.dumps(dict(deleted_files=i,deleted_bytes=removed_bytes)),flush=True)
    removed_links=[]
    for p in sorted(LINKS):
        # Remove only the link entry with nonrecursive rmdir/unlink. Its target
        # is not traversed, archived, counted as freed, or recursively deleted.
        checked_parent(p.parent)
        assert p.is_relative_to(BUILD) and p!=BUILD
        target=os.readlink(p)
        if p.is_symlink():p.unlink()
        else:
            assert os.path.isjunction(p),p
            os.rmdir(p)
        removed_links.append(dict(path=str(p),target=target,target_deleted=False))
    for dp,ds,fs in os.walk(BUILD,topdown=False):
        p=Path(dp)
        if p==BUILD:continue
        if not any(p.iterdir()):checked(p).rmdir()
    remaining=list(files())+[RECOVERY]
    after_bytes=sum(p.stat().st_size for p in remaining)
    report=dict(passed=True,before_files=len(allfiles),before_bytes=before_bytes,
                after_files=len(remaining),after_bytes=after_bytes,
                freed_bytes=before_bytes-after_bytes,deleted_files=len(remove),
                recovery_archive=str(RECOVERY),recovery_archive_sha256=sha(RECOVERY.read_bytes()),
                recovery_source_paths=len(index),recovery_unique_objects=len(objects),
                removed_directory_links=removed_links,
                current_ROM_sha256=sha((Path.home()/'Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()),
                scope=plan['policy'])
    (REPORT/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items()if k!='removed_directory_links'},indent=2),flush=True)


if __name__=='__main__':
    main()
