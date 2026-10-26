"""Additive catalog of the ONE completed static-observer replay; no launch."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();d,out=a.experiment,a.output
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    b=json.loads((d/'binding.json').read_text());q=json.loads((d/'equivalence-proof.json').read_text())
    assert sha(d/'binding.json')=='fe1e0b3ad558158b2597a62aa7a43f9f3635c5d1a478aa4aaa11e38b7451ea91'
    assert q['passed']and q['old_expected_draws']==566 and q['frame_rows']==601
    assert json.loads((d/'launch-result.json').read_text())['exit']==0
    old=Path(b['original']);static=Path(b['static'])
    assert all(sha(old/n)==h for n,h in b['original_files'].items())
    out.mkdir(parents=True);(out/'tools').mkdir();(out/'scripts').mkdir()
    names=['tmnt_static_observer_equivalence_v1.py','tmnt_static_observer_finalize_v1.py',
           'tmnt_static_exec_dispatcher_v1.lua','tmnt_static_observer_prepare_v1.py','tmnt_static_observer_mock_v2.py']
    for n in names:shutil.copyfile(ROOT/'tools/audit'/n,out/'tools'/n)
    for n in ['run.lua','performance-observer.lua','chr-commit-observer.lua','tmnt_static_exec_dispatcher_v1.lua']:
        shutil.copyfile(static/n,out/'scripts'/n)
    for n in ['binding.json','equivalence-proof.json','launch-result.json','single-run-command.json']:
        shutil.copyfile(d/n,out/n)
    catalog={p.name:dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)for p in d.iterdir()if p.is_file()}
    (out/'actual-output-catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    report='''STATIC OBSERVER: ONE EXACT HISTORICAL NATIVE EQUALITY REPLAY
2026-10-25. Observer qualification only; no production/game patch or retry.

Frozen parser ROM9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd.
Frozen static Lua3412b98077d9c4f5436ab3df00712004fee572a1a3ceaa2810f355da646b4eca.
Native bindingfe1e0b3ad558158b2597a62aa7a43f9f3635c5d1a478aa4aaa11e38b7451ea91.
Only one newly granted Mesen replay, explicit Easy numeric0 actual readback.
Original dynamic observer was read, never rerun. Static dispatcher avoids
runtime host callback-vector growth; its slots preserve ordered callbacks.
All workload inputs, staged BEFORE-phase setup, complete600-update progression,
gold music/original source and hardware/DMC/OAM/CHR/stack/bank checks retained.

All8CSV files are byte-for-byte equal;2JSONL files have identical ordered parsed
rows/values;5JSON reports are structurally equal (object key order irrelevant).
Original and successor have0raw frames and0PPU screenshots; this is not RGB
equality coverage. Every original artifact is classified in binding.json.
Metadata (script/import locations, runner logs/host output, bindings and launch
records) is bound separately and is not masked out of a gameplay comparison.
MesenEXE, all installed DLLs, settings, ROM/debug/map/labels and every import
were hashed before launch; actual outputs/host/launch files are catalogued.

The original negative timing observation remains exact:600updates,566draws,
601performance-frame rows, versus baseline572draws. This does NOT qualify the
TMNT music candidate for release or recover any draw. There was no optimization
native run, original-dynamic rerun, Hard run, retry, outcome/setting/phase edit.
Worker grant is RELEASED. Future ROMs or observers require their own binding.
'''
    (out/'report.txt').write_text(report)
    doc=ROOT/'docs/qa/tmnt-static-observer-equivalence-2026-10-25.txt'
    doc.write_text(report+'\nExternal frozen catalog: '+str(out)+'\n')
    files={p.relative_to(out).as_posix():sha(p)for p in out.rglob('*')if p.is_file()}
    receipt=dict(passed=True,observer_only=True,native_replay_count=1,game_patch=False,ROM_sha256=b['ROM_sha256'],
                 exact_old_negative_draws=566,source_binding_sha256=sha(d/'binding.json'),files=files,
                 report_path=str(doc),report_sha256=sha(doc),checker_sha256=sha(Path(__file__)))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(frozen=True,receipt_sha256=sha(out/'receipt.json'),files=len(files),report_sha256=sha(doc))))


if __name__=='__main__':main()
