"""Explicit d52 rebase of private motion/BG prototype; no canonical edit."""
from pathlib import Path
import hashlib,json,runpy,sys
R=Path(__file__).resolve().parents[1];O=R/'build/rogue-dawn-host-pipeline-v2'
P=R/'build/roster-shared-celeste-small-v1.nes'
EXPECTED='d52eeefe78c5f050d276a833c651456b717157856d1783b98c131f9da29f8a60'

def main():
 sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
 assert sha(P)==EXPECTED
 prior=R/'build/rogue-dawn-host-pipeline-v1'
 old=json.loads((prior/'build.json').read_text());assert sha(prior/'candidate.nes')==old['ROM_sha256']=='aa91efabe1e76b0483fa6d66a8e6d59a3975a8acd42dc0f1822b0a907ac9e016'
 assert json.loads((prior/'controls.json').read_text())['passed']
 for row in old['bindings']:assert sha(row['path'])==row['sha256'],row['path']
 O.mkdir(exist_ok=True);assert not(O/'build.json').exists()
 (O/'movement-flush.s').write_bytes((prior/'movement-flush.s').read_bytes())
 text=(prior/'build-private.py').read_text()
 text=text.replace("R/'build/roster-shared-rcr-adopted-v8.nes'","R/'build/roster-shared-celeste-small-v1.nes'")
 text=text.replace('4cbd019100ba4dfc51fd9f71c5d3cabd844828eb7d5d2a4aa39413e3579ab39a',EXPECTED)
 text=text.replace("R/'build/rogue-dawn-host-pipeline-v1'","R/'build/rogue-dawn-host-pipeline-v2'")
 text=text.replace("paths=[R/'tools/prepare_rogue_dawn_host_pipeline_v1.py',","paths=[R/'tools/prepare_rogue_dawn_host_pipeline_v2.py',R/'src/celeste_mario_host.s',R/'src/celeste_mario_host_entry.s',R/'tools/prepare_rogue_dawn_host_pipeline_v1.py',")
 p=O/'build-private.py';p.write_text(text,newline='\n');sys.argv=[str(p),'--output',str(O)];runpy.run_path(str(p),run_name='__main__')
if __name__=='__main__':main()
