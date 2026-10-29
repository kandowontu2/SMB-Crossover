"""Pack original Gimmick records and exact source CHR8/12/13; no redrawing."""
from pathlib import Path
import hashlib,json
import gimmick_source_audit_v1 as G
R=G.R;O=R/'build/gimmick-component-v2'
def main():
 assert not(O/'handoff.json').exists(),'frozen packet'
 p=json.loads((R/'build/gimmick-source-audit-v1.json').read_text())
 lines=['; Original ce2f8461 records, kept in original 8x16 format.','.pushseg','.segment "GIMMICK_ART"','GmArtStart:']
 unique={};total=0
 for group,key in [('Hero','hero_frames'),('Star','star_frames')]:
  lines.append('Gm'+group+'Table:')
  for r in p[key]:
   label='GmRecord'+group+r['record'][2:]
   lines.append(' .word '+label);unique[label]=r
   total+=2
 for label,r in unique.items():
  blob=bytes(v for part in r['parts']for v in part)+b'\0'
  lines.append(label+':')
  lines.append(' .byte '+','.join('$%02x'%v for v in blob));total+=len(blob)
 lines+=['GmHeroPage:',' .byte '+','.join(str(r['CHR_page']-12)for r in p['hero_frames'])]
 total+=22
 lines+=['GmHurtFrame:',' .byte '+','.join('$%02x'%v for v in G.PRG[30*8192+0x5ee:30*8192+0x608])]
 total+=26
 # Actual original B4 four records, dedicated slot1 source page8.
 lines+=['GmEffectTable:',' .word GmEffect0,GmEffect1,GmEffect2,GmEffect3']
 for i,(y,tile)in enumerate([(0xf8,0x50),(0xf2,0x3a),(0xf1,0x2e),(0xf0,0x3e)]):
  lines+=['GmEffect%d:'%i,' .byte $%02x,$%02x,1,$fc,0'%(y,tile)]
 total+=28
 palette=json.loads((R/'build/gimmick-source-details-v1.json').read_text())['palette']['actual_sprite_palette_bytes']
 assert len(palette)==16
 lines+=['GmStage0Palette:',' .byte '+','.join('$%02x'%v for v in palette),
  'GmArtEnd:','.assert GmArtEnd-GmArtStart<=1760,error,"Approved C73 art lease"',
  '.export GmArtStart,GmArtEnd,GmHeroTable,GmStarTable,GmHeroPage,GmEffectTable','.popseg']
 total+=16
 assert total<=1760,total
 (R/'src/gimmick_art.inc').write_text('\n'.join(lines)+'\n')
 target=R/'chr/characters/gimmick-source-v2.chr'
 payload=G.CHR[12*1024:14*1024]+G.CHR[8*1024:9*1024]+bytes(1024)
 assert len(payload)==4096
 target.write_bytes(payload)
 (O/'chr.s').write_text('.segment "GIMMICK_CHR"\n.incbin "'+target.as_posix()+'"\n')
 (O/'art-proof.json').write_text(json.dumps(dict(status='SOURCE_PACK_UNLINKED',records=88,unique_records=85,
  original_8x16_parts_preserved=True,art_bytes=total,CHR_pages=[12,13,8,None],
  CHR_sha256=hashlib.sha256(payload).hexdigest(),palette_scope='All16 bytes from actual original stage0 roomLow0 publisher. Host may publish only agreed hero/star roles; do not replace world palettes.'),indent=2)+'\n')
 print(json.dumps(dict(art_bytes=total,CHR_bytes=len(payload))))
if __name__=='__main__':main()
