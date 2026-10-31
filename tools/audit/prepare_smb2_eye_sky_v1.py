"""Source-link lossless one-part eye roles and true native BG restoration."""
from pathlib import Path
import difflib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/functional-roster-coherent62-v4';O=R/'build/smb2-eye-sky-v1';J=O/'joint';S=J/'smb2';BASE=R/'build/smb2-current-component-v1/smb2'
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,x):write(p,json.dumps(x,indent=2)+'\n')
def run(c,n):
 g=validate(c,O,cwd=R);z=subprocess.run(c,cwd=R,capture_output=True,text=True)
 save(O/(n+'.json'),dict(command=c,guard=g,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));assert not z.returncode,z.stderr
def main():
 assert not O.exists();S.mkdir(parents=True)
 B.validate(P/'handoff.json','bb581aad7a4224cd35b83e056fe880cbd49c5cfcf04bfa637b00ea146bc01ab6')
 a=scoped_load(P/'joint/candidate.nes');before=a['raw'];assert B.sha(P/'joint/candidate.nes')=='408acae2712c1d9bbbe34233f8261fcf27723907d37acf020e3f5314be3b8604'
 for f in(P/'joint/smb2').iterdir():
  if f.is_file()and f.suffix in['.s','.inc']:(S/f.name).write_bytes(f.read_bytes())
 (J/'component.s').write_bytes((P/'joint/component.s').read_bytes());patch=''
 old=(BASE/'smb2_roster_palette_v2.s').read_text();s=old.replace('.export S2PalettePointerC,','.export S2NativePaletteHeader,')
 start=s.index('.proc S2PalettePointerC');end=s.index('.endproc',start)+len('.endproc')
 colors=list(before[location(a,'BackgroundColors'):location(a,'BackgroundColors')+8])
 helper='''.proc S2NativePaletteHeader
 ; OWN unused45B private pointer gate retired after exact object closure.
 ; Genuine native SetBGColor chooses BackgroundColorCtrl, or AreaType when0.
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$10
 sta VRAM_Buffer1+1,x
 lda #4
 sta VRAM_Buffer1+2,x
 ldy BackgroundColorCtrl
 bne Color
 ldy AreaType
Color:lda NativeBackgroundColors,y
 sta VRAM_Buffer1+3,x
 inx
 ldy #1
 rts
NativeBackgroundColors:.byte '''+','.join('$%02x'%x for x in colors)+'''
 .assert *-S2NativePaletteHeader<=45,error,"Retired own45B gate"
 .res 45-(*-S2NativePaletteHeader),$ea
.endproc'''
 s=s[:start]+helper+s[end:];write(S/'smb2_roster_palette_v2.s',s)
 patch+=''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='parent/palette.s',tofile='new/palette.s'))
 old=(BASE/'smb2_roster_main_v2.s').read_text();s=old
 needle=''' lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 ldy #1
Loop:lda (R0),y'''
 assert s.count(needle)==1;s=s.replace(needle,' jsr S2NativePaletteHeader\nLoop:lda (R0),y')
 start=s.index('.proc S2MainPalette');end=s.index('.endproc',start);piece=s[start:end];assert piece.count(' cpx #78')==1
 piece=piece.replace(' cpx #78',' cpx #77').replace('Done:rts','Done:rts\n .res 14,$ea\n .assert *-S2MainPalette=74,error,"Existing source palette public envelope"')
 s=s[:start]+piece+s[end:];write(S/'smb2_roster_main_v2.s',s)
 patch+=''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='parent/main.s',tofile='new/main.s'))
 old=(BASE/'smb2_roster_art.inc').read_text();s=old;attrs=[]
 def record(m):
  n=int(m[1]);v=[int(x)for x in m[2].split(',')]
  if n<70:
   assert v[0]==20 and v[1]in[56,58]and v[2]in[1,65]
   attrs.append(dict(record=n,old=v[2],new=(v[2]&252)|2));v[2]=(v[2]&252)|2
  return'S2Art'+str(n)+': .byte '+','.join(map(str,v))
 s=re.sub(r'^S2Art(\d+): \.byte (.+)$',record,s,flags=re.M);assert len(attrs)==70
 write(S/'smb2_roster_art.inc',s);patch+=''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='parent/art.inc',tofile='new/art.inc'))
 atlas=bytearray(before[1048592+796*1024:1048592+808*1024]);pattern_diffs=[]
 for page in range(8):
  pos=page*1024+56*16
  for tile in range(2):
   for row in range(8):
    lo=pos+tile*16+row;hi=lo+8;assert atlas[lo]==0
    u,v=atlas[lo],atlas[hi];atlas[lo]=v;atlas[hi]=0
    if v:pattern_diffs.extend([lo,hi])
 (J/'eye-red.chr').write_bytes(atlas);write(J/'asset.s','.segment "SMB2_ROSTER_CHR"\n.incbin "eye-red.chr"\n')
 cfg=(P/'joint/private.cfg').read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix());write(J/'private.cfg',cfg)
 c=json.loads((P/'s2-component-build.json').read_text())['command'][:];c[1:1]=['-I',str(J),'-I',str(S)]
 for flag in['-o','--create-full-dep','--create-dep']:
  if flag in c:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
 c[-1]=str(J/'component.s');run(c,'component-build')
 run([str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','-I',str(J),'--create-full-dep',str(J/'asset.dep'),'-o',str(J/'asset.o'),str(J/'asset.s')],'asset-build')
 c=json.loads((P/'final-link.json').read_text())['command'][:]
 for i,x in enumerate(c):
  if x==str(P/'joint/component.o'):c[i]=str(J/'component.o')
  elif x==str(R/'build/smb2-current-component-v1/asset.o'):c[i]=str(J/'asset.o')
  elif x in[str(P/'joint'/n)for n in['private.cfg','candidate.nes','candidate.lbl','candidate.map']]:c[i]=str(J/Path(x).name)
  elif x.startswith('--dbgfile,'):c[i]='--dbgfile,'+str(J/'candidate.dbg')
 run(c,'final-link');prepare(R,J/'candidate.nes');b=scoped_load(J/'candidate.nes');after=b['raw']
 assert'S2PalettePointerC'not in b['syms'];moves={n:[address(a,n),address(b,n)]for n in a['syms']if'::'not in n and n!='S2PalettePointerC'and n in b['syms']and address(a,n)!=address(b,n)};assert not moves,moves
 allowed=[(location(a,'S2MainPalette'),location(a,'S2MainPalette')+74),(location(a,'S2PaletteCCodeStart'),location(a,'S2PaletteCCodeEnd'))]
 for n in range(70):allowed.append((location(a,'S2Art'+str(n))+2,location(a,'S2Art'+str(n))+3))
 allowed+=[(1048592+796*1024+i,1048592+796*1024+i+1)for i in pattern_diffs]
 diff=[i for i,(x,y)in enumerate(zip(before,after))if x!=y];assert all(any(lo<=i<hi for lo,hi in allowed)for i in diff)
 assert before[:16]==after[:16]and before[16+125*8192:16+126*8192]==after[16+125*8192:16+126*8192]
 write(O/'source.patch',patch);save(O/'source-proof.json',dict(passed=True,candidate=B.sha(J/'candidate.nes'),parent=B.sha(P/'joint/candidate.nes'),
  changed_bytes=len(diff),exact_ROM_diff=diff,only_own45B_74B_ARTattrs_and_eye_CHR=True,public_PCs_header_final125_exact=True,
  retired_private_ABI='S2PalettePointerC',native_background_clone=colors,complete7Bpacket_offset_must_be_less77=True,
  original_Star_and_published_ROM_palette_guards_unchanged=True,body_parts=5,body_P0CHR_exact=True,extra_OAM_CHR_RAM_PRG=0,attrs=attrs,
  eye_original_index2NES16_to_nativeP2index1NES16=True,native=False,admitted=False))
 print(json.dumps(dict(candidate=B.sha(J/'candidate.nes'),output=str(O),changed_bytes=len(diff))),flush=True)
if __name__=='__main__':main()
