"""Compile only the explicitly granted immutable224B art tail."""
import json
from pathlib import Path
import prepare_bubble_bobble_common_cold_1102_v4 as P
from check_tmnt_render_oa import address
R=P.R;O=P.O


def build(bundle,native):
 grant=json.loads((R/'docs/qa/allocations/bubble-helper-row-1102-v2.json').read_text());assert grant['granted']
 assert P.sha(bundle['raw'])==P.PIN
 names=['CurrentCHRBank','X5ChrMode','SsChrActive','ObjectMetasprite','SmPosePtr','X5WideChrActive','ReloadCHRBank','OperMode','R0','VRAM_Buffer1_Offset','VRAM_Buffer1']
 source='.setcpu "6502"\n'+''.join(f'{n}=${address(bundle,n):04x}\n'for n in names)
 source+=''.join(f'{n}=${native[n]:04x}\n'for n in['BbNativeFresh','BbNativeDraw'])
 source+='.include "bubble_bobble_helpers_1102_v1.inc"\n'
 labels=P.assemble('native-helpers',source,'MEMORY{H:start=$d320,size=$e0,file=%O;}SEGMENTS{BB_HELPERS:load=H,type=ro;}')
 code=(O/'native-helpers.bin').read_bytes();assert len(code)<=224
 original=(O/'component-native.chr').read_bytes();assert len(original)==1024 and original[800:]==bytes(224)
 art=original[:800]+code+bytes(224-len(code));assert art[:800]==original[:800]
 (O/'native-helper.chr').write_bytes(art)
 q=dict(passed=True,base_ROM_SHA256=P.PIN,ROM_written=False,helper_bytes=len(code),helper_available=224,unused=224-len(code),execution_half_open=[0xd320,0xd320+len(code)],immutable_copied_row_half_open=[0xd000,0xd400],original_art_prefix_exact=True,original_art_prefix_SHA256=P.sha(original[:800]),complete_art_helper_SHA256=P.sha(art),labels=labels,actual_menu_name_contract=dict(address=0x2328,width=16,space=0x24,source='Actual current91-profile FmQueueName packets from frontend-closure.json'),scope='Immutable helpers only; no shared owner/menu admission. Portrait/name helpers require an authenticated loaded overlay; cold menu fallback remains frontend-owned.')
 (O/'native-helpers-layout.json').write_text(json.dumps(q,indent=2)+'\n');return labels


def main():
 b=P.scoped_load(P.ROM);native=P.P.labels(O/'native-leaves.lbl');build(b,native)
 q=json.loads((O/'native-helpers-layout.json').read_text());print(json.dumps({k:q[k]for k in['passed','helper_bytes','unused','ROM_written']}))


if __name__=='__main__':main()
