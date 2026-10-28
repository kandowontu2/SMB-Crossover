"""Lossless original executable-renderer art recipe, USA source only."""
import json
import dragon_power_reference_v1 as O
import dragon_power_component_v1 as B
def pixels(pose,face,wave=False):
 m=O.Memory();m.ram[0x23]=4;m.ram[0xf7]=80;m.ram[0xf8]=80;m.ram[0xf9]=3
 m.ram[0x30]=pose;m.ram[0x31]=face
 if wave:
  m.ram[0xd7]=0x40;m.ram[0x3a]=0x82 if face==0 else 0x43;m.ram[0x3e]=80;m.ram[0x3c]=80
 q=O.call(m,0xad29 if wave else 0xbaab)
 oam=bytes(m.ram[0x704:0x700+m[0x23]]);chr=O.D.raw()[16+131072+3*8192:16+131072+4*8192];out={}
 for i in range(len(oam)-4,-1,-4):
  y,t,a,x=oam[i:i+4];tile=chr[t*16:t*16+16]
  assert a&3 in [2,3]
  for yy in range(8):
   for xx in range(8):
    sy=7-yy if a&128 else yy;sx=7-xx if a&64 else xx
    v=(tile[sy]>>(7-sx)&1)|((tile[sy+8]>>(7-sx)&1)<<1)
    if v:out[x-80+xx,y+1-80+yy]=(v,(a&3)-2)
 return out,oam,q['cycles']
def pair(px,x,y,pal):
 out=bytearray(32)
 for yy in range(16):
  for xx in range(8):
   v,p=px.get((x+xx,y+yy),(0,0));v=v if p==pal else 0;at=yy//8*16+yy%8
   out[at]|=(v&1)<<(7-xx);out[at+8]|=(v>>1)<<(7-xx)
 return bytes(out)
def main():
 B.OUT.mkdir(exist_ok=True);pages=[];records=[];facts=[];indices=[];unique={}
 for pose,wave in [(i,False)for i in range(32)]+[(0,True)]:
  for face in [0,64]:
   px,oam,cycles=pixels(pose,face,wave);parts=[]
   for y in range(min(k[1]for k in px)//16*16,max(k[1]for k in px)+1,16):
    for x in range(min(k[0]for k in px)//8*8,max(k[0]for k in px)+1,8):
     for pal in [0,1]:
      p=pair(px,x,y,pal)
      if any(p):parts.append((p,pal,y,x))
   key=tuple(parts)
   if key not in unique:
    needed=set(p[0]for p in parts);assert len(needed)<=32
    options=[(len(needed-set(page)),i)for i,page in enumerate(pages)if len(needed|set(page))<=32]
    if not options:pages.append([]);page=len(pages)-1
    else:page=min(options)[1]
    for p in sorted(needed):
     if p not in pages[page]:pages[page].append(p)
    data=[];restored={}
    for p,pal,y,x in parts:
     data +=[pages[page].index(p)*2,pal,(y+15)&255,x&255]
     for yy in range(16):
      for xx in range(8):
       at=yy//8*16+yy%8;v=(p[at]>>(7-xx)&1)|((p[at+8]>>(7-xx)&1)<<1)
       if v:restored[x+xx,y+yy]=(v,pal)
    assert restored==px
    unique[key]=len(records);records.append((page,[len(data)]+data))
   rec=unique[key];indices.append(rec)
   facts.append(dict(pose=pose,wave=wave,source_facing=face,sourceOAM=oam.hex(),source_cycles=cycles,
      opaque=len(px),host_parts=len(parts),record=rec,palette_role_pixel_sha256=O.D.digest(json.dumps(sorted(px.items())).encode())))
 assert len(pages)<=8 and max(f['host_parts']for f in facts)<=16
 chr=b''.join(b''.join(p)+bytes(1024-len(p)*32)for p in pages);chr+=bytes(8192-len(chr))
 (B.ROOT/'chr/characters/dragon-power.chr').write_bytes(chr)
 lines=['; Exact original DragonPowerUSA executable-renderer pixels. No Japanese art.',
 '.pushseg','.segment "DRAGON_POWER_ART"','DpArtStart:']
 for name,seq in [('DpPoseLo',[f'<DpArt{v}'for v in indices]),('DpPoseHi',[f'>DpArt{v}'for v in indices]),
                  ('DpPosePage',[str(records[v][0])for v in indices])]:
  lines +=[name+':',' .byte '+','.join(seq)]
 lines+=['DpPaletteRoles:',' .byte $36,$26,$04,$30,$36,$0f']
 for i,(page,data)in enumerate(records):lines +=[f'DpArt{i}:',' .byte '+','.join(f'${v:02x}'for v in data)]
 lines+=['DpArtEnd:','.assert DpArtEnd-DpArtStart<=$1000,error,"Goku ART exceeds approved85C900..D8FF"',
 '.export DpArtStart,DpPoseLo,DpPoseHi,DpPosePage,DpPaletteRoles','.popseg',
 '.pushseg','.segment "DRAGON_POWER_CHR"','.incbin "chr/characters/dragon-power.chr"','.popseg']
 p=B.ROOT/'src/dragon_power_art.inc';p.write_text('\n'.join(lines)+'\n')
 proof=dict(status='PASS_SOURCE_PIXEL_REGROUP_ONLY',original=O.D.binding(O.D.ROM),recipe=O.D.binding(__file__),
  CHR=O.D.binding(B.ROOT/'chr/characters/dragon-power.chr'),ART=O.D.binding(p),CHR_pages_used=len(pages),
  unique_records=len(records),records=facts,ART_bytes=len(indices)*3+6+sum(len(d)for _,d in records),
  palette_contract='OriginalP2->hostrole0 body36/26/04;OriginalP3->role1 head/wave30/36/0F. Role pointer only, no unsafe palette publication.',
  origin='Hostleft=sourceF7,hosttop=sourceF8-16. DescriptorY=originaldisplayOffset+15, actualOAMY=hosttop+descriptorY.',
  limits='No nativePPU/palette ownership/timing qualification; exact source palette-role pixels and geometry only')
 assert proof['ART_bytes']<=4096
 q=B.OUT/'art-controls.json';q.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps({k:proof[k]for k in ['CHR_pages_used','unique_records','ART_bytes']},indent=2))
if __name__=='__main__':main()
