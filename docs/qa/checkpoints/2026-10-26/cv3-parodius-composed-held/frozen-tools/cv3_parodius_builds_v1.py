"""Fresh combined canonical/ordinary builds and honest full-parent inventory."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);source=a.prepared/'source'
 def build(stem,flag=None):
  cmd=[sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/(stem+'.nes'))]
  if flag:cmd+=['--flag-off',flag]
  with(a.output/(stem+'.host.log')).open('w')as log:r=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
  assert not r.returncode,(a.output/(stem+'.host.log')).read_text()[-5000:];return sha(a.output/(stem+'.nes'))
 canonical=build('candidate');assert canonical==sha(a.prepared/'candidate.nes')=='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'
 ordinary=[]
 for mapper,expected in[('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
  h=build('ordinary-'+mapper,mapper);assert h==expected;ordinary.append(dict(mapper=mapper,sha256=h,ordinary_original_exact=True))
 inventory=json.loads((a.prepared/'layout-v2/all-deployable-files.json').read_text());old=json.loads((D/'cv3-remaining-legacy-wrapper-v2/layout-v1/all-deployable-files.json').read_text());oldpaths={q['path']for q in old};primary=oldpaths|{'src/nmi_vram_fast.s','src/parodius_hud_queue.s'};builds={'candidate.nes','candidate.dbg','candidate.lbl','candidate.map'};assert len(inventory)==809 and len(primary)==638;extra=[q for q in inventory if q['path']not in primary|builds];assert len(extra)==167;assert all(q['path'].startswith(('reference/','tools/reference/'))for q in extra)
 partitions=dict(primary_source_tool_asset_paths=[q for q in inventory if q['path']in primary],unchanged_parent_reference_inputs=extra,unchanged_parent_top_level_derived_outputs=[q for q in inventory if q['path']in builds]);assert len(partitions['primary_source_tool_asset_paths'])==638
 for q in inventory:assert sha(source/q['path'])==q['sha256'],('Unexpected source change after fresh compile',q['path'])
 (a.output/'source-inventory-partitions.json').write_text(json.dumps(partitions,indent=2)+'\n');r=dict(passed=True,native_executed=False,adopted=False,ROM_sha256=canonical,fresh_canonical_exact=True,ordinary_flagoff=ordinary,full_parent_snapshot_inventory=809,primary_source_tool_asset_paths=638,extra_unchanged_reference_inputs=167,extra_unchanged_derived_outputs=4,inventory_label_addendum='layout-v2/all-deployable-files.json is an intentionally broad complete-parent snapshot inventory; its all_deployable_files809 label overstates deployability. Actual partition638 primary source/tool/assets+167 retained reference inputs+4 retained stale top-level derived candidate files; none omitted from correspondence proof or overwritten, and none is asserted to be fresh linked output.',partitions_sha256=sha(a.output/'source-inventory-partitions.json'),tool_sha256=sha(__file__),scope='Fresh canonical and original ordinary builds, full source byte stability and additive manifest classification only. No native/adoption claim; old broad inventory and first strict catalog failure stay unmodified.')
 (a.output/'proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
