"""Lossless original8px body-grid funding, irregular sword poses stay raw."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_cold_worker_1102_v19 as A
P,O=A.L.P,A.O


def main():
 old=(O/'prince-pose-packets-v11.bin').read_bytes();offsets=[int.from_bytes(old[2*i:2*i+2],'little')for i in range(239)];unique=sorted(set(offsets)-{65535});ends={a:unique[i+1]if i+1<len(unique)else len(old)for i,a in enumerate(unique)}
 data=bytearray([255]*478);mapping={};rows=[];saved=0
 for at in unique:
  packet=old[at:ends[at]];n=packet[0]&15;np=(packet[0]>>4)&3;prefix=2+np;assert len(packet)==prefix+3*n
  parts=[packet[prefix+3*i:prefix+3*i+3]for i in range(n)];xs=[p[2]if p[2]<128 else p[2]-256 for p in parts];ys=[p[0]if p[0]<128 else p[0]-256 for p in parts];x0,y0=min(xs),min(ys)
  grid=all((x-x0)%8==0 and(y-y0)%8==0 and(x-x0)//8<16 and(y-y0)//8<16 for x,y in zip(xs,ys))
  mapping[at]=len(data)|(0x8000 if grid else 0);data.extend(packet[:prefix])
  if grid:
   data.extend([x0&255,y0&255])
   for p,x,y in zip(parts,xs,ys):data.extend([((x-x0)//8<<4)|((y-y0)//8),p[1]])
  else:data.extend(packet[prefix:])
  rows.append(dict(old_offset=at,new_offset=mapping[at]&32767,grid=grid,parts=n));saved+=n-2 if grid else 0
 for f,at in enumerate(offsets):
  if at!=65535:data[2*f:2*f+2]=mapping[at].to_bytes(2,'little')
 assert len(old)-len(data)==saved==681
 (O/'prince-pose-grid-v37.bin').write_bytes(data)
 # Export private labels without changing one byte of the frozen545B leaf.
 text=(O/'host-render-v11.s').read_text();exports=['PpPosePointer','PpReadProjection','Parts','Byte','Read','Attribute','OffsetLo','OffsetHi','Header']
 text+='\n.export '+','.join(exports)+',PpGridPartEnd\n';needle=' lda #<PpNativePacket\n';assert text.count(needle)==1;text=text.replace(needle,'PpGridPartEnd:\n'+needle)
 original,lab=A.assemble('grid-render-labels-v37',text,(O/'host-render-v11.cfg').read_text());assert original==(O/'host-render-v11.bin').read_bytes()
 start=0xc800+len(data)
 source=f'''Byte=${lab['Byte']:04x}
Read=${lab['Read']:04x}
PpReadProjection=${lab['PpReadProjection']:04x}
.setcpu "6502"
.segment "GRID"
.export PpGridLookup,PpGridProjection,PpGridY,PpGridX,PpGridEnd
.export PpGridFlag,PpGridBaseX,PpGridBaseY,PpGridCell
PpGridLookup:
 lda $c617
 beq Bad
 cmp #239
 bcs Bad
 asl
 tay
 lda #$c8
 adc #0
 sta IndexLo+2
 sta IndexHi+2
IndexLo:lda $c800,y
 sta Read+1
IndexHi:lda $c801,y
 cmp #$ff
 beq Bad
 sta PpGridFlag
 and #$7f
 clc
 adc #$c8
 sta Read+2
 sec
 rts
Bad:clc
 rts
PpGridProjection:
 jsr PpReadProjection
 bit PpGridFlag
 bpl ProjectionDone
 jsr Byte
 sta PpGridBaseX
 jsr Byte
 sta PpGridBaseY
ProjectionDone:rts
PpGridY:
 bit PpGridFlag
 bpl Raw
 jsr Byte
 sta PpGridCell
 and #15
 asl
 asl
 asl
 clc
 adc PpGridBaseY
 rts
PpGridX:
 bit PpGridFlag
 bpl Raw
 lda PpGridCell
 and #$f0
 lsr
 clc
 adc PpGridBaseX
 rts
Raw:jmp Byte
PpGridFlag:.byte 0
PpGridBaseX:.byte 0
PpGridBaseY:.byte 0
PpGridCell:.byte 0
PpGridEnd:
'''
 helper,glab=A.assemble('pose-grid-helper-v37',source,f'MEMORY{{M:start=${start:04x},size=$200,file=%O;}}SEGMENTS{{GRID:load=M,type=ro;}}')
 renderer=bytearray(original);patches=[]
 def patch(pc,blob):
  at=pc-0xbbc1;assert 0<=at and at+len(blob)<=len(renderer);pre=bytes(renderer[at:at+len(blob)]);renderer[at:at+len(blob)]=blob;patches.append(dict(CPU=pc,old=pre.hex(),new=blob.hex()))
 jump=bytes([0x4c])+glab['PpGridLookup'].to_bytes(2,'little');length=lab['PpReadProjection']-lab['PpPosePointer'];assert length>=3
 patch(lab['PpPosePointer'],jump+bytes([0xea])*(length-3))
 def calls(lo,hi,dest):return[at for at in range(lo,hi-2)if original[at-0xbbc1:at-0xbbc1+3]==bytes([0x20])+dest.to_bytes(2,'little')]
 sites=calls(lab['PpHostDraw'],lab['PpHostProject'],lab['PpReadProjection']);assert len(sites)==1;patch(sites[0],bytes([0x20])+glab['PpGridProjection'].to_bytes(2,'little'))
 sites=calls(lab['Parts'],lab['PpGridPartEnd'],lab['Byte']);assert len(sites)==3
 patch(sites[0],bytes([0x20])+glab['PpGridY'].to_bytes(2,'little'));patch(sites[2],bytes([0x20])+glab['PpGridX'].to_bytes(2,'little'))
 (O/'grid-render-v37.bin').write_bytes(renderer)
 # Actual6502 lookup/projection/cell leaves reconstruct all original raw
 # records. Full native emitter/OAM/IRQ qualification is a separate run.
 art=json.loads((O/'source-art.json').read_text());cases=0;CPU=[]
 def invoke(m,pc,y=0,x=91):
  c=P.T.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p=83,x,y,0x21;c.sp=224;c.stPushWord(0x5ffe)
  for _ in range(3000):
   if c.pc==0x5fff:break
   assert m[c.pc]!=0,('Grid fixture BRK',hex(c.pc));c.step()
  else:raise AssertionError('Grid fixture instruction bound')
  assert c.sp==224 and c.x==x;CPU.append(c.processorCycles);return c
 for pose in art['poses']:
  frame=pose['source_frame'];m=[0]*65536;m[0xbbc1:0xbbc1+len(renderer)]=renderer;m[0xc800:0xc800+len(data)]=data;m[start:start+len(helper)]=helper;m[0xc617]=frame;m[0xc611]=128
  c=invoke(m,glab['PpGridLookup']);assert c.p&1
  c=invoke(m,lab['Byte']);header=c.a;assert header==old[offsets[frame]];m[lab['Header']]=header
  # Original draw reads header/pages then projection. Its exact helper
  # consumes grid bases only in the packed case.
  invoke(m,glab['PpGridProjection'],y=1+((header>>4)&3))
  ptr=m[lab['Read']+1]|m[lab['Read']+2]<<8;y=2+((header>>4)&3)+(2 if mapping[offsets[frame]]&32768 else 0)
  restored=[]
  for _ in range(header&15):
   c=invoke(m,glab['PpGridY'],y);restored.append(c.a);y=c.y
   c=invoke(m,lab['Byte'],y);restored.append(c.a);y=c.y
   c=invoke(m,glab['PpGridX'],y);restored.append(c.a);y=c.y
  pos=offsets[frame]+2+((header>>4)&3);assert bytes(restored)==old[pos:pos+3*(header&15)],(frame,pose['source_facing'])
  assert ptr+y==0xc800+rows[next(i for i,r in enumerate(rows)if r['old_offset']==offsets[frame])]['new_offset']+(2+((header>>4)&3)+(2 if mapping[offsets[frame]]&32768 else 0)+2*(header&15)if mapping[offsets[frame]]&32768 else 2+((header>>4)&3)+3*(header&15))
  g=pose['source_projection_geometry'];assert m[0xc70f]==g['native_070F']and m[0xc6f1]==(128+g['native_06F1_minus_anchor_y'])&255 and m[0xc4c3]==g['native_04C3'];assert not any(m[:256])and not any(m[512:2048]);cases+=1
 q=dict(passed=True,source_CPU_only=True,native_emulator=False,ROM_written=False,placement_granted=False,original_metadata_bytes=len(old),new_metadata_bytes=len(data),metadata_saved=saved,grid_poses=sum(r['grid']for r in rows),raw_irregular_poses=sum(not r['grid']for r in rows),all_source_face_packets=cases,all_2578_original_cell_Y_tile_X_bytes_exact=True,all_original_geometry_exact=True,all_original_art_31072bytes_unchanged=True,renderer_bytes_unchanged=len(renderer),private_code_public_addresses_unchanged=True,helper_bytes=len(helper),proposed_reclaimed_metadata_helper_half_open=[start,start+len(helper)],helper_original_host_ZP_preserved=True,isolated_leaf_CPU=[min(CPU),max(CPU)],renderer_patches=patches,net_reclaimed_live_bytes_before_battle=saved-len(helper),pointer_format='Offsetbit15 selects lossless XYgrid; FF sentinel unchanged.178grid poses store baseX/baseY and one XY nibblebyte+pattern perpart;26irregular sword poses retain original3bytes.',required=['Actual native408pose/edge/emitter/CHR/IRQ proof against unchanged source artwork.','Root must amend exact compact metadata end/executable helper interval; reclaim is not yet a grant.','Full battle760B/nativeproxy/policies relink and physical44page/cold/state/reader/lifetime fit.'],scope='Measured source-grid redundancy, exact6502 reconstruction of every original cell byte and geometry. No original coordinates/colors/art are approximated; no new resources or native gameplay claim.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'prince-pose-packets-v11.bin',O/'source-art.json',O/'host-render-v11.s',O/'host-render-v11.bin',O/'prince-pose-grid-v37.bin',O/'grid-render-v37.bin',O/'pose-grid-helper-v37.bin']})
 (O/'pose-grid-CPU-v37.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','renderer_patches']}))


if __name__=='__main__':main()
