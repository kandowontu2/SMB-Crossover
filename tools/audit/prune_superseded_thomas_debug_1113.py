"""Inventory/prune seven retired host debug files; no archives or source removal."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil

import build_storage_guard_v1 as G

ROOT=Path(__file__).resolve().parents[2]
BUILD=(ROOT/'build').resolve()
NAMES=('thomas-late-lifts-1102-v1','thomas-melee-stack','thomas-lift-carry',
       'thomas-native-carry','thomas-pipe-lifts','thomas-natural-host-1031-v6','thomas-adapter')
EXPECTED=(
    'cd6bd8b09a01d111c44b670511987d5b8015faebeb6d43964999426b08ee56bb',
    'e4a328e67bde8fa3087474889dac432b86a1b70466ee98d22e049f9f4aa8c18b',
    'ad0c85a787d70be61ad35b763ca5a3d9d9ea8a67d9c716da74d4188f3ef8a36f',
    '66c124a4ae2d5193069febeb6113179eeb190c7b9f2d16ca380e6f9108834dcb',
    '15852791b3b2852a51d5e44e4d3bac192713fc979b5f922055a9d9eb3df28135',
    '78a9fa8667910d921a452b5e68f77cb443a37ceb455f3a08857e7840934b32ca',
    'b7908bedfbd8005e081ab2f1d5d07c319c94b01fc803e944360d6d5fd4295070',
)
LIVE=('roster-combined-1101-v3/candidate.dbg','kirby-approach-owner-1101-v3/candidate.dbg',
      'bub-menu-candidate-1102-v2/combined-event.dbg','thomas-current-candidate-1102-v3/candidate.dbg')
REPORT=ROOT/'docs/qa/thomas-debug-cleanup-1113.md'


def checked(relative):
    original=BUILD/relative
    path=original.resolve(strict=True)
    assert path==original and path.is_relative_to(BUILD) and path.is_file()
    for part in (path,*path.parents):
        if part==BUILD:break
        assert not part.is_symlink() and not part.stat(follow_symlinks=False).st_file_attributes&0x400
    return path


def snapshot(path):
    return dict(path=path.relative_to(BUILD).as_posix(),bytes=path.stat().st_size,
                SHA256=sha256(path.read_bytes()).hexdigest())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    rows=[snapshot(checked(name+'/candidate.dbg')) for name in NAMES]
    assert tuple(row['SHA256'] for row in rows)==EXPECTED
    live={relative:snapshot(checked(relative)) for relative in LIVE}
    before=G.preflight(fresh=True)
    free=shutil.disk_usage(ROOT).free
    if not args.apply:
        print(json.dumps(dict(targets=rows,live_symbols=live,before=before,free_bytes=free,
                              deletes=0,outputs=0)),flush=True);return
    assert not REPORT.exists(),'Do not replace an existing cleanup receipt'
    # All deletes are individual, explicitly named files; no recursive operations.
    for row in rows:
        path=checked(row['path'])
        assert snapshot(path)==row
        path.unlink()
    assert all(not(BUILD/row['path']).exists() for row in rows)
    assert {relative:snapshot(checked(relative)) for relative in LIVE}==live
    after=G.preflight(fresh=True)
    assert before['build_files']-after['build_files']==len(rows)
    assert before['build_bytes']-after['build_bytes']==sum(row['bytes'] for row in rows)
    text=('# Retired Thomas debug cleanup\n\n'
        'Removed only seven superseded compiler candidate.dbg files. Active Steve, '
        'Karnov and DK Jr workers confirmed they do not use these inputs. All four '
        'current symbol-provider files below are preserved byte for byte. Source '
        'files, compiler recipes, source/native checkpoints, original-game debug '
        'files, the recovery archive, ROMs and user files remain. No archives or '
        'backups were created. Historical recipes that directly read these retired '
        'debug files need their exact debug input regenerated before replay.\n\n'
        '|Retired build path|Bytes|SHA256|\n|---|---:|---|\n'+
        ''.join(f"|{r['path']}|{r['bytes']}|{r['SHA256']}|\n" for r in rows)+
        '\nPreserved current symbol providers:\n\n'+
        ''.join(f"- {r['path']}: `{r['SHA256']}`\n" for r in live.values())+
        '\nStorage receipt:\n\n```json\n'+json.dumps(dict(before=before,after=after,
          free_before=free,free_after=shutil.disk_usage(ROOT).free),indent=2)+'\n```\n')
    REPORT.write_text(text,encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,removed_files=len(rows),removed_logical_bytes=sum(r['bytes'] for r in rows),
        active_symbol_inputs_equal=True,build=after,free_bytes=shutil.disk_usage(ROOT).free,
        receipt=str(REPORT),new_archives=0,source_files_removed=0)),flush=True)


if __name__=='__main__':main()
