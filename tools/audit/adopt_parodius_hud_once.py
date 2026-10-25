"""Adopt the verified MMC5 graphical bars and preserve MMC3 asset packing."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PARENT = '274fff8613d98a281d7549d13e59430c4d6b4553eb16bd9d2c651e0b409c8b3b'
CURRENT = 'ee0b6bc5e253e6de7476ef9b781e748c1fced896a28cadd13d74561119172a44'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    args=parser.parse_args();candidate=args.candidate.resolve()
    rom=candidate/'candidate.nes'
    assert sha(rom)==CURRENT
    proofs=[]
    for name in ['queue-proof.json','native-v1/proof.json','native-routes-v1/proof.json']:
        path=candidate/name;q=json.loads(path.read_text())
        assert q['passed'] and q['ROM_sha256']==CURRENT
        if 'runs'in q:assert q['complete']and len(q['runs'])==3
        proofs.append(dict(path=str(path),sha256=sha(path)))
    out=candidate/'adoption-v1';out.mkdir(exist_ok=False)
    paths=['smb1base-mmc5-expanded.cfg','src/parodius.s','src/parodius_render.s',
           'src/parodius_hud.inc','chr/characters/parodius-hud.chr']
    before={};sources=[]
    for name in paths:
        source=candidate/'source'/name;target=ROOT/name
        before[name]=target.read_bytes() if target.exists()else None
        if target.exists():
            backup=out/'previous'/name;backup.parent.mkdir(parents=True,exist_ok=True)
            backup.write_bytes(before[name])
        target.write_bytes(source.read_bytes());sources.append(dict(path=name,sha256=sha(target)))
    packing=ROOT/'tools/prepare_mmc3_oversized.py';name=packing.relative_to(ROOT).as_posix()
    before[name]=packing.read_bytes()
    newline=b'\r\n'if b'\r\n'in before[name]else b'\n'
    anchor=b'    raw[395*1024:396*1024]=ui'+newline
    assert before[name].count(anchor)==1
    added=b'''    # Graphical Parodius fonts share the verified unused gap before Chip412.
    hud=prepared/'parodius-hud.chr'
    if hud.exists():
        data=hud.read_bytes();assert len(data)==3072
        raw[396*1024:399*1024]=data
'''.replace(b'\n',newline)
    packing.write_bytes(before[name].replace(anchor,anchor+added))
    sources.append(dict(path=name,sha256=sha(packing)))
    root_rom=out/'candidate.nes'
    try:
        with(out/'root-build.log').open('w')as log:
            result=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                                   '--source-overlay',str(ROOT),'--output',str(root_rom)],
                                  cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0 and sha(root_rom)==CURRENT
        # Check the converter's complete prepared-art/reference equality using
        # the active recipe. This is asset preparation, not MMC3 native admission.
        with(out/'mmc3-prepare.log').open('w')as log:
            result=subprocess.run([sys.executable,str(packing),'--source-root',str(ROOT),
                                   '--output',str(out/'mmc3-prepared-source'),
                                   '--reference-rom',str(root_rom)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0,(out/'mmc3-prepare.log').read_text()[-3000:]
    except BaseException:
        for name,raw in before.items():
            target=ROOT/name
            if raw is None:
                target.unlink()
            else:
                target.write_bytes(raw)
        raise
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    assert sha(installed)==PARENT
    backup=out/('SMB-Crossover-Current-MMC5-'+PARENT+'.nes')
    shutil.copy2(installed,backup);assert sha(backup)==PARENT
    shutil.copy2(root_rom,installed);assert sha(installed)==CURRENT
    q=dict(adopted=True,goal_complete=False,ROM_sha256=CURRENT,parent_ROM_sha256=PARENT,
           installed=str(installed),previous_download_backup=str(backup),root_build=str(root_rom),
           source=sources,evidence=proofs,original_other_CHR_and_RAM_exact=True,
           root_compile_exact_to_tested_ROM=True,MMC3_prepared_asset_parity=True,
           native_PPU_cursor_pixel_frames=192,native_PPU_cursor_pixels=344064,
           scope='MMC5 full graphical original Parodius bars, all seven32px cursor positions, private font acquisition and bounded dirty queue. Actual rendered masks/NMI/banks pass for all three ships; three ordinary-controller zero-death1-1 runs continue through1-2 entry. Human inspected representative actual PPU images. MMC3 retains text fallback; its full graphical font upload and separate architecture remain outstanding. Zelda II terrain and overall roster/item/audio/lag goal remain incomplete.')
    (out/'proof.json').write_text(json.dumps(q,indent=2))
    receipt=ROOT/'build/verification/parodius-graphical-hud';receipt.mkdir(exist_ok=False)
    (receipt/'proof.json').write_text(json.dumps(q,indent=2))
    print(json.dumps(q),flush=True)


if __name__=='__main__':main()
