"""Distinct private native proxy/typed-contact successor; never write a ROM."""
import json,re
from pathlib import Path
import prepare_bubble_bobble_common_cold_1102_v4 as P
from check_tmnt_render_oa import address,location
R=P.R;O=P.O


def frozen(name):
 q=json.loads((O/'native-ingress-qualified-1102-v4.json').read_text());p=R/name
 assert P.sha(p.read_bytes())==q['files'][name]['SHA256'],name
 return p.read_text()


def main():
 b=P.scoped_load(P.ROM);assert P.sha(b['raw'])==P.PIN
 source=frozen('build/bubble-bobble-source-1101-v1/native-policy-leaves.s').replace('BbReject=$a06f','BbReject=$a072')
 source=f'EnemyGraphicsEngine=${address(b,"EnemyGraphicsEngine"):04x}\nBank_EnemyGraphicsEngine=${((location(b,"EnemyGraphicsEngine")-16)//8192)|128:02x}\n'+source
 # The native self-secondary flag suppresses all native physics/contact;
 # native positive spawn publication is also a fresh actor identity boundary.
 start=source.index('BbNativeActorBirth:\n');end=source.index('BbNativeProxyCapture:\n',start)
 source=source[:start]+'BbNativeActorBirth=BbNativeFreshDone ; no native hook is needed\n\n'+source[end:]
 source=source.replace('.segment "BB_ACTOR_HOLE"','.segment "BB_HOST"')
 old=''' txa
 asl
 tax
 lda $c310,x
 sta $c323,y
 lda $c311,x
 sta $c324,y
 ldx $c3c0
 lda #1
 sta $c320,y                 ; Publish only after all association fields.
'''
 new=''' stx ObjectOffset
 stx $c3ed
 lda #<EnemyGraphicsEngine
 sta $c3ea
 lda #>EnemyGraphicsEngine
 sta $c3eb
 lda #Bank_EnemyGraphicsEngine
 sta $c3ec
 jsr BbNativeCallService     ; Generate a genuine native victim pose once.
 ldx $c3c0
 txa
 ora #$80
 sta Enemy_Flag,x            ; Native self-secondary proxy: no AI/contact.
 txa
 asl
 asl
 asl
 asl
 tay
 lda #1
 sta $c320,y                 ; Publish only after art/flag/native fields.
'''
 assert source.count(old)==1;source=source.replace(old,new)
 old=''' lda Enemy_Flag,x
 beq BbNativeInvalidProxy
 cmp $c322,y
 bne BbNativeInvalidProxy
'''
 new=''' txa
 ora #$80
 cmp Enemy_Flag,x
 bne BbNativeInvalidProxy
'''
 assert source.count(old)==1;source=source.replace(old,new)
 start=source.index(' txa\n asl\n tay\n lda $c310,y',source.index('BbNativeValidateProxy:'))
 end=source.index(' sec\n rts\n',start);source=source[:start]+source[end:]
 old='BbNativeProxyRestore:\n jsr BbNativeValidateProxy\n bcc BbNativeProxyNo\n'
 assert source.count(old)==1;source=source.replace(old,old+' lda $c322,y\n sta Enemy_Flag,x\n')
 old='BbNativeProxyOutPop:\n ldx $c3c0\n'
 assert source.count(old)==1;source=source.replace(old,'BbNativeProxyOutPop:\n ldx $c3c0\n jsr BbNativeProxyRestore    ; Restore the positive native flag before defeat.\n ldx $c3c0\n')
 old='BbRelaxNative16:\n jmi BbNativeProxyEmpty\n'
 assert source.count(old)==1;source=source.replace(old,'BbRelaxNative16:\n bpl BbNativeProxyFlagReady\n jsr BbNativeValidateProxy\n jcc BbNativeProxyEmpty\nBbNativeProxyFlagReady:\n')
 old='BbRelaxNative33:\n jmi BbNativeNo\n'
 assert source.count(old)==1;source=source.replace(old,'BbRelaxNative33:\n bpl BbNativeBodyFlagReady\n jsr BbNativeValidateProxy\n jcs BbNativeBodyDone\n jmp BbNativeNo\nBbNativeBodyFlagReady:\n')
 # All global short branches are re-relaxed after the source layout changes.
 source=re.sub(r'(?m)^(\s*)b(eq|ne|cc|cs|mi|pl|vc|vs) ([A-Za-z_]\w*)',r'\1j\2 \3',source)
 defined=set(re.findall(r'(?m)^([A-Za-z_]\w*)[:=]',source))
 def exports(m):return '.export '+','.join(n for n in m[1].split(',')if not n.startswith('BbRelaxNative')or n in defined)
 source=re.sub(r'(?m)^\.export ([^\n]+)$',exports,source)
 source+='\n.export BbNativeProxyFlagReady,BbNativeBodyFlagReady,BbNativeFullBox\nBbNativeFullBox:\n jsr BbNativeIn             ; Native scroll has already advanced its camera.\n jsr BbNativeBoxes\n ldx #3\nBbNativeFullBoxCopy:\n lda $c3b0,x\n sta BoundingBox_UL_Corner,x\n dex\n bpl BbNativeFullBoxCopy\n sec\n rts\nBbNativeProxyEnd:\n.export BbNativeProxyEnd,BbNativeFullBoxCopy\n'
 # Mark every named native branch for the same exact short-branch relaxation.
 branches=[]
 def mark(m):
  n=f'BbProxyRelax{len(branches)}';branches.append((n,m[2],m[3]));return n+':\n'+m[0]
 source=re.sub(r'(?m)^(\s*)j(eq|ne|cc|cs|mi|pl|vc|vs) ([A-Za-z_]\w*)[^\n]*',mark,source)
 source+='\n.export '+','.join(sorted(set([n for n,_,_ in branches]+[t for _,_,t in branches])))+'\n'
 cfg=frozen('build/bubble-bobble-source-1101-v1/native-policy-leaves.cfg').replace('native-policy-','native-proxy-').replace('size=$b00','size=$1800')
 for iteration in range(8):
  lab=P.assemble('native-proxy-leaves',source,cfg);changes=[]
  for name,cond,target in branches:
   old=name+':\n j'+cond+' '+target
   if old in source and -128<=lab[target]-(lab[name]+2)<=127:changes.append((old,name+':\n b'+cond+' '+target))
  if not changes:break
  for old,new in changes:source=source.replace(old,new,1)
 else:raise AssertionError('native proxy relaxation convergence')
 body=(O/'native-proxy-leaves.bin').read_bytes();assert lab['BbNativeProxyEnd']<=0xbfe0
 helpers=frozen('build/bubble-bobble-source-1101-v1/native-policy-helpers.s')
 for name in['BbNativeFresh','BbNativeDraw','BbNativeActor','BbNativeHurtChoose']:helpers=re.sub(name+r'=\$[0-9a-f]+',f'{name}=${lab[name]:04x}',helpers)
 h=P.assemble('native-proxy-helpers',helpers,'MEMORY{H:start=$d320,size=$e0,file=%O;}SEGMENTS{BB_HELPERS:load=H,type=ro;}')
 helper=(O/'native-proxy-helpers.bin').read_bytes();image=bytearray((O/'component.bin').read_bytes())
 image[0x1540:0x1540+len(body)]=body
 for off,name in[(0xb0,'native-proxy-box-hole.bin'),(0x153a,'native-proxy-sound-hole.bin')]:
  part=(O/name).read_bytes();assert image[off:off+len(part)]==bytes([255])*len(part);image[off:off+len(part)]=part
 # A06F is the dedicated38th row. Its old reject moves to A072; moving Actor
 # into the freed main body leaves all original source A100..B53A untouched.
 image[0x6f:0x80]=bytes([255])*17;image[0x72:0x74]=bytes.fromhex('1860')
 core=P.P.labels(O/'component.lbl');imports=json.loads((O/'component-layout.json').read_text())['imports']
 normal=set(json.loads((O/'native-leaves-layout.json').read_text())['actual_6502_import_bindings'])
 for row in imports:
  name=row['name'];target=lab['BbNative'+name]if name in['Tile23','Tile84','Sound','EnemyDraw']else(0xa073 if name in normal else 0xa072)
  at=row['vector']-0xa000;image[at:at+3]=bytes([76,target&255,target>>8])
 labels={**lab,**h};old=json.loads((O/'native-policy-layout.json').read_text());vectors={int(r):z['name']for r,z in old['vectors'].items()if int(r)!=11}
 vectors.update({10:'NativeHead',14:'NativeSide',16:'BbNativeFullBox',37:'BbNativeBodyContact'});labels.update(NativeHead=address(b,'BlockBufferColli_Head'),NativeSide=address(b,'BlockBufferColli_Side'))
 for row in range(38):
  target=labels[vectors[row]]if row in vectors else 0xa072
  image[3*row:3*row+3]=bytes([76,target&255,target>>8])
 art=(O/'component-native.chr').read_bytes()[:800]+helper+bytes(224-len(helper))
 (O/'native-proxy.bin').write_bytes(image);(O/'native-proxy-helper.chr').write_bytes(art)
 cookie=bytes([0xa7,39,1])+bytes.fromhex(P.sha(image+art))[:13];(O/'native-proxy-BB-cookie.bin').write_bytes(cookie)
 owner=frozen('build/bubble-bobble-source-1101-v1/native-policy-owner.s').replace('"native-policy-BB-cookie.bin"','"native-proxy-BB-cookie.bin"')
 owner=re.sub(r'BbNativeRetire=\$[0-9a-f]+',f'BbNativeRetire=${lab["BbNativeRetire"]:04x}',owner)
 own=P.assemble('native-proxy-owner',owner,'MEMORY{P:start=$ae00,size=$1000,file=%O;}SEGMENTS{COMMON_OWNER_PROPOSAL:load=P,type=ro;}')
 routes=frozen('build/bubble-bobble-source-1101-v1/common-routes.s');assert routes.count(' cmp #111')==1;routes=routes.replace(' cmp #111',' cmp #114')
 routes+='\n.segment "EX_DISPATCH"\n.export BbTypedDispatch\nBbTypedDispatch:\n lda SafecallA_SMC+1          ; Typed selector overwrote A, not the native frame.\n jmp ExDispatch\n.segment "BB_TYPED_CONTACT"\n.export BbTypedContact\nBbTypedContact:\n lda #$fb\n sta FarcallJmpTarget_SMC+1\n jmp BbTypedDispatch\n'
 rcfg=frozen('build/bubble-bobble-source-1101-v1/common-routes.cfg').replace('common-route-','native-proxy-route-')
 rcfg=rcfg.replace('SEGMENTS{','MEMORY{TYP:start=$b029,size=8,file="'+(O/'native-proxy-typed-contact.bin').as_posix()+'";}SEGMENTS{BB_TYPED_CONTACT:load=TYP,type=ro;')
 rr=P.assemble('native-proxy-routes',routes,rcfg)
 contact=frozen('build/bubble-bobble-source-1101-v1/native-contact-gate.s').replace('BbBodyVeneer=$b0ad','BbBodyVeneer=$b029')
 P.assemble('native-proxy-contact-gate',contact,'MEMORY{P:start=$bf03,size=49,file=%O;}SEGMENTS{BB_CONTACT_GATE:load=P,type=ro;}')
 # The native lower fixed-ROM head/side leaves are directly callable from
 # the private vector; they require no new service glue or physical carrier.
 assert all(0x8000<=labels[n]<0xa000 for n in['NativeHead','NativeSide'])
 ports='''.setcpu "6502"
.segment "BB_SHOT_PORT"
.export BbShotPort,BbBBoxPort
BbShotPort:
 php
 pha
 lda SelectedCharacter
 cmp #39
 beq BbNoNativeShot
 lsr
 cmp #18
 bne BbLegacyShot
BbNoNativeShot:
 pla
 plp
 rts
BbLegacyShot:
 pla
 plp
 ; Incoming A is already the actual outer farcall's SafecallA_SMC.
 lda #$bc
 sta FarcallJmpTarget_SMC+1
 lda #$bb
 sta FarcallJmpTarget_SMC+2
 lda #$ce
 jmp FarCallCommon
.segment "BB_BBOX_PORT"
BbBBoxPort:
 php
 lda SelectedCharacter
 cmp #36
 beq BbExtendedBBox
 cmp #39
 beq BbExtendedBBox
 plp
 jmp BoundingBoxCore
BbExtendedBBox:
 plp
 ; Both source box callbacks receive incoming A from the real outer SMC.
 lda #<HuFullBox
 sta FarcallJmpTarget_SMC+1
 lda #>HuFullBox
 sta FarcallJmpTarget_SMC+2
 lda #$cf
 jsr FarCallCommon
 bcs BbBBoxDone
 jmp BoundingBoxCore
BbBBoxDone:
 rts
'''
 ports=''.join(f'{n}=${address(b,n):04x}\n'for n in['SelectedCharacter','FarcallJmpTarget_SMC','FarCallCommon','BoundingBoxCore','HuFullBox'])+ports
 pp=P.assemble('native-proxy-ports',ports,'MEMORY{S:start=$adb6,size=34,file=%O;B:start=$add8,size=38,file="'+(O/'native-proxy-bbox.bin').as_posix()+'";}SEGMENTS{BB_SHOT_PORT:load=S,type=ro;BB_BBOX_PORT:load=B,type=ro;}')
 q=dict(passed=True,ROM_written=False,shared_source_written=False,base_ROM_SHA256=P.PIN,code_end=lab['BbNativeProxyEnd'],code_spare=0xbfe0-lab['BbNativeProxyEnd'],helper_bytes=len(helper),helper_spare=224-len(helper),labels=labels,owner_labels=own,route_labels=rr,port_labels=pp,BB_cookie=cookie.hex(),vectors={r:dict(name=n,target=labels[n])for r,n in vectors.items()},typed_contact=dict(row=37,private_entry=0xa06f,resident_entry=0xb029,virtual_veneer=0xb0fb,virtual_veneer_not_executed=True,legacy_HuBody11_rejects=True),native_secondary_proxy=dict(flag='80|own-slot',original_flag_saved=True,no_new_shared_AI_or_birth_hooks=True,positive_spawn_invalidates=True),source_funded_native_ports=dict(existing_half_open=[0xadb6,0xae00],shot_half_open=[0xadb6,0xadd8],bbox_half_open=[0xadd8,0xadfe],spare=2,granted=False),scope='Compiled distinct successor only. Native suspension/art/timeout/pop/retire/spawn and complete Main/foreign/ISR qualification remain required. No ROM/shared routing/menu change.')
 (O/'native-proxy-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','code_spare','helper_bytes','helper_spare','ROM_written']}))


if __name__=='__main__':main()
