"""Freeze exact4285 private composition source/CPU correspondence; no native grant."""
from pathlib import Path
import argparse,ast,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return dict(path=str(p),sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);cv=D/'cv3-remaining-legacy-wrapper-v2';old=cv/'freeze-v2/readiness-source-only.json';native=cv/'native-freeze-v1/qualification-native.json';assert sha(old)=='fab1c3c38bd8885ca957442bf84b155adfd7f17a3142118b6c29e769c1141445'and sha(native)=='27341f8a370064076b0712d06ce18106bca18dfaf5531cbd2e215f06ff39c4bf';r=json.loads(old.read_text());n=json.loads(native.read_text());bindings=dict(r['all_frozen_bindings']);bindings.update(n['all_new_frozen_bindings'])
 def bind(p):
  p=Path(p);h=sha(p)
  if str(p)in bindings:assert bindings[str(p)]==h,('Old frozen input drift',str(p))
  bindings[str(p)]=h;return record(p)
 bind(old);bind(native);rom=a.prepared/'candidate.nes';assert sha(rom)=='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682';parent=D/'parodius-hud-cancel-candidate-v1';assert sha(parent/'candidate.nes')=='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631';bind(parent/'proof.json')
 receipts=[]
 folders=['layout-v2','builds-v1','cv3-hot-cpu-v1','ordinary-cpu-v1','cv3-irq-v1','source-oracle-v1','queue-cpu-v1','public-nmi-v1','queue-lifecycle-v1','callers-v1','hud-cpu-v1','gateway-cpu-v1','hud-interrupt-v1']
 for name in folders:
  f=a.prepared/name/'proof.json';z=json.loads(f.read_text());assert z['passed'];assert z.get('ROM_sha256',z.get('candidate_ROM_sha256'))==sha(rom);assert not z.get('native_executed',z.get('native_run',False));receipts.append(bind(f))
  for f in(a.prepared/name).rglob('*'):
   if f.is_file():bind(f)
 manifest=json.loads((a.prepared/'layout-v2/all-deployable-files.json').read_text());assert len(manifest)==809
 for q in manifest:
  f=a.prepared/'source'/q['path'];assert sha(f)==q['sha256'];bind(f)
 for f in[a.prepared/'candidate.nes',a.prepared/'candidate.dbg',a.prepared/'candidate.lbl',a.prepared/'baseline.nes',a.prepared/'baseline.dbg',a.prepared/'baseline.lbl',a.prepared/'implementation-fromf35.patch',a.prepared/'build-host.log',parent/'candidate.nes',parent/'candidate.dbg',parent/'candidate.lbl']:bind(f)
 for f in(ROOT/'tools/audit/proposals/cv3-legacy-wrapper-v2').rglob('*'):
  if f.is_file():bind(f)
 report=ROOT/'docs/qa/cv3-parodius-composed-source-2026-10-26.txt';bind(report)
 # Include all actual local Python import dependencies; existing frozen Lua and
 # oracle/runtime inputs are retained by the exact previous readiness bindings.
 pending=list((ROOT/'tools/audit').glob('cv3_parodius_*.py'));seen=set()
 while pending:
  f=pending.pop()
  if f in seen:continue
  seen.add(f);bind(f);tree=ast.parse(f.read_text(encoding='utf-8-sig'))
  for node in ast.walk(tree):
   names=[x.name.split('.')[0]for x in node.names]if isinstance(node,ast.Import)else[node.module.split('.')[0]]if isinstance(node,ast.ImportFrom)and node.module else[]
   for name in names:
    path=ROOT/'tools/audit'/(name+'.py')
    if path.is_file()and path not in seen:pending.append(path)
 tools={str(f):sha(f)for f in sorted(seen)}
 for path,h in bindings.items():assert sha(path)==h,('Frozen input/tool/environment drift',path)
 result=dict(passed=True,native_executed=False,native_grant=False,adopted=False,production_mutated=False,status='PRIVATE_F35_PLUS_CV3_SOURCE_CPU_READY_NATIVE_PENDING',candidate=record(rom),parent=record(parent/'candidate.nes'),CV3_donor=record(cv/'candidate.nes'),source=str(a.prepared/'source'),source_inventory=record(a.prepared/'layout-v2/all-deployable-files.json'),source_inventory_partitions=record(a.prepared/'builds-v1/source-inventory-partitions.json'),source_snapshot_inventory_count=809,primary_source_tool_assets=638,unchanged_extra_reference_inputs=167,unchanged_extra_derived_outputs=4,source_receipts=receipts,report=record(report),public_CV3_source_checkpoint=record(ROOT/'tools/audit/proposals/cv3-legacy-wrapper-v2/checkpoint.json'),retained_2cb5_one_native_result=record(native),other_native_labels_retained='14BASIC/9lifecycle are eaa3; oneHard1F recovered717 is2cb5; no4285 native. f35 sixth native aggregate incomplete at composition time.',all_CV3_banks_exact2cb5_and_all_other_banks_header_CHR_exactf35=True,source_eight_path_merge_only=True,f35_vic_queue_config_nmi_source_raw_preserved=True,future_launches=[],frozen_tools=tools,all_frozen_bindings=bindings,tool_sha256=sha(__file__),scope='Exact private composition and finite fresh source/CPU/build/ABI/queue/IRQ correspondence only. No controller/native/physical DMA/cadence/waveform/adoption certification. ROOT and area-preparation worker must separately bind/grant any new replay. All37/1-1/items remain incomplete.')
 dest=a.output/'readiness-source-only.json';dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,bindings=len(bindings),source_receipts=len(receipts),local_tool_dependencies=len(tools),readiness=record(dest)),indent=2))
if __name__=='__main__':main()
