"""Freeze the finite source/CPU HUD successor readiness; no native acceptance."""
from pathlib import Path
import argparse,hashlib,json,shutil
SHA='64f454a248785ff4c53bd0d52158fd2cf5389de38e5c35a888c3e6a6ed982362'
BASE='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--root-chunk',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 root=Path(__file__).resolve().parents[2];candidate=a.base/'hud-candidate-v11';assert sha(candidate/'candidate.nes')==SHA
 paths={
  'layout':candidate/'proof.json',
  'protocol':a.base/'hud-protocol-cpu-v4/proof.json',
  'final_guard':a.base/'hud-final-guard-cpu-v3/proof.json',
  'lag_NMI':a.base/'hud-nmi-cpu-v4/proof.json',
  'whole_NMI_prefix':a.base/'hud-whole-nmi-cpu-v6/proof.json',
  'no_pending_gateway':a.base/'hud-gateway-cpu-v1/proof.json',
  'source_owners':a.base/'hud-owner-v4/proof.json',
  'ROOT_chunk_full_return':a.root_chunk/'proof.json',
 }
 proofs={n:json.loads(f.read_text())for n,f in paths.items()}
 for n,q in proofs.items():
  if n=='layout':assert q['prepared'] and q['after_sha256']==SHA and q['before_sha256']==BASE and q['CHR_bytes_exact'] and q['all_old_symbols_exact']
  elif n=='source_owners':assert q['source_review_passed']
  else:assert q['passed'] and q.get('ROM_sha256',q.get('candidate_ROM_sha256'))==SHA,(n,q)
 bound={}
 def bind(f):
  f=f.resolve();assert f.is_file(),f;bound[str(f)]=dict(bytes=f.stat().st_size,sha256=sha(f))
 for f in paths.values():bind(f)
 for f in candidate.glob('candidate.*'):
  if f.is_file():bind(f)
 bind(candidate/'sourcepatch.patch');bind(a.report);bind(Path(__file__))
 for rel in proofs['layout']['changed_source']:bind(candidate/'source'/rel)
 for rel in proofs['source_owners']['bindings']:bind(candidate/'source'/rel)
 for folder in ['hud-protocol-cpu-v4','hud-final-guard-cpu-v3','hud-gateway-cpu-v1']:
  bind(a.base/folder/'cases.json')
 bind(a.root_chunk/'cases.json')
 for name in ['mmc3','mmc5']:
  f=a.base/'hud-flagoff-v4'/f'{name}.nes';g=a.base/'hud-flagoff-v3'/f'{name}.nes';assert f.read_bytes()==g.read_bytes();bind(f);bind(g);bind(f.with_suffix('.build.json'))
 # Earlier outputs stay immutable. Bind failures and superseded diagnostics
 # without turning them into passing qualification results.
 for rel in ['nmi-fast-packet-v1/proof.json','candidate-modes-v1/proof.json','candidate-failure-diagnostic-v1/proof.json','broad-budget-v1/genuine-failing-packets.json','hud-abi-negative-v1/proof.json','hud-final-guard-cpu-v1/failure.json','hud-owner-v3/failure.txt','hud-owner-v3/failed-tool.py','hud-whole-nmi-cpu-v4/proof.json','hud-candidate-v9/proof.json','hud-candidate-v10/proof.json']:
  bind(a.base/rel)
 for name in ['parodius_visibility_hud_candidate_v1.py','parodius_visibility_hud_cpu_v1.py','parodius_visibility_hud_guard_cpu_v1.py','parodius_visibility_hud_nmi_cpu_v1.py','parodius_visibility_hud_nmi_budget_v1.py','parodius_visibility_hud_gateway_cpu_v1.py','parodius_visibility_hud_owner_v1.py','parodius_visibility_hud_packet_v1.py','parodius_visibility_hud_design_v1.py','check_nmi_vram_fast_cpu_v1.py','check_nmi_chunk_arithmetic_v2.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py']:
  f=root/'tools/audit'/name;bind(f);dest=a.output/'tools'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(f,dest)
 shutil.copy2(a.report,a.output/a.report.name)
 q=dict(source_CPU_readiness_passed=True,native_run=False,native_qualified=False,adopted=False,goal_complete=False,baseline_ROM_sha256=BASE,candidate_ROM_sha256=SHA,
  receipts={n:dict(path=str(f.resolve()),sha256=sha(f))for n,f in paths.items()},
  counts=dict(protocol=proofs['protocol']['total_cases'],final_guard=proofs['final_guard']['cases'],lag_NMI_instruction_boundaries=proofs['lag_NMI']['actual_compiled_NMI_cases'],no_pending_gateway=proofs['no_pending_gateway']['cases'],ROOT_chunk_full_return=proofs['ROOT_chunk_full_return']['cases']),
  layout=dict(installed_symbols_exact=proofs['layout']['old_symbols'],CHR_exact=True,ROM_differing_bytes=proofs['layout']['differing_bytes'],changed_source=list(proofs['layout']['changed_source'])),
  global_empty_nonship_NMI_extra_cycles=9,
  limits=['Source/CPU components only; numeric Easy/Hard controls here are6 isolated setup cases, not native mode coverage. Gateway OperMode0/1 means menu/game.',
  'Whole-NMI prefix ends after STA4014 instruction and excludes513/514-cycle hardware DMA, NMI-entry latency/jitter, PPU evaluation/IRQ timing and DMC stalls.',
  'First HUD publication and dirty attrs intentionally defer when combined extent is unsafe; native bounded delay/starvation, cold/menu/area/death/reset/font and Buffer2 behavior remain gates.',
  'Finite final-guard tests cover valid packets through83B and ordered native suffix/prefix retention; they do not certify arbitrary producer overflow or every<=31B packet deadline.',
  'The original copy-only cf0f candidate remains rejected with4/6 native controls. Original50b5 OAM/DMA failures remain negative evidence.',
  'Octopus crowded body dropout and Sophia overlap remain open; no BODY record/art/priority change was made.'],
  tool_sha256=sha(Path(__file__)),report_sha256=sha(a.report))
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');bind(a.output/'proof.json');bind(a.output/a.report.name)
 manifest=dict(binding_count=len(bound),bindings=bound)
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(ready=True,native_run=False,proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bound),counts=q['counts']),indent=2))
if __name__=='__main__':main()
