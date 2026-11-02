"""Exact public routing/lifecycle fit, proposal only; no shared ROM mutation."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
import measure_prince_owner_routes_1102_v23 as A
import measure_prince_lzdict_1102_v9 as D
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
O=L.O;B=A.B


def main():
 b=scoped_load(L.BASE);native=L.P.T.labels(O/'host-services-v18.lbl');render=L.P.T.labels(O/'host-render-v11.lbl');src=''.join(f'{n}=${v:04x}\n'for n,v in {**native,**{k:render[k]for k in ['PpHostDraw']}}.items()if n.startswith('PpNative')or n=='PpHostDraw')
 src+='''.setcpu "6502"
PpServiceTag=$c09e ; Source world SavedY; overwritten before its only read.
.segment "FRESH_PREFIX"
.export PpNativeFresh,PpNativeFreshEnd
PpNativeFresh:
 lda #0
 ldx #7
FreshGap:
 sta $c0f8,x
 dex
 bpl FreshGap
 jmp PpNativeResetTail
PpNativeFreshEnd:
.segment "PUBLIC"
.export PpNativeResetTail,PpNativeRoute,PpNativePublicEnd
PpNativeResetTail:
 ldx #$af
FreshPrefix:
 sta $c000,x
 dex
 cpx #$ff
 bne FreshPrefix
 ldx #$0f
FreshGap2:
 sta $c352,x
 dex
 bpl FreshGap2
 ldx #$0b
FreshGap3:
 sta $c3ff,x
 dex
 bpl FreshGap3
 ldx #$6d
FreshGap4:
 sta $c491,x
 dex
 bpl FreshGap4
 ldx #$f9
FreshActorPage:
 sta $c606,x
 dex
 cpx #$ff
 bne FreshActorPage
 ldx #0
FreshLastPage:
 sta $c700,x
 inx
 bne FreshLastPage
 jmp PpNativeInit
PpNativeRoute:
 pha
 lda PpServiceTag
 beq PublicTick
 cmp #6
 beq PublicDraw
 cmp #45
 beq PublicFresh
 cmp #108
 beq PublicFresh
 cmp #3
 beq PublicGraphics
 pla
 clc
 rts
PublicTick:
 pla
 jmp PpNativeTick
PublicDraw:
 pla
 jmp PpHostDraw
PublicFresh:
 pla
 jmp PpNativeFresh
PublicGraphics:
 pla
 sec
 rts
PpNativePublicEnd:
'''
 private,plab=A.assemble('public-private-v24',src,'MEMORY{F:start=$b3ef,size=$11,file="'+(O/'public-fresh-v24.bin').as_posix()+'";P:start=$dcc5,size=$6d,file=%O;}SEGMENTS{FRESH_PREFIX:load=F,type=ro;PUBLIC:load=P,type=ro;}')
 # Existing77B classifier: retain legal raw0..39 routing exactly except new
 # raw38 goes to the Ex-family veneers. Its phase caller restores nativeY/P.
 names=['SelectedCharacter','FarcallJmpTarget_SMC','NextBank_SMC','HuCommonRestore','HuNativeWorldPalette'];defs=''.join(f'{n}=${address(b,n):04x}\n'for n in names)
 route=(R/'tools/reference/excitebike_shared_router_1101_v1.s').read_text();assert route.count(' lsr\n jmp ExThreeOwnerHigh')==1;route=route.replace(' lsr\n jmp ExThreeOwnerHigh',' jmp ExThreeOwnerHigh')
 old='''ExThreeOwnerHigh:
 lda #$aa
 bcc ExThreeHighReady
 lda #$b0
ExThreeHighReady:
 sta FarcallJmpTarget_SMC+2
 ldy #$88
 bcc ExThreeLowReady
 ldy #$8b                     ; +incomingC1 = actual Ex veneer low8C.
ExThreeLowReady:
'''
 new='''ExThreeOwnerHigh:
 cmp #37
 ldy #$88
 lda #$aa
 bcc ExThreeHighReady
 ldy #$8b
 lda #$b0
ExThreeHighReady:
 sta FarcallJmpTarget_SMC+2
''';assert old in route;route=route.replace(old,new)
 gate,rlab=A.assemble('public-router-v24',defs+route,'MEMORY{G:start=$a707,size=$30,file=%O;R:start=$bfb0,size=$1d,file="'+(O/'public-router-tail-v24.bin').as_posix()+'";}SEGMENTS{EX_THREE_GATE:load=G,type=ro;EX_THREE_ROUTE:load=R,type=ro;}')
 # Preserve the original19B scene gate. Direct bounded BCC reaches B062;
 # the redundant local JMP was private to that source gate.
 prefix=(B/'native-proxy-routes.s').read_text().split('.export ExServiceVeneers')[0];scene=prefix+'''
.segment "SCENE"
.export CoSceneGate,CoSceneGateEnd
CoSceneGate:
 php
 pha
 lda SelectedCharacter
 sec
 sbc #37
 cmp #3
 bcc CoSceneGate+($b062-$b013)
 pla
 plp
 jmp ExPriorScene
 .res 2,$ea
CoSceneGateEnd:
'''
 scene='ExSceneOwn=$b062\n'+scene
 scene_blob,slab=A.assemble('public-scene-v24',scene,'MEMORY{S:start=$b013,size=19,file=%O;}SEGMENTS{SCENE:load=S,type=ro;}')
 selector=(O/'shared-frame-v22.s').read_text();selector=selector[selector.index('.segment "EX_SELECT"'):]
 selector=selector.replace(' and #$fd\n cmp #37\n beq PrOdd',' sec\n sbc #37\n cmp #3\n bcc PrOdd')
 assert selector.count(' lda SelectedCharacter\n cmp #39')==1;selector=selector.replace(' lda SelectedCharacter\n cmp #39',' lda SelectedCharacter\n cmp #38\n beq PrPrince\n cmp #39')
 selector=selector.replace('ExDispatchNo=ShDispatchNo','''PrPrince:
 lda FarcallJmpTarget_SMC+1
 sta $c09e
 lda #<PpNativeRoute
 sta FarcallJmpTarget_SMC+1
 lda #>PpNativeRoute
 jmp PrSharedCall
ExDispatchNo=ShDispatchNo''')
 labs=L.P.T.labels(O/'shared-frame-v22.lbl');de={n:address(b,n)for n in ['SelectedCharacter','FarcallJmpTarget_SMC']};de.update({n:labs[n]for n in ['ShDispatch','ShDispatchNo','PrSharedCall']});de.update(ShServiceVeneers=0xaa88,ShCheckCode=0xa800,CoCheckCode=0xaef3,ExForeignUi=0xb031,PpNativeRoute=plab['PpNativeRoute'])
 sel,lab=A.assemble('public-selector-v24','.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${v:04x}\n'for n,v in de.items())+selector,'MEMORY{S:start=$a740,size=$b2,file=%O;}SEGMENTS{EX_SELECT:load=S,type=ro;}')
 foreign=bytearray((B/'native-proxy-route-foreign.bin').read_bytes());foreign[10:12]=(lab['ExForeignLo']-4).to_bytes(2,'little');foreign[45:47]=labs['ShDispatchNo'].to_bytes(2,'little');(O/'public-foreign-v24.bin').write_bytes(foreign)
 runtime=bytearray((O/'native-runtime-v18.bin').read_bytes());fresh=(O/'public-fresh-v24.bin').read_bytes();assert runtime[0x13ef:0x1400]==bytes(17);runtime[0x13ef:0x13ef+len(fresh)]=fresh
 metadata=(O/'native-metadata-v18.bin').read_bytes()+private;packed=[]
 for name,data in [('runtime',bytes(runtime)),('metadata',metadata)]:
  enc=D.encode(data);(O/f'public-{name}-v24.bin').write_bytes(data);(O/f'public-{name}-v24.lzdict').write_bytes(enc);packed.append(len(enc))
 oldpool=(O/'cold-pool-v19.bin').read_bytes();oldruntime=(O/'native-runtime-v18.lzdict').stat().st_size;oldmeta=(O/'native-metadata-v18.lzdict').stat().st_size
 total=len(oldpool)-oldruntime-oldmeta+sum(packed)
 q=dict(measured=True,qualified=False,proposal_only=True,ROM_written=False,shared_sources_written=False,base_ROM=A.PIN,private_resolver_bytes=plab['PpNativePublicEnd']-plab['PpNativeRoute'],private_reset_tail_bytes=plab['PpNativeRoute']-plab['PpNativeResetTail'],private_public_tail_bytes=len(private),private_public_half_open=[0xdcc5,plab['PpNativePublicEnd']],remaining_metadata_tail=0xdd32-plab['PpNativePublicEnd'],private_fresh_prefix_bytes=len(fresh),private_fresh_prefix_half_open=[0xb3ef,0xb3ef+len(fresh)],source_original_live_state_zero_ranges=[[0xc000,0xc0b0],[0xc0f8,0xc100],[0xc352,0xc362],[0xc3ff,0xc40b],[0xc491,0xc4ff],[0xc606,0xc800]],warm_packet_retained='C200..C235 is the already source-proven dead original OAM replaced by the native packet; warm reset retains it until next Draw overwrites every consumed packet byte. Cold decoder staging still must be zeroed by qualified finalizer before live init.',service_tag=dict(address=0xc09e,existing_field='Source world SavedY; requires explicit before-use/lifetime/ISR supplement before grant.'),resident_selector_bytes=len(sel),resident_selector_growth=len(sel)-(O/'shared-selector-v22.bin').stat().st_size,conditional_frame_funding=141,manager_extra_bytes=(O/'owner-third-extra-v23.bin').stat().st_size,remaining_resident_bytes=141-(O/'owner-third-extra-v23.bin').stat().st_size-(len(sel)-(O/'shared-selector-v22.bin').stat().st_size),PRG79_router=dict(gate_bytes=len(gate),tail_bytes=(O/'public-router-tail-v24.bin').stat().st_size,existing_source_grant=77,legal_raw_domain=[0,39],only_changed_legal_owner=38,out_of_domain_raw40_255_not_a_legal_roster_constructor_claim=True),scene_gate_bytes=len(scene_blob),proposed_total_pool_bytes=total,pool_capacity=44032,pool_spare=44032-total,implemented_private_rows={'0':'Authentic source/native epoch Tick','1':'Draw-owned CHR already publishes; carry handled','2':'Original-art native Draw','15':'Zero original live state, genuine source constructor','19':'Existing ROM full owner retirement','36':'Source scene constructor'},all_other_rows='Explicit Cclear fallback; health/hurt/combat/palette/native collision profiles remain to be bound before production admission.',cold_worker_successor_recompile_and_CPU_required=True,grant=False,bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),R/'tools/reference/excitebike_shared_router_1101_v1.s',O/'shared-frame-v22.bin',O/'public-selector-v24.bin',O/'public-private-v24.bin',O/'public-fresh-v24.bin',O/'public-router-v24.bin',O/'public-router-tail-v24.bin',O/'public-scene-v24.bin',O/'public-foreign-v24.bin',O/'public-runtime-v24.bin',O/'public-metadata-v24.bin',O/'owner-routes-measurement-v23.json']})
 (O/'public-routes-measurement-v24.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','implemented_private_rows']}));assert total<=44032


if __name__=='__main__':main()
