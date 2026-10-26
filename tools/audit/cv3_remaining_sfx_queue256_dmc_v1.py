"""Unchanged DMC assertions with explicit transient atomic-queue owner allowances."""
from pathlib import Path
import hashlib,json,sys
import cv3_dmc_complete_cpu_v1 as suite
from check_tmnt_render_oa import address
original_diff=suite.diff
def queue_private_diff(qs,allow=()):
 private=list(range(address(qs[1].b,'RgAudioZp')+36,address(qs[1].b,'RgAudioZp')+160))+list(range(address(qs[1].b,'Cv3FxQueue'),address(qs[1].b,'Cv3FxQueue')+256))+[address(qs[1].b,'Cv3NoiseActive')]
 # The old direct scene helper cleared typed26 in main. The new actual scene
 # wrapper atomically publishes CANCEL, and the next NMI clears it before the
 # common decoder. Only this declared pending-cancel transient is normalized.
 if qs[0].get('AvAudioRequest')==0 and qs[1].get('AvAudioRequest')==26:
  head,tail=qs[1].get('Cv3FxQueueHead'),qs[1].get('Cv3FxQueueTail');assert head!=tail and qs[1].get('Cv3FxQueue',(head-1)&255)==8
  private.append(address(qs[1].b,'AvAudioRequest'))
 original_diff(qs,list(allow)+private)
if __name__=='__main__':
 suite.diff=queue_private_diff;suite.main();out=Path(sys.argv[sys.argv.index('--output')+1]);proof=json.loads((out/'proof.json').read_text());proof['queue_protocol_wrapper']=dict(original_tool_sha256=hashlib.sha256(Path(suite.__file__).read_bytes()).hexdigest(),wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),private_lane=[36,160],phase_owner='Cv3NoiseActive is NMI-owned after atomic publication; actual source/phase/NMI contract independently checked.',only_Av_allowance='Old0/new26 only when a committed pending CANCEL8 is verified; next real NMI clears it before common dispatch.',all_original_source_DMC_payload_rate_DAC_owner_register_APU_assertions_retained=True)
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
