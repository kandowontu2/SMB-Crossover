"""Rebuild prepared mapper CHR in a disposable, retained copy of asset inputs."""
from pathlib import Path
import sys,shutil,json,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/reference'))
import pack_chr,build_ordinary_body_layout,build_megaman_injury_art,build_megaman_assets,build_samus_assets
O=R/'build/verification/new-roster-1-1-nd/repack-proof';O.mkdir(exist_ok=False)
shutil.copytree(R/'chr',O/'chr')
(O/'src').mkdir();(O/'tests/fixtures').mkdir(parents=True);(O/'build').mkdir()
for name in('bass_metasprites.inc','bill_metasprites.inc','megaman_metasprites.inc','expanded_poses.inc'):
 shutil.copyfile(R/'src'/name,O/'src'/name)
shutil.copyfile(R/'tests/fixtures/megaman-bass-injury-source-art.json',O/'tests/fixtures/megaman-bass-injury-source-art.json')
for mod in(pack_chr,build_ordinary_body_layout,build_megaman_injury_art,build_megaman_assets,build_samus_assets):mod.ROOT=O
pack_chr.main()
report={}
for name in('packed-mmc3.chr','packed-mmc5.chr','ordinary-bass-walk.chr','crossover-expanded.chr','crossover-hurt-body.chr'):
 before=(R/'chr/characters'/name).read_bytes();after=(O/'chr/characters'/name).read_bytes()
 assert before==after,('Asset regeneration must reproduce prepared bytes',name)
 report[name]=hashlib.sha256(after).hexdigest()
for mapper in('mmc3','mmc5'):
 name=f'chr_map_{mapper}.inc';assert (R/'src'/name).read_bytes()==(O/'src'/name).read_bytes(),name
(O/'proof.json').write_text(json.dumps(dict(passed=True,prepared_mapper_CHR_exact=report,physical_maps_exact=True),indent=2)+'\n')
print('PASS normal packing exactly reproduces both prepared mapper CHR files and physical maps')
