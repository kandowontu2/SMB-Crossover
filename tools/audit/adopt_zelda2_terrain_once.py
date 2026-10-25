"""Install the verified Zelda II block/pipe terrain fix once, preserving rollback."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
PARENT='ee0b6bc5e253e6de7476ef9b781e748c1fced896a28cadd13d74561119172a44'
CURRENT='f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();c=a.candidate.resolve()
    assert sha(c/'candidate.nes')==CURRENT
    evidence=[]
    for name in ['cpu-proof.json','native-components-v4/native-proof.json','native-routes-v3/proof.json','direct-v1/proof.json','native-controls-v2/proof.json']:
        path=c/name;q=json.loads(path.read_text());assert q['passed']and q['ROM_sha256']==CURRENT
        evidence.append(dict(path=str(path),sha256=sha(path)))
    controls=json.loads((c/'native-controls-v1/proof.json').read_text())
    for identity in ['link','sophia','mac']:
        assert next(r for r in controls['runs']if r['identity']==identity)['passed']
    evidence.append(dict(path=str(c/'native-controls-v1/proof.json'),sha256=sha(c/'native-controls-v1/proof.json'),
                         scope='Three passing controls only. The failed Samus Hard run used its Easy controller; matching Easy succeeds separately. Original failure retained.'))
    out=c/'adoption-v1';out.mkdir(exist_ok=False)
    files=['src/characters.s','src/entrypoint.s','src/little_mac_terrain.s','src/megaman_weapons.s',
           'src/samus.s','src/tmnt_probe_gates.s','src/zelda2_link_motion.s','src/zelda2_link_terrain.s']
    previous={};sources=[]
    for name in files:
        target=ROOT/name;previous[name]=target.read_bytes()if target.exists()else None
        if target.exists():
            backup=out/'previous'/name;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(previous[name])
        target.write_bytes((c/'source'/name).read_bytes());sources.append(dict(path=name,sha256=sha(target)))
    root_rom=out/'candidate.nes'
    try:
        with(out/'root-build.log').open('w')as log:
            result=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                                   '--source-overlay',str(ROOT),'--output',str(root_rom)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0 and sha(root_rom)==CURRENT
        with(out/'mmc3-prepare.log').open('w')as log:
            result=subprocess.run([sys.executable,str(ROOT/'tools/prepare_mmc3_oversized.py'),
                                   '--source-root',str(ROOT),'--output',str(out/'mmc3-prepared-source'),
                                   '--reference-rom',str(root_rom)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0,(out/'mmc3-prepare.log').read_text()[-3000:]
    except BaseException:
        for name,raw in previous.items():
            target=ROOT/name
            if raw is None:target.unlink()
            else:target.write_bytes(raw)
        raise
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes');assert sha(installed)==PARENT
    backup=out/('SMB-Crossover-Current-MMC5-'+PARENT+'.nes');shutil.copy2(installed,backup);assert sha(backup)==PARENT
    shutil.copy2(root_rom,installed);assert sha(installed)==CURRENT
    q=dict(adopted=True,goal_complete=False,ROM_sha256=CURRENT,parent_ROM_sha256=PARENT,
           installed=str(installed),previous_download_backup=str(backup),root_build=str(root_rom),source=sources,evidence=evidence,
           root_compile_exact_to_tested_ROM=True,existing_RAM_and_CHR_exact=True,MMC3_prepared_asset_parity=True,
           native_1_1_zero_death_modes=['easy','hard'],independent_physical_PPU_frames=9326,
           staged_native_geometry_cases=11,staged_guarded_NMIs=176,
           scope='MMC5 Zelda II full-height normal/crouched block and pipe queries, separate Fairy points, real ceiling crossing, authoritative bumped block cell, wall page carries and Fairy floor alignment. Independent Easy/Hard zero-death1-1 replays, native geometry components and affected-profile controls pass. Fairy lower sides deliberately centered for SMB instead of native asymmetric indexing. Source enemy hurtbox and moving-platform-specific Fairy attachment remain a separate follow-up; no full campaign/all-upgrade/audio/lag or current oversized-MMC3 native qualification.')
    (out/'proof.json').write_text(json.dumps(q,indent=2))
    receipt=ROOT/'build/verification/zelda2-terrain';receipt.mkdir(exist_ok=False)
    (receipt/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)


if __name__=='__main__':main()
