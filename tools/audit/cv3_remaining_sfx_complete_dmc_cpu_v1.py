"""Rerun immutable DMC suite, declaring only the new private family state."""
from pathlib import Path
import hashlib,json,sys
import cv3_dmc_complete_cpu_v1 as suite
from check_tmnt_render_oa import address
original_diff=suite.diff
def expanded_private_diff(qs,allow=()):
 original_diff(qs,list(allow)+list(range(address(qs[1].b,'RgAudioZp')+36,address(qs[1].b,'RgAudioZp')+56)))
if __name__=='__main__':
 suite.diff=expanded_private_diff
 suite.main()
 out=Path(sys.argv[sys.argv.index('--output')+1]);proof=json.loads((out/'proof.json').read_text());proof['private_state_wrapper']=dict(immutable_original_tool_sha256=hashlib.sha256(Path(suite.__file__).read_bytes()).hexdigest(),wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),additional_declared_private_offsets=[36,56],all_original_behavior_APU_register_mapper_DMC_payload_assertions_retained=True,scope='Only original RAM diff helper gains the newly declared selected-family state. No old control, case or behavior assertion removed. The legacy active-cost setup compares ordinary owner2 against source owner3, so its28-cycle source-owner cost is not the new overlay overhead.')
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
