"""Freeze the short paired bootstrap diagnostic proposal; no native launch."""
from pathlib import Path
import argparse,hashlib,json,shutil
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--prepared',type=Path,required=True);P=p.parse_args().prepared;o=P/'freeze-v1';o.mkdir(exist_ok=False);(o/'tools').mkdir()
 assert sha(P/'readiness.json')=='f5460bc0b9fda465b962b5525e473081ca500bd80dd5aefc247cbf8f096978dc'
 q=json.loads((P/'readiness.json').read_text());assert q['native_run']is False and q['limit_PPU_endFrames']==220 and q['maximum_proposed_native_launches']==2
 bindings=json.loads((P/'bindings.json').read_text());assert len(bindings)==674
 for path,h in bindings.items():assert sha(path)==h,path
 for label in['baseline','candidate']:assert not(P/label/'launch.json').exists()and not(P/label/'bootstrap-events.jsonl').exists()
 tools=sorted(p for p in(R/'tools/audit').glob('mm_proto_bootstrap_dma_*')if p.is_file())
 for p in tools:shutil.copyfile(p,o/'tools'/p.name)
 report=R/'docs/qa/mm-proto-shot-mux-title-dma-2026-10-26.txt';shutil.copyfile(report,o/report.name)
 old=D/'mm-proto-shot-mux-native-ready-v5/title-dma-negative-v1';assert sha(old/'proof.json')=='b5d354c9e05516aece817ea11ce701f828074ae4111e4860f542f6c4c6386c18'
 proof=json.loads((old/'proof.json').read_text());assert proof['actual_Main_releases']==172 and proof['all_actual_release_banks']==[126]
 proposal=dict(native_run=False,old_failed_physical256_unlogged=True,actual_raw_source_attrs_all_zero=True,actual_Main_releases=172,actual_Main_release_banks=[126],actual_Main_release_PC=[0x8355],source_begin=proof['observed_title_DMA']['ppu'],source_mask=30,software2003=0,actual_hardware_OAMADDR_unlogged=True,current_primary_source='https://github.com/nesdev-org/MesenCE/blob/master/Core/NES/NesPpu.cpp',source_checked_date='2026-10-26',source_not_bound_to_pinned_DLL=True,primary_source_paraphrase='Current upstream handles unused attribute bits and rendering-time sprite writes. This is a classification lead only. No byte equality mask is permitted.',hypotheses=proof['hypotheses'],proposal='Only exact bound matched baseline3cee/c5 bootstrap,220PPU frames each, source controller prefix183 polls then neutral. No long gameplay retry or installation.')
 (o/'classification.json').write_text(json.dumps(proposal,indent=2)+'\n')
 catalog={str(p):sha(p)for p in P.rglob('*')if p.is_file()and not p.is_relative_to(o)};catalog.update({str(p):sha(p)for p in o.rglob('*')if p.is_file()});catalog.update({str(old/'proof.json'):sha(old/'proof.json'),str(old/'catalog.json'):sha(old/'catalog.json'),str(report):sha(report)})
 for path,h in catalog.items():assert sha(path)==h,path
 (o/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
 result=dict(prepared=True,native_run=False,diagnostic_only=True,readiness_sha256=sha(P/'readiness.json'),bindings=674,bindings_sha256=sha(P/'bindings.json'),catalog_files=len(catalog),catalog_sha256=sha(o/'catalog.json'),frozen_tools=len(tools),report_sha256=sha(report),classification_sha256=sha(o/'classification.json'),old_negative_sha256=sha(old/'proof.json'),commands_sha256=sha(P/'commands.json'),maximum_native_launches=2,frames_each=220,grant_required=True,all_raw256_and2004_values_stamps_preserved=True,completed_hardware_serialized_BEFORE_guard_decisions=True,no_masks_gameplay_retry_or_adoption=True,checker_sha256=sha(__file__))
 (o/'readiness.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
