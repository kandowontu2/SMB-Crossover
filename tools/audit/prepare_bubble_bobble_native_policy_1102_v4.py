"""Private successor of the frozen native core; no shared or ROM mutation."""
import json,re
from pathlib import Path
import prepare_bubble_bobble_common_cold_1102_v4 as P
R=P.R;O=P.O


def main():
 freeze=json.loads((O/'qualified-native-proofs-1102-v1.json').read_text())
 def frozen(name):
  p=R/name;assert P.sha(p.read_bytes())==freeze['files'][name]['SHA256'];return p.read_text()
 source=frozen('build/bubble-bobble-source-1101-v1/native-leaves.s')
 # Native $14 is FlyingCheepCheep; genuine powerups have ID$2E. The source
 # <21 normal-enemy domain already excludes powerups from bubble proxies.
 old=' cmp #$14\nBbRelaxNative19:\n jeq BbNativeProxyEmpty\n';assert source.count(old)==1
 source=source.replace(old,'BbRelaxNative19:\n')
 old=' cmp #$14\nBbRelaxNative34:';assert source.count(old)==1
 source=source.replace(old,' cmp #$2e\nBbRelaxNative34:')
 old=' bcs BbNativeBodyDone\n lda $c300\n';assert source.count(old)==1
 source=source.replace(old,' bcs BbNativeBodyDone\nBbNativeHurtChoose:\n lda $c300\n')
 source+='\n.export BbNativeFreshDone,BbNativeActor,BbNativeHurtChoose,BbPolicyStatus,BbPolicyEnd\nBbPolicyStatus:\n lda #1\n tax\n rts\nBbPolicyEnd:\n'
 cfg=frozen('build/bubble-bobble-source-1101-v1/native-leaves.cfg').replace('native-actor-hole.bin','native-policy-actor-hole.bin').replace('native-box-hole.bin','native-policy-box-hole.bin').replace('native-sound-hole.bin','native-policy-sound-hole.bin')
 lab=P.assemble('native-policy-leaves',source,cfg);body=(O/'native-policy-leaves.bin').read_bytes()
 assert lab['BbPolicyEnd']<=0xbfe0
 helpers=frozen('tools/reference/bubble_bobble_helpers_1102_v1.inc')
 helpers+='''
.export BbPolicyInjury,BbPolicyAdder,BbPolicyBox,BbPolicyHelpersEnd
BbPolicyInjury:
 jsr BbNativeActor
 jmp BbNativeHurtChoose
BbPolicyAdder:
 ldy #2
 sec
 rts
BbPolicyBox:
 ldy #1
 rts
BbPolicyHelpersEnd:
'''
 # Reuse exact frozen native addresses; no dependency on historical trees.
 prefix=frozen('build/bubble-bobble-source-1101-v1/native-leaves.s').split('.segment "BB_HOST"')[0]
 definitions='.setcpu "6502"\n'
 from check_tmnt_render_oa import address
 b=P.scoped_load(P.ROM);assert P.sha(b['raw'])==P.PIN
 for n in['CurrentCHRBank','X5ChrMode','SsChrActive','ObjectMetasprite','SmPosePtr','X5WideChrActive','ReloadCHRBank','OperMode','R0','VRAM_Buffer1_Offset','VRAM_Buffer1']:definitions+=f'{n}=${address(b,n):04x}\n'
 for n in['BbNativeFresh','BbNativeDraw','BbNativeActor','BbNativeHurtChoose']:definitions+=f'{n}=${lab[n]:04x}\n'
 h=P.assemble('native-policy-helpers',definitions+helpers,'MEMORY{H:start=$d320,size=$e0,file=%O;}SEGMENTS{BB_HELPERS:load=H,type=ro;}')
 helper=(O/'native-policy-helpers.bin').read_bytes();assert len(helper)<=224
 image=bytearray((O/'component.bin').read_bytes());image[0x1540:0x1540+len(body)]=body
 for off,name in[(0x71,'native-policy-actor-hole.bin'),(0xb0,'native-policy-box-hole.bin'),(0x153a,'native-policy-sound-hole.bin')]:
  part=(O/name).read_bytes();assert image[off:off+len(part)]==bytes([255])*len(part);image[off:off+len(part)]=part
 core=P.P.labels(O/'component.lbl');old=json.loads((O/'native-leaves-layout.json').read_text())
 for name in old['actual_6502_import_bindings']:
  target=lab['BbNative'+name]if name in['Tile23','Tile84','Sound','EnemyDraw']else core['BbReject']+1
  at=core['BbImport'+name]-0xa000;image[at:at+3]=bytes([76,target&255,target>>8])
 vectors={0:'BbNativeUpdate',1:'BbHelperGraphics',2:'BbNativeDraw',5:'BbPolicyInjury',6:'BbPolicyStatus',9:'BbNativeFreshDone',11:'BbNativeBodyContact',12:'BbPolicyAdder',13:'BbPolicyBox',15:'BbNativeFresh',16:'BbNativeContactBox',17:'BbHelperPortrait',18:'BbHelperName',23:'BbNativeFreshDone',26:'BbHelperColors',30:'BbHelperName',34:'BbNativeFreshDone',36:'BbNativeFresh'}
 all_labels={**lab,**h}
 for row,name in vectors.items():
  target=all_labels[name];image[3*row:3*row+3]=bytes([76,target&255,target>>8])
 assert image[lab['BbNativeFreshDone']-0xa000:lab['BbNativeFreshDone']-0xa000+2]==bytes.fromhex('3860')
 art=(O/'component-native.chr').read_bytes()[:800]+helper+bytes(224-len(helper))
 (O/'native-policy.bin').write_bytes(image);(O/'native-policy-helper.chr').write_bytes(art)
 cookie=bytes([0xa7,39,1])+bytes.fromhex(P.sha(image+art))[:13];(O/'native-policy-BB-cookie.bin').write_bytes(cookie)
 owner=frozen('build/bubble-bobble-source-1101-v1/common-owner.s')
 owner=re.sub(r'BbNativeRetire=\$[0-9a-f]+',f'BbNativeRetire=${lab["BbNativeRetire"]:04x}',owner)
 include=frozen('tools/reference/bubble_bobble_common_owner_1102_v5.inc').replace('"common-BB-cookie.bin"','"native-policy-BB-cookie.bin"')
 assert '.include "bubble_bobble_common_owner_1102_v5.inc"'in owner
 owner=owner.replace('.include "bubble_bobble_common_owner_1102_v5.inc"',include)
 own=P.assemble('native-policy-owner',owner,'MEMORY{P:start=$ae00,size=$1000,file=%O;}SEGMENTS{COMMON_OWNER_PROPOSAL:load=P,type=ro;}')
 q=dict(passed=True,ROM_written=False,shared_source_written=False,base_ROM_SHA256=P.PIN,source_native_freeze=freeze['archive_SHA256'],code_end=lab['BbPolicyEnd'],code_spare=0xbfe0-lab['BbPolicyEnd'],helper_bytes=len(helper),helper_spare=224-len(helper),private_image_SHA256=P.sha(image),art_helper_SHA256=P.sha(art),BB_cookie=cookie.hex(),owner_labels=own,vectors={row:dict(name=name,target=all_labels[name])for row,name in vectors.items()},labels=all_labels,original_donor_component_unchanged=True,actual_native_powerup_ID=46,source_supported_normal_enemy_20_restored=True,scope='Compiled private policy successor only. Bindings for actual body/injury/status/visibility/geometry/pickup/weapon-tail contracts require CPU ingress tests. Native shot-bank/fullbox override, head/side forwarding, AI/birth routing, actual Main/menu admission remain absent.')
 (O/'native-policy-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','code_spare','helper_bytes','helper_spare','ROM_written']}))


if __name__=='__main__':main()
