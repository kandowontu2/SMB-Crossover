"""Freeze finite df515 readiness with every predecessor/negative kept separate."""
from pathlib import Path
import argparse,hashlib,json,shutil
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SHA='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);root=Path(__file__).resolve().parents[2];c=a.base/'hud-scroll-candidate-v1';assert sha(c/'candidate.nes')==SHA;bindings={}
 def bind(f):assert f.is_file(),f;bindings[str(f.resolve())]=dict(bytes=f.stat().st_size,sha256=sha(f))
 paths={n:a.base/folder/'proof.json'for n,folder in [('layout','hud-scroll-candidate-v1'),('capture_model','hud-scroll-cpu-v3'),('gateway','hud-scroll-gateway-cpu-v1'),('protocol','hud-scroll-protocol-cpu-v1'),('final_guard','hud-scroll-guard-cpu-v1'),('lag_NMI','hud-scroll-lag-NMI-cpu-v1'),('whole_NMI_cost','hud-scroll-whole-NMI-cpu-v1')]};proofs={n:json.loads(f.read_text())for n,f in paths.items()}
 for n,q in proofs.items():
  if n=='layout':assert q['prepared']and q['all_v11_symbols_exact']and q['ROM_delta_bytes']==22
  else:assert q['passed']and q.get('ROM_sha256',q.get('candidate_ROM_sha256'))==SHA
  bind(paths[n]);f=paths[n].parent/'cases.json'
  if f.exists():bind(f)
 for f in c.glob('candidate.*'):
  if f.is_file():bind(f)
 bind(c/'sourcepatch.patch')
 source_notes=[]
 for name in ['reset.s','samus_freeze_render.s','parodius_adapter.s','parodius_bells.s','nmi_vram_fast.s','parodius_hud_queue.s']:
  f=c/'source/src'/name;bind(f);source_notes.append(dict(path=str(f),sha256=sha(f)))
 bind(c/'source/smb1base-mmc5-expanded.cfg')
 for folder,name in [('hud-readiness-v1','proof.json'),('hud-readiness-v1','manifest.json'),('hud-readiness-bank126-erratum-v1','proof.json'),('hud-scroll-negative-v1','proof.json'),('hud-scroll-negative-v1','manifest.json'),('hud-hard-crash-comparison-v2','proof.json'),('hud-hard-crash-comparison-v2','windows-application-error.txt'),('hud-scroll-cpu-preparse-v1','failure.txt'),('hud-scroll-cpu-preparse-v1','failed-tool.py'),('hud-scroll-cpu-v1','failure.json'),('hud-scroll-cpu-v2','failure.json')]:bind(a.base/folder/name)
 for folder in ['hud-scroll-cpu-v1','hud-scroll-cpu-v2']:bind(a.base/folder/'parodius_visibility_hud_scroll_cpu_v1.py')
 tools=['parodius_visibility_hud_scroll_candidate_v1.py','parodius_visibility_hud_scroll_cpu_v1.py','parodius_visibility_hud_scroll_gateway_cpu_v1.py','parodius_visibility_hud_scroll_packet_v1.py','parodius_visibility_hud_candidate_v1.py','parodius_visibility_hud_cpu_v1.py','parodius_visibility_hud_guard_cpu_v1.py','parodius_visibility_hud_nmi_cpu_v1.py','parodius_visibility_hud_nmi_budget_v1.py','check_nmi_vram_fast_cpu_v1.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py']
 for name in tools:f=root/'tools/audit'/name;bind(f);dest=a.output/'tools'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(f,dest)
 for f in [root/'tools/Windows/cc65/bin/cl65.exe',root/'build/smb-crossover-mmc5-expanded.nes',Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')]:bind(f)
 assert sha(root/'build/smb-crossover-mmc5-expanded.nes')==sha(Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes'))=='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
 bind(a.report);shutil.copy2(a.report,a.output/a.report.name)
 q=dict(source_CPU_readiness_passed=True,native_run=False,native_qualified=False,adopted=False,goal_complete=False,ROM_sha256=SHA,parent_v11_sha256='64f454a248785ff4c53bd0d52158fd2cf5389de38e5c35a888c3e6a6ed982362',production_unchanged_sha256='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363',receipts={n:dict(path=str(f.resolve()),sha256=sha(f))for n,f in paths.items()},counts=dict(capture_model=2016,gateway=2304,protocol=28899,final_guard=4884,lag_NMI=638),source_owner_bindings=source_notes,capture_only_extra_cycles=13,ROM_delta_bytes=22,all_v11_addresses_CHR_exact=True,v11_completed_native_assertion_controls=7,v11_visual_passed=False,VicHard_not_launched=True,HOST_FAILURE_RETRY=True,report_sha256=sha(a.report),tool_sha256=sha(Path(__file__)),limits='Finite source/CPU proposal only. New I/O is intentional and separately tested; old exact-I/O or native receipts are not relabeled. Await one initial OctopusEasy native control and ROOT actual-frame review before other controls. All lifecycle/DMC/crowding/global goals remain open.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');bind(a.output/'proof.json');(a.output/'manifest.json').write_text(json.dumps(dict(bindings=bindings),indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(ready=True,native_run=False,bindings=len(bindings),proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json')),indent=2))
if __name__=='__main__':main()
