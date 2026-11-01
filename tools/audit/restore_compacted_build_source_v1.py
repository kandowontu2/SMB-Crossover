"""Find or restore explicitly named source files from the compact recovery ZIP."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
from build_storage_guard_v1 import preflight,TASK_BYTES,TASK_FILES

R=Path(__file__).resolve().parents[2]
B=(R/'build').resolve()
A=B/'_recovery/legacy-sources-2026-10-31.zip'


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--find',help='List at most30 matching archived source paths; does not extract.')
    ap.add_argument('--path',action='append',default=[],help='An exact source path relative to build/. Repeat for individual files.')
    args=ap.parse_args()
    assert args.find or args.path,'Specify a search or exact path. Whole-archive extraction is deliberately unavailable.'
    with zipfile.ZipFile(A)as z:
        index={q['path']:q for q in json.loads(z.read('index.json'))}
        if args.find:
            matches=[n for n in index if args.find.casefold()in n.casefold()]
            print(json.dumps(dict(matches=matches[:30],total_matches=len(matches),extracted=False),indent=2))
        chosen=[index[n]for n in dict.fromkeys(args.path)]
        assert len(chosen)<=TASK_FILES and sum(q['bytes']for q in chosen)<=TASK_BYTES
        preflight(reserved_bytes=sum(q['bytes']for q in chosen),reserved_files=len(chosen),fresh=True)
        for q in chosen:
            p=(B/q['path']).resolve();assert p.is_relative_to(B)and p!=B
            data=z.read('objects/'+q['sha256']);assert hashlib.sha256(data).hexdigest()==q['sha256']
            if p.exists():assert p.is_file()and p.read_bytes()==data,('Refuse overwrite',p)
            else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        if chosen:print(json.dumps(dict(restored_paths=[q['path']for q in chosen],restored_bytes=sum(q['bytes']for q in chosen))))


if __name__=='__main__':
    main()
