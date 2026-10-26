"""Freeze the private current3b SMB3 source-only adapter; never launches native."""
from pathlib import Path
import argparse,ast,hashlib,json,sys
from smb3_host_current3b_cpu_v1 import D,R,sha,put

def dependencies(starts):
 seen=set();pending=list(starts)
 while pending:
  f=pending.pop().resolve()
  if f in seen:continue
  assert f.is_file(),f;seen.add(f)
  if f.suffix!='.py':continue
  for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
   names=[node.module]if isinstance(node,ast.ImportFrom)and node.module else[n.name for n in node.names]if isinstance(node,ast.Import)else[]
   for name in names:
    for directory in [f.parent,R/'tools/audit',R/'tools']:
     dep=directory/(name.replace('.','/')+'.py')
     if dep.exists():pending.append(dep);break
 return sorted(seen)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(a.packet/'candidate.nes')=='7469d9f62af3161c896b844546ead66002bb425ba8b5143692b1c2ae1d9f1219'
 report=R/'docs/qa/smb3-host-current3b-2026-10-26.txt';source=json.loads((a.packet/'source-manifest.json').read_text());files=[a.packet/'source'/n for n in source]
 starts=list((R/'tools/audit').glob('smb3_host_current3b_*.py'))+[R/'tools/prepare_smb3_dmc_mirrors.py',R/'tools/audit/smb3_asset_relocation_cpu_v4.py',R/'tools/audit/smb3_asset_relocation_irq_v1.py',R/'tools/build_mmc5_expanded.py'];tools=dependencies(starts)
 receipts=['controls-v1/proof.json','boundaries-v2/proof.json','owner-controls-v2/proof.json','world-sfx-v1/proof.json','asset-controls-v1/proof.json','asset-irq-v1/proof.json','rebuild-controls-v1/proof.json','layout-v1/proof.json','candidate.smb3-mirrors.json','whole-budget-v1.json']
 for n in receipts:
  q=json.loads((a.packet/n).read_text());assert q.get('passed',True),n
 files +=[a.packet/n for n in receipts]+[a.packet/'candidate.nes',a.packet/'candidate.dbg',a.packet/'source-manifest.json',a.packet/'source-projection.json',a.packet/'build-command.json',a.packet/'layout-v1/implementation.patch',report]
 for n in ['smb3-host-current3b-v1/failure.json','smb3-host-current3b-v2/failure.json','smb3-host-current3b-v3/boundaries-v1/failure.json','smb3-host-current3b-v3/owner-controls-v1/failure.json']:
  f=D/n
  if f.exists():files.append(f)
 base=D/'root-current-roster-composition-v1';files +=[base/n for n in ['candidate.nes','candidate.dbg','source-manifest.json']]
 for directory,names in [(D/'smb3-native-readers-opt-v2',['candidate.nes','source/src/smb3_native_standalone.s','source/src/smb3_native_payload.s','source/audio/smb3-native/source-payload.bin']),(D/'smb3-native-core-v5',['preparation.json']),(D/'smb3-original-music-closure-v3',['dynamic-closure.json','proof.json'])]:files +=[directory/n for n in names]
 files +=[R/'reference/new-roster-audio/mario3/crossover-named.nsf',Path(sys.executable)]
 files=sorted(set(f.resolve()for f in files+tools));bindings=[dict(path=str(f).replace('\\','/'),sha256=sha(f),bytes=f.stat().st_size)for f in files]
 for n,h in source.items():assert sha(a.packet/'source'/n)==h
 put(a.output/'readiness.json',dict(passed=True,source_ready=True,native_run=False,native_granted=False,adopted=False,parent_ROM_sha256=sha(base/'candidate.nes'),candidate_ROM_sha256=sha(a.packet/'candidate.nes'),source_directory=str(a.packet/'source').replace('\\','/'),complete_source_files=len(source),changed_source_files=9,receipt_paths=receipts,report_path=str(report).replace('\\','/'),tool_paths=[str(f).replace('\\','/')for f in tools],bindings=bindings,source_reproduction=['python tools/audit/smb3_host_current3b_prepare_v3.py --output NEW_EXTERNAL_PACKET','python tools/prepare_smb3_dmc_mirrors.py --source NEW_EXTERNAL_PACKET/source --rom NEW_EXTERNAL_PACKET/candidate.nes'],remaining=['No native call/clone/sample/render/cadence observation yet','Actual NMI/PPU/DMC waveform/latency and pause/title lifecycle need focused qualification','Durable postlink producer exists but production build hook deliberately unchanged'],freeze_tool_sha256=sha(__file__)))
 print(json.dumps(dict(passed=True,bindings=len(bindings),tools=len(tools),readiness_sha256=sha(a.output/'readiness.json'))))
if __name__=='__main__':main()
