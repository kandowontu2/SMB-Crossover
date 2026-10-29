"""Port complete authentic Kamikaze poses, using its changed graphics table."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];O=R/'build/kamikaze-mario-art-v2'
def sha(b):return hashlib.sha256(b).hexdigest()
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
def main():
 O.mkdir(exist_ok=True);assert not(O/'source-art.json').exists()
 p=Path('C:/NES/the stash/Kamikaze_Mario_DX_Plus_V1.9_SMB1_Hack.nes');raw=p.read_bytes();assert sha(raw)=='5e866dab7fd0d3f402dff679748a68f9c98d32ffa6c970923be97b79f33617d1'
 # Both genuine game-code copies use the changed table atEE17. Their
 # unchanged actual BD17EE indexed reader is atEFDC in each copy.
 assert raw[16+0x6fdc:16+0x6fdf]==bytes.fromhex('bd17ee')
 tab=raw[16+0x6e17:16+0x6e17+208];assert tab==raw[16+0xee17:16+0xee17+208]
 source=raw[16+81920:16+81920+8192];patterns=bytearray(4096);records=[];asm=[]
 # Names retain native pose clocks. The original SMB offsets, retained as
 # comments in player.s, select Standing25/Crouch10/Death22/Grow23..25.
 # Walk is in the host's existing1,2,0 cyclic order. Held swim and throw
 # combinations use the corresponding complete source pose; no tile-index
 # substitution or invented anatomy. These are explicit skin adapters.
 pose=[0,25,1,2,0,3,4,10,5,6,7,5,6,7,
       11,11,11,11,11,11,10,5,6,7,5,6,7,8,9,
       23,13,14,12,15,16,17,18,19,17,18,19,
       23,13,14,12,15,16,17,18,19,17,18,19,20,21,22,23,24,25,11,11,23,23]
 assert len(pose)==63
 asm+=['; Complete source frame records; CPU A62 labels read through C62.','KmFrameMap: .byte '+','.join(map(str,pose)),
        'KmPages: .byte '+','.join(str(16+f//8)for f in range(26))]
 for side in['R','L']:
  for part in['Lo','Hi']:
   asm+=['Km'+side+part+': .byte '+','.join(('<'if part=='Lo'else'>')+f'(Km{side}{f}+$2000)'for f in range(26))]
 for f in range(26):
  page=f//8;first=(f%8)*8;tiles=list(tab[f*8:(f+1)*8])
  for row in range(2):
   for col in range(2):
    pair=first+row*4+col*2;at=page*1024+pair*16
    for half in range(2):
     tile=tiles[(row*2+half)*2+col];pattern=bytes(16)if tile==252 else source[tile*16:tile*16+16]
     patterns[at+half*16:at+(half+1)*16]=pattern
  for side in['R','L']:
   parts=[]
   for row in range(2):
    for col in range(2):parts.extend([first+row*4+col*2,64 if side=='L'else 0,(-8+row*16)&255,(8-col*8)if side=='L'else col*8])
   asm += [f'Km{side}{f}: .byte 16,'+','.join(map(str,parts))]
   records.append(dict(frame=f,side=side,page=696+page,source_tiles=tiles,record=[16]+parts))
 target=R/'chr/characters/kamikaze-mario-source-v2.chr';target.write_bytes(patterns)
 inc=R/'src/kamikaze_mario_source_art_v2.inc';inc.write_text('\n'.join(asm)+'\n')
 proof=dict(status='EXACT_COMPLETE_SOURCE_POSES_NOT_NATIVE_ADMISSION',source=bind(p),output=bind(target),descriptors=bind(inc),bindings=[bind(Path(__file__))],source_table_offset=16+0x6e17,source_table_sha256=sha(tab),source_frames=26,records=records,host_pose_mapping=pose,
  adaptation='Native Mario physics/palette/clocks remain authoritative. Complete source32px canvases include authentic24px small artwork,8px visual overhang above the native small hitbox; native4-sprite reservation is unchanged. No source-game physics claim. Held-swim/throw combinations are mapped explicitly to complete source poses.',
  rejected='v1 tile-only substitution falsely assumed unchanged source-table anatomy; native visual disqualified c2b8615d before distribution.')
 (O/'source-art.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(CHR=bind(target),records=len(records))))
if __name__=='__main__':main()
