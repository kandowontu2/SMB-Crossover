"""Preserve the verified private MMC5 CHR publication fix and exact source."""
from pathlib import Path
import datetime, gzip, hashlib, json, shutil, subprocess, sys, zipfile

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/chr-publication-np'
FINAL=ROOT/'build/checkpoints/chr-publication-np'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not FINAL.exists(), 'Do not replace a saved checkpoint'
    proof=json.loads((QA/'proof.json').read_text())
    rom=QA/'candidate-v2.nes'
    assert proof['passed']and proof['rom_sha256']==sha(rom)
    parent=json.loads((ROOT/'build/checkpoints/roll-performance-no/manifest.json').read_text())
    names=set(parent['source_files'])
    names.update(p.relative_to(ROOT).as_posix()for pattern in ('*chr_commit*','*chr_publication*')
                 for p in(ROOT/'tools/audit').glob(pattern)if p.is_file())
    names.update(['docs/qa/player-chr-publication-2026-10-23.md',
                  'docs/qa/final-verification-plan-2026-10-23.md'])
    hashes={n:sha(ROOT/n)for n in sorted(names)}
    sys.path.insert(0,str(ROOT/'tools'))
    from playthroughs.roster_run import workspace_bytes
    assert workspace_bytes(ROOT)+sum((ROOT/n).stat().st_size for n in names)+100_000_000<30_000_000_000
    stage=QA/'snapshot-v2';stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name in sorted(names):z.write(ROOT/name,name)
    source=stage/'source'
    with zipfile.ZipFile(stage/'source.zip')as z:
        assert all((source/i.filename).resolve().is_relative_to(source.resolve())for i in z.infolist())
        z.extractall(source)
    rebuilt=stage/'roundtrip.nes'
    result=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),
        '--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),
        '--output',str(rebuilt)],cwd=source,capture_output=True,text=True)
    (stage/'rebuild.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and sha(rebuilt)==sha(rom),'Exact source-bundle rebuild'
    assert all(sha(ROOT/n)==v for n,v in hashes.items()),'Source changed during checkpoint creation'
    for name,wanted in proof['unchanged_public_roms'].items():
        assert sha(ROOT/'build'/f'smb-crossover-{name}.nes')==wanted
    FINAL.mkdir()
    shutil.copy2(stage/'source.zip',FINAL/'source.zip')
    for suffix in('.nes','.lbl','.map'):shutil.copy2(rom.with_suffix(suffix),FINAL/('candidate'+suffix))
    raw=rom.with_suffix('.dbg').read_bytes()
    (FINAL/'candidate.dbg.gz').write_bytes(gzip.compress(raw,mtime=0))
    assert gzip.decompress((FINAL/'candidate.dbg.gz').read_bytes())==raw
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        status='PRIVATE_CHR_PUBLICATION_REPAIR_WITH_OPEN_PERFORMANCE_AUDIO_AND_FULL_MATRIX',
        parent_checkpoint='roll-performance-no',identities=37,rom_sha256=sha(rom),
        source_zip_sha256=sha(FINAL/'source.zip'),source_bundle_rebuild=dict(exact=True,rom_sha256=sha(rebuilt)),
        source_files=hashes,evidence=dict(proof=proof,proof_sha256=sha(QA/'proof.json')),
        limitations=['Private MMC5 only; published33-identity builds unchanged.',
            'Pentarou severe body dropout with shots, PN reset HUD glyph, and PN death path need follow-up.',
            'Global lag/dropout, dedicated audio, production oversized MMC3 integration remain.',
            'Final every-identity1-1 and every-powerup matrix remains required.'])
    (FINAL/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (QA/'checkpoint.json').write_text(json.dumps(dict(checkpoint=str(FINAL),rom_sha256=sha(rom),
        source_zip_sha256=report['source_zip_sha256'],goal_complete=False),indent=2)+'\n')
    assert workspace_bytes(ROOT)<30_000_000_000
    print(json.dumps(dict(checkpoint=str(FINAL),rom_sha256=sha(rom),source_zip_sha256=report['source_zip_sha256'])))


if __name__=='__main__':main()
