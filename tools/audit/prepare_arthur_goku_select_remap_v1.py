"""Private exact-source Arthur/Goku Select move; new Battletoads slot pending.

No original physics/audio/art is changed. No new resource lease or native
process is used. Existing gate tail and menu budgets are asserted exactly.
"""
from pathlib import Path
from itertools import groupby
import difflib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
P=R/'build/functional-roster-coherent62-v4';O=R/'build/arthur-goku-select-remap-v1';J=O/'joint'

def once(t,a,b):assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)
def main():
 assert not O.exists();h=json.loads(B.read(P/'handoff.json'));B.bound(h)
 assert h['candidate']=='408acae2712c1d9bbbe34233f8261fcf27723907d37acf020e3f5314be3b8604'
 old=load(P/'joint/candidate.nes');nrseg=next(g for g in old['segs'].values()if g['name']=='"NEW_ROSTER_GATE"')
 assert int(nrseg['start'],0)==0xa000 and int(nrseg['size'],0)==0xdee
 tail=old['raw'][16+124*8192+0xdee:16+124*8192+0xe00];assert tail==b'\xff'*18
 assert not[n for n,s in old['syms'].items()if s.get('seg')==nrseg['id']and 0xadee<=int(s.get('val','0'),0)<0xae00]
 # The source hard boundary and next explicit native consumer, not fill
 # alone, establish this existing owner's cold tail budget.
 nrsrc=B.read(P/'joint/src/new_roster_dispatch.s');cfg=B.read(P/'joint/private.cfg')
 assert '.assert * <= $ae00,lderror,"Roster dispatcher overlaps Rogue auxiliary reservation"'in nrsrc
 assert 'ROGUE_DAWN_CONTROL_AUX:load=X5_NEW_7C,type=ro,start=$ae00'in cfg
 shutil.copytree(P/'joint',J);patch=[]
 def rt(t):return t.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
 for p in J.rglob('*'):
  if p.is_file()and p.suffix in ['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
 def edit(p,t):
  a=B.read(p);B.write(p,t);patch.extend(difflib.unified_diff(a.splitlines(True),t.splitlines(True),fromfile='frozen62/'+p.relative_to(J).as_posix(),tofile='ArGoku-remap/'+p.relative_to(J).as_posix()))
 # Retain the genuine4B entry; only the budgeted cold tail gains code.
 p=J/'src/new_roster_dispatch.s';t=B.read(p)
 t=once(t,'.proc NrMenuCharacter\n lda X5MenuCharacters,x\n rts\n.endproc','.proc NrMenuCharacter\n jmp NrMenuAltTail\n nop\n.endproc')
 end='.segment "NEW_ROSTER_GATE"\n.assert * <= $ae00,lderror,"Roster dispatcher overlaps Rogue auxiliary reservation"'
 t=once(t,end,'''.segment "NEW_ROSTER_GATE"
.assert * = $adee,lderror,"Original gate tail preimage moved"
NrMenuColdPadStart:
.proc NrMenuAltTail
 lda X5MenuCharacters,x
 php
 cpx #31
 bne Done
 bit FmAlts
 bpl Done
 lda #24
Done:plp
 rts
.endproc
.assert *-NrMenuColdPadStart=17,lderror,"Arthur/Goku cold helper size"
.res $ae00-*,$ff
.assert * = $ae00,lderror,"Existing gate-owned cold pad boundary"''');edit(p,t)
 p=J/'src/roster_expansion_menu.inc';t=B.read(p);a=' .byte 0,1,2,3,4,5,6,7,12,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32'
 edit(p,once(t,a,a.replace('22,23,24,25','22,23,33,25')))
 p=J/'src/full_roster_menu.s';t=B.read(p)
 pending_size=address(old,'FmResolve')-address(old,'FmPending')
 toggle_size=address(old,'FmQueueName')-address(old,'FmToggle')
 t=once(t,'NotFF:\n cpx #23\n beq Ready\n','NotFF:\n')
 t=once(t,'NotSMB2:\n lda #14\n cpx #25\n beq Pending\n','NotSMB2:\n')
 t=once(t,'NotBowser:\n lda #17\n cpx #27\n beq Pending\n','NotBowser:\n')
 t=once(t,' lda #30\n clc\n rts\nForceVariant:',''' lda FmAlts
 bmi Goku
 lda #30
 bne ArthurGokuReady
Goku:lda #9
ArthurGokuReady:clc
 rts
ForceVariant:''')
 t=once(t,'Pending:sec\n rts\n.endproc',f'''Pending:sec
 rts
.assert *-FmPending<={pending_size},lderror,"Existing pending span"
.res {pending_size}-(*-FmPending),$ea
.endproc''')
 t=once(t,' and #Select_Button\n jeq No\n ldx CrossoverMenuIndex',' and #Select_Button\n bne HasSelect\n clc\n rts\nHasSelect:ldx CrossoverMenuIndex')
 t=once(t,' lda FmAlts\n and #$df\n sta FmAlts',' eor FmAlts\n sta FmAlts')
 a=''' lda FmAlts
 and #68
 beq SelectShinobi
 cmp #4
 beq SelectThomas
 lda #0
 beq RyuAlt
SelectShinobi:lda #4
 bne RyuAlt
SelectThomas:lda #64
RyuAlt:sta R0
 lda FmAlts
 and #$bb
 ora R0
 sta FmAlts
 jmp Yes'''
 b=''' lda FmAlts
 and #68
 beq SelectShinobi
 cmp #4
 beq SelectThomas
 lda FmAlts
 and #$bb
 sta FmAlts
 jmp Yes
SelectShinobi:lda #4
 bne Flip
SelectThomas:lda #68
 bne Flip'''
 t=once(t,a,b)
 t=once(t,'NotPrince:\n cpx #21','NotPrince:\n cpx #31\n bne NotArthur\n lda #$80\n jmp Flip\nNotArthur:\n cpx #21')
 t=once(t,'No:clc\n rts\n.endproc',f'''No:clc
 rts
.assert *-FmToggle<={toggle_size},lderror,"Existing Select span"
.res {toggle_size}-(*-FmToggle),$ea
.endproc''')
 # Source equivalent coordinates: each ASL produces C0 for X0/4/8/12,
 # so ADC has the exact original120/128 and159/175 output without tables.
 t=once(t,' lda FmPreviewX,x\n sta Sprite_Data+3,x\n lda FmPreviewY,x\n sta Sprite_Data,x',''' txa
 and #4
 asl
 adc #120
 sta Sprite_Data+3,x
 txa
 and #8
 asl
 adc #159
 sta Sprite_Data,x''')
 t=once(t,'FmPreviewX:.byte 120,0,0,0,128,0,0,0,120,0,0,0,128,0,0,0\nFmPreviewY:.byte 159,0,0,0,159,0,0,0,175,0,0,0,175,0,0,0\n','')
 t=once(t,'.include "full_roster_menu_art.inc"','''.include "full_roster_menu_art.inc"
;28B funded by26B coordinate/data compaction plus the old2B tail.
; Only the real Start path calls this; original flags survive except native
; final A0 N/Z, X/Y unchanged, and every foreign alternate byte is cleared.
.proc FmStartFlags
 php
 lda #$80
 cpx #31
 beq Mask
 lsr
 lsr
 cpx #9
 beq Mask
 lda #0
Mask:and FmAlts
 sta FmAlts
 plp
 lda #0
 sta FmGroups
 rts
.endproc
.assert *-FmStartFlags=28,lderror,"Start identity worker exact funding"''');edit(p,t)
 p=J/'src/character_select.s';t=B.read(p)
 a='''  php
  lda #0
  cpx #9
  bne QwStartStore
  lda FmAlts
  and #32
QwStartStore:
  sta FmAlts
  plp
  lda #0
  sta FmGroups'''
 edit(p,once(t,a,'''  farcall FmStartFlags
  .res 3,$ea ; Existing21B Start identity block, all later PCs unchanged.'''))
 # Honest pending BT placeholder: no Rash/Zitz pixels are fabricated or
 # mislabelled from Goku. Existing allzero pattern supplies a blank image.
 p=J/'src/full_roster_menu_art.inc';t=B.read(p);t=once(t,'     *GOKU      ','  *BATTLETOADS  ')
 preview=(J/'pending-previews.chr').read_bytes();blank=next(i*2 for i in range(128)if preview[i*32:(i+1)*32]==bytes(32))
 a=t.index('FmPreviewTiles:');b=t.index('FmPreviewColors:');lines=t[a:b].splitlines();assert len(lines)==34
 lines[10]=' .byte '+','.join([str(blank)]*4);t=t[:a]+'\n'.join(lines)+'\n'+t[b:];edit(p,t)
 # Remove the obsolete Goku gray thumbnail from the newly pending cell.
 # Blank is original menu tile36; its source pattern is verified zero.
 packed=(J/'packed.chr').read_bytes();assert packed[4096+36*16:4096+37*16]==bytes(16)
 encoded=(J/'menu.rle').read_bytes();nam=bytearray();i=0
 while encoded[i]:count,v=encoded[i:i+2];nam.extend([v]*count);i+=2
 assert len(nam)==1024
 for y in range(3):
  for x in range(2):nam[(4+23//8*4+y)*32+4+23%8*3+x]=36
 stream=bytearray()
 for v,g in groupby(nam):
  count=len(list(g))
  while count:n=min(count,255);stream.extend([n,v]);count-=n
 stream.append(0);(J/'menu.rle').write_bytes(stream)
 # Compile only actual Main; all imported public entries are asserted below.
 c=json.loads(B.read(P/'main-build.json'))['command'];c=[rt(x)for x in c];c[1:1]=['-I',str(J),'-I',str(J/'src')]
 link=json.loads(B.read(P/'final-link.json'))['command'][:]
 for i,x in enumerate(link):
  if x==str(P/'joint/main.o'):link[i]=str(J/'main.o')
 for flag in ['-o','-Ln','-m','--dbgfile','--mapfile','-C']:
  if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
 if '--ld-args'in link:
  k=link.index('--ld-args')+1;v=link[k].split(',')
  for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
  link[k]=','.join(v)
 checks=[dict(step=n,validation=validate(cmd,J,cwd=R))for n,cmd in [('main-build',c),('final-link',link)]]
 B.write(O/'output-preflight.json',json.dumps(checks,indent=2)+'\n')
 for name,cmd in [('main-build',c),('final-link',link)]:
  validate(cmd,J,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);B.write(O/(name+'.json'),json.dumps(dict(command=cmd,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,(name,z.stderr)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,J/'candidate.nes');new=load(J/'candidate.nes')
 names=['FmPending','FmResolve','FmToggle','FmQueueName','FmNativePrepare','FmDrawDkPreview','FmDrawPreview','FmDrawPreviewSelected','NrMenuCharacter','CrossoverMenuInput','MenuResolveCharacter','MaaFresh','HuEntryBase','HuEnd','GmCommonNmiStart','GmCommonNmiEnd','S2ServiceVeneers','QwService','DpAdmissionPortrait']
 for n in names:assert address(old,n)==address(new,n),n
 assert address(new,'NrMenuAltTail')==0xadee
 for n in ['ram3.bin','code.bin','data.bin','ff-cookie.bin','ff-stream.bin']:assert B.sha(J/n)==B.sha(P/'joint'/n),n
 a,b=old['raw'],new['raw'];assert a[:16]==b[:16]and a[1048592:]==b[1048592:]
 diffs=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];assert all((i-16)//8192 in [66,76,124]for i in diffs),sorted(set((i-16)//8192 for i in diffs))
 B.write(O/'source.patch',''.join(patch))
 d=dict(status='SOURCE_LINKED_ARTHUR_GOKU_REMAP_TARGETED_CONTROLS_PENDING',candidate=B.sha(J/'candidate.nes'),parent=h['candidate'],native=False,installed=False,ready=62,slots=32,pending_BT_slot=23,pending_BT_raw=33,BT_authentic_art_not_yet_joined=True,BT_current_pending_profiles=1,Arthur_default=dict(slot=31,raw=32),Goku_alternate=dict(slot=31,raw=24,FmAlts=128),old_Goku_body_at_slot23_removed=True,header_CHR_WRAM_payloads_exact=True,public_entries_checked=names,PRG_diff_banks=[66,76,124],PRG_diff_bytes=len(diffs),NrGate_tail=dict(start=0xadee,end=0xae00,original_segment_end=0xadee,original_fill_sha256=__import__('hashlib').sha256(tail).hexdigest(),prior_named_payload_refs=0,source_boundary_assert=True,next_consumer='ROGUE_DAWN_CONTROL_AUX AE00',helper_bytes=17,remaining_fill_bytes=1),bindings={str(p.resolve()):B.sha(p)for p in [Path(__file__),P/'handoff.json',J/'candidate.nes',J/'candidate.dbg',O/'output-preflight.json',O/'source.patch']})
 B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n');B.bound(h);print(json.dumps({k:v for k,v in d.items()if k!='bindings'}))

if __name__=='__main__':main()
