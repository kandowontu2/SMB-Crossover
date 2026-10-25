from pathlib import Path
import hashlib, json, shutil, subprocess, sys
from mmc3_parser_build_v1 import R,D,compile_rom
P=D/'mmc3-parser-v42';O=D/'mmc3-parser-recipe-v43';O.mkdir(exist_ok=False);tools=O/'tools';tools.mkdir()
for name in ['prepare_mmc3_oversized.py','mmc3_current_repairs.py']:shutil.copy(R/'tools'/name,tools/name)
assets=tools/'mmc3_oversized';assets.mkdir();shutil.copy(P/'repairs.proposed.json',assets/'repairs.json');shutil.copy(R/'tools/mmc3_oversized/mmc3-menu-previews.chr',assets)
source=O/'source'
with(O/'prepare.log').open('w')as log:p=subprocess.run([sys.executable,str(tools/'prepare_mmc3_oversized.py'),'--source-root',str(R),'--output',str(source),'--reference-rom','C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'prepare.log').read_text()[-3500:]
rom=O/'candidate.nes';compile_rom(source,rom)
assert rom.read_bytes()==(P/'candidate.nes').read_bytes()
q=dict(passed=True,ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),exact_current_source_recipe_rebuild=True,recipe_sha256=hashlib.sha256((assets/'repairs.json').read_bytes()).hexdigest(),source_adopted=False,scope='Fresh current root preparation through the additive proposed recipe and complete compile is byte-identical to private V42. Active root source and accepted recipe unchanged.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
