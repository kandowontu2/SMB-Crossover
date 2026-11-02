"""Repack only redundant original geometry; never change pose/body pixels."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import recover_prince_core_1101_v1 as B
O=B.O


def main():
 old=(O/'prince-pose-packets.bin').read_bytes();offsets=[int.from_bytes(old[2*i:2*i+2],'little')for i in range(239)]
 unique=sorted(set(offsets)-{65535});end={at:unique[i+1]if i+1<len(unique)else len(old)for i,at in enumerate(unique)}
 art=json.loads((O/'source-art.json').read_text());proofs=[]
 for p in art['poses']:
  g=p['source_projection_geometry'];delta=g['native_06F1_minus_anchor_y'];signed=delta if delta<128 else delta-256
  assert g['native_04C3']==4*(signed-3 if signed>=3 else 2-signed)&255
  assert g['native_070F']in [8,16,24,32,40,48]and -64<=signed<64
  proofs.append([p['source_frame'],p['source_facing'],g['native_070F'],delta,g['native_04C3']])
 new=bytearray([255]*478);mapping={}
 for at in unique:
  packet=old[at:end[at]];header=packet[0];pages=header>>4;geometry=1+pages;width,delta,height=packet[geometry:geometry+3];w=width//8-1
  assert width%8==0 and 0<=w<=5
  mapping[at]=len(new);new.extend([header|((w&3)<<6),*packet[1:geometry],(delta&127)|((w&4)<<5),*packet[geometry+3:]])
 for frame,at in enumerate(offsets):
  if at!=65535:new[2*frame:2*frame+2]=mapping[at].to_bytes(2,'little')
 (O/'prince-pose-packets-v11.bin').write_bytes(new)
 src=R/'tools/reference/prince_host_render_1102_v1.s';text=src.read_text()
 start=text.index(' lda PpState+$617\n');stop=text.index(' pha\n and #15\n',start)
 lookup=text[start:stop]
 text=text[:start]+' jsr PpPosePointer\n jcc Done\n ldy #0\n jsr Byte\n sta Header\n'+text[stop:]
 text=text.replace(' pla\n lsr\n lsr\n lsr\n lsr\n sta PageCount',' pla\n lsr\n lsr\n lsr\n lsr\n and #3\n sta PageCount',1)
 start=text.index(' ; Publish original projection geometry');stop=text.index(' lda #1\n ldx PpState+$615',start)
 text=text[:start]+' jsr PpReadProjection\n'+text[stop:]
 helper='''
.export PpHostProject
PpHostProject:
 jsr PpPosePointer
 bcc ProjectionDone
 ldy #0
 jsr Byte
 sta Header
 lsr
 lsr
 lsr
 lsr
 and #3
 tay
 iny
 jsr PpReadProjection
ProjectionDone:rts
PpPosePointer:
 lda PpState+$617
 beq PointerBad
 cmp #239
 bcs PointerBad
 asl
 tay
 lda #$c8
 adc #0
 sta OffsetLo+2
 sta OffsetHi+2
OffsetLo:lda $c800,y
 sta Read+1
OffsetHi:lda $c801,y
 cmp #$ff
 beq PointerBad
 clc
 adc #$c8
 sta Read+2
 sec
 rts
PointerBad:clc
 rts
PpReadProjection:
 jsr Byte
 pha
 and #$7f
 cmp #$40
 bcc :+
 ora #$80
:
 sta $c088
 clc
 adc PpState+$611
 sta PpState+$6f1
 lda $c088
 sec
 sbc #3
 sta PpState+$4bc
 lda $c088
 bmi BelowThree
 cmp #3
 bcc BelowThree
 sbc #3
 bcs Height
BelowThree:
 eor #$ff
 clc
 adc #3
Height:
 asl
 asl
 sta PpState+$4c3
 pla
 and #$80
 lsr
 lsr
 lsr
 lsr
 lsr
 sta WidthHigh
 lda Header
 lsr
 lsr
 lsr
 lsr
 lsr
 lsr
 ora WidthHigh
 clc
 adc #1
 asl
 asl
 asl
 sta PpState+$70f
 rts
Header:.byte 0
WidthHigh:.byte 0
'''
 text=text.replace('PpRenderEnd:\n',helper+'PpRenderEnd:\n')
 (O/'host-render-compact-v11.s').write_text(text)
 q=dict(prepared=True,qualified=False,old_metadata_bytes=len(old),new_metadata_bytes=len(new),saved_metadata_bytes=len(old)-len(new),source_pose_pairs=len(proofs),all_original_geometry_formula_exact=True,geometry_bit_format='Header bits0..3 sprite count,4..5 page count,6..7 low2 widthcode; geometry byte bit7 high widthcode,0..6 signed7bit original delta. Width8*(code+1),04C3=4*(delta-3 if delta>=3 else2-delta) modulo256.',scope='Source-backed lossless runtime geometry encoding proposal. All pixels/metasprite records/page lists retain their exact ordering and values; actual native renderer/IRQ proof follows separately.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),src,O/'prince-pose-packets.bin',O/'source-art.json']})
 (O/'geometry-codec-v11.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
