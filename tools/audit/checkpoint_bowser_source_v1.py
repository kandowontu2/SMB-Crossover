"""Save Bowser source/art progress without executables, ROMs or captures."""
from pathlib import Path
import hashlib
import json
import zipfile

from checkpoint_roster_packets_v1 import ROOT, DEST, verify


def bind(path):
    path=Path(path).resolve();data=path.read_bytes()
    return dict(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def main():
    match=ROOT/'build/smb3-original-source-match-v1/proof.json'
    art=ROOT/'build/smb3-bowser-source-assets-v1/handoff.json'
    m=json.loads(match.read_text());a=json.loads(art.read_text())
    seen={};verify(m,seen);verify(a,seen)
    assert m['original_PRG_exact'] and len(a['frames'])==9
    assert len(a['original_renderer']['genuine_original_cases'])==72
    closure=Path(m['assembly_closure']['path']);c=json.loads(closure.read_text());verify(c,seen)
    compiler=Path(m['compiler_proof']['path']);n=json.loads(compiler.read_text());verify(n,seen)
    acquisition=Path(n['acquisition']['path']);q=json.loads(acquisition.read_text());verify(q,seen)
    public=[ROOT/'tools/audit'/name for name in ['acquire_nesasm_source_v1.py','build_local_nesasm_v1.py',
        'acquire_smb3_assembly_closure_v1.py','match_original_smb3_source_v1.py',
        'prepare_original_smb3_bowser_assets_v1.py','checkpoint_bowser_source_v1.py']]
    report=ROOT/'docs/qa/smb3-bowser-original-source-2026-10-29.json'
    assert not report.exists()
    result=dict(status='Original PRG and nine Bowser poses qualified; playable host still open',
        original_match=bind(match),source_art=bind(art),compiler=bind(compiler),
        assembly_source_files=727,original_PRG_bytes_exact=262144,
        original_CHR_passthrough=True,independent_PCX_conversion=False,
        real_original_renderer_cases=72,packed_CHR_pages=2,reserved_CHR=[824,827],
        original_palette=[255,26,48,39],native_palette=[15,26,48,39],
        visual_review='Root viewed the complete nine-pose source contact sheet. Exact original geometry/half mirrors preserved; approximate RGB preview only, not emulated player graphics.',
        corrections_before_freeze='Original CPU comparison caught intrinsic front-facing poses ignoring incoming horizontal flip for coordinate selection. Corrected oracle before freezing; no original renderer changed.',
        source_credit='Southbird, https://www.sonicepoch.com/sm3mix/',
        still_open=['SMB1 Bowser alternate','Playable controls, collision/combat/upgrades/lifecycle/audio',
            'Real selection, lives, 1-1, both modes, all earned upgrades and visual/performance checks'],
        Downloads_unchanged=True,source_only=True)
    report.write_text(json.dumps(result,indent=2)+'\n')
    target=DEST/'bowser3-original-prg-and-authentic-poses';assert not target.exists();target.mkdir()
    files=public+[report,match,art,closure,compiler,acquisition,
        Path(m['acquisition']['path']),Path(m['smb3.fns']['path']),
        Path(m['assembly_log']['path'])]
    files += [Path(row['path'])for row in c['files']]
    files += [Path(row['path'])for row in q['files']]
    files += [Path(row['path'])for row in a['outputs']]
    members={};archive=target/'frozen-source-packet.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path in dict.fromkeys(files):
            assert path.is_relative_to(ROOT)
            assert path.suffix not in ['.exe','.nes','.dbg','.map','.nesppuv1']
            data=path.read_bytes();name=path.relative_to(ROOT).as_posix()
            info=zipfile.ZipInfo(name,(2026,10,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data);members[name]=hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(archive)as z:
        assert {name:hashlib.sha256(z.read(name)).hexdigest()for name in z.namelist()}==members
    receipt=dict(status=result['status'],archive=bind(archive),archive_members=members,
        original_bound_files=seen,report=bind(report),owned_public_files=[bind(p)for p in public])
    (target/'root-review.json').write_text(json.dumps(receipt,indent=2)+'\n')
    progress=ROOT/'docs/qa/new-character-source-progress-2026-10-28.json'
    state=json.loads(progress.read_text())
    state['SMB3_Bowser_source']=dict(status=result['status'],original_match=bind(match),
        source_assets=bind(art),report=bind(report),checkpoint=str(target.relative_to(ROOT)))
    progress.write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps(dict(report=bind(report),files=len(members),archive=bind(archive))))


if __name__=='__main__':main()
