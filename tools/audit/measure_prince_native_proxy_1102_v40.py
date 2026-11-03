"""Original guard-state/native1-1 actor proxy; unplaced CPU proposal only."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_cold_worker_1102_v19 as A
import prepare_prince_successor_manifest_1102_v26 as M
import check_prince_host_services_1102_v18 as H
from check_tmnt_render_oa import address,location
P,O=A.L.P,A.O


def main():
 base,_,_,_=M.bundle();core=P.T.labels(O/'contact-core.lbl');life=P.T.labels(O/'host-life-v12.lbl');services=P.T.labels(O/'host-services-v18.lbl')
 # Authenticated original action57, not a handmade guard animation. Only
 # coordinates/facing/native identity are imported after this constructor.
 d=P.machine();ram=bytearray(2048);ram[0x61c]=128;ram[0x69]=14;ram[0x6d1]=5;list.__setitem__(d.memory,slice(0,2048),ram);d.memory.switch(5);P.call(d,0x8730,a=57,y=14)
 for advance in range(16):
  d.a,d.x,d.y,d.p=0,14,0,0x21;d.sp=253;d.stPushWord(0x5ffe);d.pc=0xf158;P.until(d,0xf1a2,limit=10000)
  if d.memory[0x625]==171:break
 else:raise AssertionError('Original guard57 did not reach standing171')
 template=bytes(d.memory[0x61c:0x62a]);assert(template[8],template[9],template[10])==(57,171,1),template.hex()
 # Native TallBBox3 has an exact21px bottom offset; source standing guard
 # geometry has delta3. Importing native bottom minus source Origin therefore
 # matches the same physical floor and original +/-30px battle lane.
 at=location(base,'BoundBoxCtrlData')+12;assert base['raw'][at:at+4]==bytes([2,9,14,21]);sourcepose=json.loads((O/'source-art.json').read_text());assert all(p['source_projection_geometry']['native_06F1_minus_anchor_y']==3 for p in sourcepose['poses']if p['source_frame']==171)
 names=['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_BoundBoxCtrl','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_MovingDir','R0','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon']
 defs={n:address(base,n)for n in names};defs.update(PpHostImportX=life['PpHostImportX'],PpSourceNear=core['PpN_5_890D'],SmcOffsets=services['SmcOffsets'],NativeDefeat=address(base,'ShellOrBlockDefeat'),NativeDefeatBank=((location(base,'ShellOrBlockDefeat')-16)//8192)|128)
 source=''.join(f'{n}=${v:04x}\n'for n,v in defs.items())+'''
.setcpu "6502"
.macpack longbranch
.segment "PROXY"
.export PpNativeProxyIn,PpNativeProxyOut,PpProxyEnd
.export PpProxyBestSlot,PpProxyBestDistance
PpNativeProxyIn:
 lda $c0a6
 and #3
 cmp #2
 jne Return
 jsr PpHostImportX
 lda #104
 sta PpProxyBestDistance
 lda #255
 sta PpProxyBestSlot
 ldx #5
Scan:
 lda Enemy_Flag,x
 cmp #1
 bne Next
 lda Enemy_ID,x
 cmp #7
 bcs Next
 lda Enemy_State,x
 and #$20
 bne Next
 lda Enemy_BoundBoxCtrl,x
 cmp #3
 bne Next
 lda Enemy_Y_HighPos,x
 cmp #1
 bne Next
 jsr ImportX
 jsr PpSourceNear
 bcs Next
 lda $c017
 cmp PpProxyBestDistance
 bcs Next
 sta PpProxyBestDistance
 stx PpProxyBestSlot
Next:
 dex
 bpl Scan
 ldx PpProxyBestSlot
 bmi Absent
 txa
 ora #$80
 cmp $c61c
 beq Import
 ldy #13
Birth:
 lda GuardTemplate,y
 sta $c61c,y
 dey
 bpl Birth
 txa
 ora #$80
 sta $c61c
 stx $c051
 stx $c710
 lda #255
 sta $c712
 lda #0
 sta $c711
 sta $c6de
 lda #1
 sta $c6d0
Import:
 jsr ImportX
 lda Enemy_Y_Position,x
 clc
 adc #21
 sta $c61f
 lda Enemy_Y_HighPos,x
 adc #$ff
 sta $c620
 sec
 lda $c61f
 sbc $c089
 sta $c61f
 lda $c620
 sbc $c08a
 sta $c620
 lda #0
 ldy Enemy_MovingDir,x
 cpy #1
 bne FaceReady
 lda #255
FaceReady:
 sta $c623
 lda #1
 sta $c6e0
 rts
Absent:
 lda #0
 sta $c6e0
 sta $c61c
Return:rts
ImportX:
 lda Enemy_X_Position,x
 clc
 adc #8
 sta $c61d
 lda Enemy_PageLoc,x
 adc #0
 sta $c61e
 rts

; Export only the original guard's genuine terminal damage result. Native
; physics/AI/flags remain owned by the native actor, no outcome is seeded.
PpNativeProxyOut:
 lda $c6d0
 bne Return
 lda $c6de
 cmp #85
 bne Return
 lda $c61c
 bpl Return
 and #$7f
 cmp #6
 bcs Return
 tax
 stx PpProxyBestSlot
 lda Enemy_Flag,x
 cmp #1
 bne Return
 lda Enemy_State,x
 and #$20
 bne Return
 lda Enemy_ID,x
 cmp #7
 bcs Return
 ldx #0
SaveZp:
 lda R0,x
 pha
 inx
 cpx #8
 bne SaveZp
 ldx #0
SaveSmc:
 ldy SmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne SaveSmc
 lda #<NativeDefeat
 sta FarcallJmpTarget_SMC+1
 lda #>NativeDefeat
 sta FarcallJmpTarget_SMC+2
 ldx PpProxyBestSlot
 lda #NativeDefeatBank
 jsr FarCallCommon
 ldx #4
RestoreSmc:
 pla
 ldy SmcOffsets,x
 sta $0100,y
 dex
 bpl RestoreSmc
 ldx #7
RestoreZp:
 pla
 sta R0,x
 dex
 bpl RestoreZp
 lda #0
 sta $c61c
 sta $c6e0
 rts
PpProxyBestSlot:.byte 255
PpProxyBestDistance:.byte 104
GuardTemplate:
 .byte '''+','.join(f'${v:02x}'for v in template)+'''
PpProxyEnd:
'''
 blob,lab=A.assemble('native-proxy-v40',source,'MEMORY{M:start=$4400,size=$800,file=%O;}SEGMENTS{PROXY:load=M,type=ro;}')
 # Bind the now-qualified whole battle component to actual owned world and
 # quiet source-event leaves. This remains an unplaced CPU-only image.
 text=(O/'combat-tail-v34.s').read_text()
 for old,new in [('PpNativeSfx=$5100',f'PpNativeSfx=${services["PpNativeQuietSfx"]:04x}'),('PpNativeRawSfx=$5110',f'PpNativeRawSfx=${services["PpNativeQuietSfx"]:04x}'),('PpWorldLandingAlign=$5120',f'PpWorldLandingAlign=${life["PpWorldLandingAlign"]:04x}')]:assert old in text;text=text.replace(old,new)
 battle,blab=A.assemble('native-battle-v40',text,'MEMORY{M:start=$4000,size=$1000,file=%O;}SEGMENTS{BATTLE:load=M,type=ro;}')
 q=dict(measured=True,qualified=False,ROM_written=False,native_emulator=False,placement_granted=False,base_SHA256=M.A.PIN,proxy_code_bytes=len(blob),battle_code_bytes=len(battle),original_guard_action57_constructor=template.hex(),native_body_table3_bytes=base['raw'][at:at+4].hex(),native_ground_proxy_domain='Live primary EnemyFlag1, ID0..6, statebit5clear, native box3, Yhigh1. Source Near890D supplies exact16bit absolute distance/<104 admission; closest native slot becomes the single original guard.',state_contract='Original guard actor61C..629 and guardHP6D0/death6DE/visible6E0/roomledger710..712;61C lowbits hold native slot while activebit7 remains original. Native constructors must clear these before publishing ready. Two owned metadata-local bytes hold only scan scratch.',geometry_contract='ProxyX=nativeEnemyX+8. ProxyY16=nativeEnemyY16+21-sourceOrigin16; box3bottom21 plus original guardstandingdelta3 matches native24px physical anchor. Original full battle retains reach32/38/48, vertical+/-30, facing, A-strike154, B-parry, and actual source action/mode.',native_defeat='Only source guardHP0 plus death85 may call genuine ShellOrBlockDefeat. All nativeR0..7 and5SMCbytes saved/restored; no direct native death/enemy outcome store.',estimated_live_fit=dict(grid_metadata_bytes=4337,grid_decoder_bytes=114,existing_native_services_bytes=299,existing_public_bytes=95,full_battle_bytes=len(battle),proxy_bytes=len(blob),subtotal_before_native_policies_router=4337+114+299+95+len(battle)+len(blob),RAM2_C800_DFD0_capacity=0xdfd0-0xc800),remaining=['CPU actual native actor scan/birth/source-clock/hurt/strike/outcome/foreign/ISR cases.','Native HP/palette/public collision policies and exact relink/cold/44carrier backing/runtimefit.','Reader/constructor/clock/foreign retirement closure and root exact RAM2amendment; no new RAM is granted.'],bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-proxy-v40.bin',O/'native-battle-v40.bin',O/'combat-tail-CPU-v36.json',O/'pose-grid-native-CPU-v38.json',M.A.BASE,R/'docs/qa/allocations/prince-carrier514-1102-v35.json']})
 (O/'native-proxy-measurement-v40.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
