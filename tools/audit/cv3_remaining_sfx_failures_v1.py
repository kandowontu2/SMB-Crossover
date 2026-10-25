"""Re-execute retained bad candidates and bind the first wrong source states."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load
from cv3_primary_sfx_source_v1 import Original,CV3
from cv3_remaining_sfx_complete_cpu_v1 import init,sound
from cv3_dmc_complete_cpu_v1 import apu
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-remaining-sfx-v1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
 f=D/'full-proposal-v2/candidate.nes';q=init(load(f));sound(q,0x13);assert q.get('AvAudioRequest')==27;sound(q,0x1f);assert q.get('AvAudioRequest')==128
 rows.append(dict(kind='Confirmed actual pending-request corruption',ROM=str(f),ROM_sha256=sha(f),actual_release_sequence=[0x13,0x1f],updates_between=0,first_wrong_state='AvAudioRequest=128 (owned-mask value) instead of26',unfixed_followon='RemainingAudioTick indexes outside typed request domain and reaches a ROM write',repair='TYA restores typed request; final independent pending voice IDs retain mixed source priority.'))
 f=D/'full-proposal-v5/candidate.nes';q=init(load(f));sound(q,0x24);o=Original(CV3.read_bytes());o.call(0xe227);o.call(0xe25f,a=0x24)
 for _ in range(12):q.invoke('AudioUpdate');o.call(0xe24e)
 sound(q,0x13);o.call(0xe25f,a=0x13);o.m.trace=[];o.call(0xe24e);q.invoke('AudioUpdate');actual=[v for at,v in apu(q)if at==0x400f];wanted=[r['value']for r in o.m.trace if r['address']==0x400f];assert actual==[8]and wanted==[13]
 rows.append(dict(kind='Confirmed raw source400F mismatch',ROM=str(f),ROM_sha256=sha(f),sequence=[0x24,12,0x13],actual400F=actual,original400F=wanted,repair='Retain actual shared source frequency-high state and process pulse before noise. Final441 pair and512 continued mixed raw tests include all bits; no masking.',original_trace=o.m.trace,target_trace=apu(q)))
 masked=D/'full-cpu-v4/diagnostic-masked-comparator.py';assert masked.exists()
 result=dict(passed=True,meaning='Retained failures reproduced, not passing gameplay',reproductions=rows,unaccepted_masked_comparator=dict(path=str(masked),sha256=sha(masked),root_rejected=True,final_raw_strict=True),other_retained_failures=['source-v1: wrong reference path before CPU','noise-proposal-v1: preparation text assertion before compile','noise-proposal-v2/noise-cpu-v1: wrong dagger/axe bit selector; original waveform data differed','noise-qualified-v1: missing declared scene-reset bank82 byte in expected changed-bank catalog','per-voice-plan-v1: incorrect assumption low source6 could not occupy an idle voice; corrected independent source priority','full-proposal-v1/full-proposal-v4: new-code branch distances rejected by assembler','full-qualified-v1: planned resident127 death-hook expectation corrected to actual bank2 UnionDeathStartCore operands','full-qualified-v2: CV_AUDIO segment starts in27 and spans28; corrected free-span bank metadata in v3'],scope='Actual assembled/source CPU only; all failed private trees retained. No installed/ROOT game source was involved.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,reproduced_failures=len(rows),proof_sha256=sha(a.output/'proof.json')),indent=2))
if __name__=='__main__':main()
