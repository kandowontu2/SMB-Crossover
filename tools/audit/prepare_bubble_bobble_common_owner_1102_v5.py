"""Measure complete cold/auth/retirement source before requesting grants."""
import json,hashlib
import prepare_bubble_bobble_common_cold_1102_v4 as P
from check_tmnt_render_oa import address,location
R=P.R;O=P.O


def main():
 b=P.scoped_load(P.ROM);assert P.sha(b['raw'])==P.PIN
 old=json.loads((O/'common-cold-layout.json').read_text());kernel=old['split_pad_proposal']['labels'];bb=P.P.labels(O/'native-leaves.lbl')
 image=(O/'native-private.bin').read_bytes();art=(O/'native-helper.chr').read_bytes()
 cookie=bytes([0xa7,39,1])+hashlib.sha256(image+art).digest()[:13];(O/'common-BB-cookie.bin').write_bytes(cookie)
 names=['R0','R1','R2','R3','R4','R5','R6','R7','CurrentBankC','SelectedCharacter','ReloadCHRBank','OperMode','FamilyMainCommit','DisableScreenFlag','Mirror_PPUMASK','Mirror_PPUCTRL','NmiDisable','NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC','FarCallCommon','X5PublishChr','HorizontalScroll','VerticalScroll']
 definitions='.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${address(b,n):04x}\n'for n in names)
 definitions+=f'Bank_X5PublishChr=${((location(b,"X5PublishChr")-16)//8192)|128:02x}\n'
 definitions+=f'CoWorker=${kernel["BbColdWorker"]:04x}\nCoExDescriptor=${kernel["BbColdExDescriptor"]:04x}\nCoBBDescriptor=${kernel["BbColdBBDescriptor"]:04x}\nBbNativeRetire=${bb["BbNativeRetire"]:04x}\nShRetire=$a849\n'
 labels=P.assemble('common-owner',definitions+'.include "bubble_bobble_common_owner_1102_v5.inc"\n','MEMORY{P:start=$ae00,size=$1000,file=%O;}SEGMENTS{COMMON_OWNER_PROPOSAL:load=P,type=ro;}')
 blob=(O/'common-owner.bin').read_bytes();kernelbytes=old['split_pad_proposal']['total_bytes'];available=556+247
 q=dict(passed=True,proposal_only=True,ROM_written=False,shared_source_written=False,resident_granted=False,ROM_SHA256=P.PIN,owner_frame_bytes=len(blob),copy_kernel_with_two_descriptors=kernelbytes,total_bytes=len(blob)+kernelbytes,source_funded_available=available,fit=len(blob)+kernelbytes<=available,unfunded_bytes=max(0,len(blob)+kernelbytes-available),remaining_for_shared_routing=max(0,available-len(blob)-kernelbytes),raw39_proposed_only=True,Prince_not_supported=True,no_extra_RAM=True,labels=labels,BB_cookie=cookie.hex(),source_SHA256=P.sha(blob),ABI='CoCold/CoRetire preserve AXYP,R0..7,Cmapping,reloadCHR and five live SMC operands; cold returns Csuccess, retire preserves C. CoCheckCode is private C-only with R0..7/Cmapping preserved. Both full16Bheaders checked. BB foreign retirement calls genuine compiled private retire before header invalidation or overwrite. CoCold guards exact forcedblank boundary; RAM2byte0 finalcommit after full8192copy/verify.',remaining=['CPU prove all warm/cold/header poisons/foreign retire and interrupt cuts.','Place and source-bind every relocated Ex public entry/cookie/SMC-table consumer before any shared edit.','Shared service/scene/menu/raw39 routing is not included in this cold/auth/retirement byte count.','Prince packed layout needs its own typed worker/descriptor; it is not claimed supported by this page worker.'])
 (O/'common-owner-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','owner_frame_bytes','copy_kernel_with_two_descriptors','total_bytes','source_funded_available','fit','unfunded_bytes','remaining_for_shared_routing']}))


if __name__=='__main__':main()
