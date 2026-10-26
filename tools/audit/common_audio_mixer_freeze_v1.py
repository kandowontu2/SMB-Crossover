"""Freeze independently guarded current3b common-audio proposal, source only."""
from pathlib import Path
import argparse,json,sys
from smb3_host_current3b_cpu_v1 import D,R,sha,put
from smb3_host_current3b_freeze_v1 import dependencies

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--qualified',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);candidate='f4efd9ccb222501877dfc77c5189841aa9dc500756736f15aaf02a6994ae8c0f';assert sha(a.packet/'candidate.nes')==sha(a.qualified/'candidate.nes')==candidate
 layout=json.loads((a.packet/'layout.json').read_text());base=Path(layout['parent_directory']);manifest=json.loads((a.packet/'source-manifest.json').read_text());parent=json.loads((base/'source-manifest.json').read_text());assert manifest.keys()==parent.keys();changed=[]
 for name,h in manifest.items():
  assert sha(a.packet/'source'/name)==h,name
  if h!=parent[name]:changed.append(name)
 assert sorted(changed)==['src/guest_audio.s','src/mmc5_sfx.s']
 receipts=[a.qualified/n for n in ['controls-v1/proof.json','roster-v1/proof.json','irq-v1/proof.json','whole-v1/proof.json']]+[a.packet/'build-controls-v1/proof.json',a.packet/'layout.json']
 for q in receipts:
  j=json.loads(q.read_text());assert j['passed']and j['ROM_sha256']==candidate,q
 cp=json.loads(receipts[0].read_text());rp=json.loads(receipts[1].read_text());ip=json.loads(receipts[2].read_text());wp=json.loads(receipts[3].read_text())
 assert sum(cp['cases'].values())==7344 and rp['full_AudioUpdate_calls']==9472 and rp['identities']==37 and ip['actual_IRQ_cases']==1072 and wp['calls']==768
 summary=dict(passed=True,source_only=True,native_run=False,native_granted=False,adopted=False,parent_ROM_sha256=layout['parent_ROM_sha256'],ROM_sha256=candidate,complete_source_files=len(manifest),changed_source_files=layout['changes'],changed_banks=layout['changed_banks'],all_other_banks_header_CHR_exact=True,all_public_entries_spans_preserved=True,genuine_private_moves=layout['genuine_private_moved_symbols'],qualification_same_literal_ROM_across_unguarded_and_guarded_sources=True,guarded_source_fresh_canonical_and_both_ordinary_exact=True,source_manifest_sha256=sha(a.packet/'source-manifest.json'),receipts=[dict(path=str(q).replace('\\','/'),sha256=sha(q))for q in receipts],counts=dict(caller_cases=7344,ordinary_full_AudioUpdate=9472,identities=37,actual_IRQ=1072,matched_whole_calls=768),ordinary_source_scope_failure=str(a.qualified/'ordinary-scope-v1/scope.json').replace('\\','/'),limits='CPU/source ready only, no native timing/PPU/APU waveform/campaign acceptance. Independent current3b two-file patch, no held SMB3 core/cache/data/clones imported.')
 put(a.packet/'proof.json',summary)
 starts=[R/'tools/audit'/n for n in ['common_audio_mixer_prepare_v1.py','common_audio_mixer_prepare_v2.py','common_audio_mixer_prepare_v3.py','common_audio_mixer_controls_v1.py','common_audio_mixer_roster_v1.py','common_audio_mixer_irq_v1.py','common_audio_mixer_whole_v1.py','common_audio_mixer_build_v1.py','common_audio_mixer_freeze_v1.py','smb3_host_mixer_profile_v1.py','smb3_host_sweep_profile_v1.py']]+[R/'tools/build_mmc5_expanded.py'];tools=dependencies(starts);report=R/'docs/qa/common-audio-mixer-source-2026-10-26.txt'
 files=[a.packet/'source'/n for n in manifest]+[a.packet/n for n in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','source-manifest.json','implementation.patch','proof.json','build-command.json']]+receipts+[a.qualified/n for n in ['candidate.nes','candidate.dbg','source-manifest.json','ordinary-scope-v1/scope.json']]+[base/n for n in ['candidate.nes','candidate.dbg','source-manifest.json']]+[base/'source'/n for n in changed]+[a.qualified/'source'/n for n in changed]+[D/'common-audio-mixer-current3b-v1/failure.json',D/'common-audio-mixer-current3b-v1/build-command.json',D/'smb3-host-mixer-profile-v1/proof.json',D/'smb3-host-sweep-profile-v1/proof.json',D/'smb3-host-current3b-native-ready-v1/native/smb3-music-native.jsonl',report,Path(sys.executable)]+tools
 files +=[D/'smb3-host-mixer-opt-v1'/n for n in ['layout.json','controls-v1/proof.json','roster-v1/proof.json','irq-v1/proof.json','whole-v1/proof.json']]
 files=sorted(set(q.resolve()for q in files));bindings=[dict(path=str(q).replace('\\','/'),sha256=sha(q),bytes=q.stat().st_size)for q in files]
 put(a.output/'readiness.json',summary|dict(source_component_ready=True,native_ready=False,report=str(report).replace('\\','/'),bindings=bindings,tools=[str(q).replace('\\','/')for q in tools],remaining=['One exact same-controller MegaEasy450 native regression vs actualcurrent3b must be prepared/reviewed/granted separately','No native frame cadence/render/PCM/SFX waveform/all-roster campaign acceptance','Earlier7469 actual98draw music deficit staysheld; independent shared patch does not depend on that integration'],freeze_tool_sha256=sha(__file__)))
 print(json.dumps(dict(passed=True,bindings=len(bindings),tools=len(tools),source_files=len(manifest),readiness_sha256=sha(a.output/'readiness.json'))))
if __name__=='__main__':main()
