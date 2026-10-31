"""Reviewed source-only Thomas classifier funding; immutable a126 ancestry."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
import thomas_original_cpu_1031_v1 as T
P=R/'build/thomas-physical-host-1031-v9';O=R/'build/thomas-private-ingress-1031-v3'
J=R/'build/bt-p2-cf-menu-source-1031-v2/joint';U=R/'build/cf-bt-shared-transport-v3/joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 assert not O.exists();S=O/'source';S.mkdir(parents=True);(O/'sideoutputs').mkdir()
 stage=json.loads((P/'source-stage.json').read_text())
 for p,h in stage['bindings'].items():assert sha(p)==h,p
 for p in(P/'source').iterdir():
  if p.is_file():shutil.copyfile(p,S/p.name)
 cfg=(P/'candidate.cfg').read_text().replace(P.as_posix(),O.as_posix()).replace(str(P),str(O));(O/'candidate.cfg').write_text(cfg)
 entry=(J/'entrypoint.s').read_text();(S/'entrypoint.s').write_text(entry)
 source=R/'build/bt-ready-menu-1031-v2/joint/src/new_roster_dispatch.s';text=source.read_text()
 text='.import ThGmHeadWithinOwn\n'+text
 bank='TargetBank:.byte .lobyte(.bank(Legacy)|$80),.lobyte(.bank(Ice)|$80),.lobyte(.bank(City)|$80),.lobyte(.bank(Sunny)|$80),.lobyte(.bank(Gimmick)|$80)'
 bank=' .if .xmatch({Name},{NrDraw})\n::ThNrDrawBankTable:\n .endif\n'+bank
 replacement=''' .if .xmatch({Name},{NrGraphics})
TargetBank=ThNrDrawBankTable
 .elseif .xmatch({Name},{NrPortrait})
TargetBank=NrMovement::TargetBank
 .else
'''+bank+'''
 .endif'''
 needle=bank[bank.index('TargetBank:.byte'):]
 assert needle in text;text=text.replace(needle,replacement)
 text=text.replace(' .res Size-42-24*Explicit-ExtraSize,$ff',' .if .xmatch({Name},{NrGraphics}) .or .xmatch({Name},{NrPortrait})\n .res Size-37-24*Explicit-ExtraSize,$ff\n .else\n .res Size-42-24*Explicit-ExtraSize,$ff\n .endif')
 a=text.index('.macro GmExtraNrGraphics');b=text.index('.macro GmExtraNrDraw',a)
 old=text[a:b]
 new='''.macro GmExtraNrGraphics
.scope GmOwnedHelper51
 .byte $ff
::GmMenuName:
 farcall HuGmMenuName,jmp
::HuOnlyRare:
 tya
 clc
 adc #15
 asl
 asl
 asl
 asl
 sta FarcallJmpTarget_SMC+1
 lda #>HuEntryBase
 adc #0
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(HuEntryBase)|$80)
 jmp GmNrFinish
::ThOnlyCheck:
 cmp #10
 bne Foreign
 lda FmAlts
 and #$44
 cmp #$40
 beq HuOnlyRare
 lda #10
Foreign:jmp GmOnlyCompareStart
.endscope
.endmacro
GmHeadWithinOwn=ThGmHeadWithinOwn
GmNrRoute NrGraphics,IcGraphics,RcGraphics,SunnyGraphicsIntegrated,RlGraphicsDispatch,GmHostGraphics,97,GmExtraNrGraphics,60,0
'''
 text=text[:a]+new+text[b:]
 a=text.index('::GmNrIndex:');b=text.index('.endscope',a)
 text=text[:a]+'''::GmNrIndex:
 lda SelectedCharacter
 cmp #20
 bcc Low
 cmp #27
 bcs Rare
 sec
 sbc #20
 tay
 lda HighMap,y
 bmi Rare
 tay
 rts
Rare:jmp HuNrRarePrefix
Low:
 cmp #2
 beq Rare
 cmp #10
 beq Rare
 cmp #9
 bne Legacy
 lda FmAlts
 and #32
 bne Rare
Legacy:ldy #0
 rts
HighMap:.byte 1,2,$ff,3,$ff,$ff,4
 .byte $ff
'''+text[b:]
 text=text.replace('::GmOnlyCommon:\n lda SelectedCharacter\n cmp #2',' .word $ffff\n::GmOnlyCommon:\n lda SelectedCharacter\n jmp ThOnlyCheck\n::GmOnlyCompareStart:\n cmp #2',1)
 text=text.replace('97,GmExtraNrPortrait,55,0','97,GmExtraNrPortrait,60,0')
 (S/'new_roster_dispatch.s').write_text(text)
 # Genuine equal bank expressions are asserted, not inferred from one byte.
 asserts='\n'
 for left,right in [('RlGraphicsDispatch','RlDrawDispatch'),('JnPortraitDispatch','JnMovementDispatch')]:asserts+=f'.assert .bank({left})=.bank({right}),lderror,"Thomas source bank-table alias"\n'
 for x in ['IcGraphics','RcGraphics','SunnyGraphicsIntegrated','GmHostGraphics']:
  y={'IcGraphics':'IcDraw','RcGraphics':'RcDraw','SunnyGraphicsIntegrated':'SunnyDraw','GmHostGraphics':'GmDraw'}[x]
  asserts+=f'.assert .bank({x})=.bank({y}),lderror,"Thomas genuine graphics/draw bank alias"\n'
 for x,y in [('IcPortrait','IcMovement'),('RcPortrait','RcMovement'),('SunnyPortrait','SunnyNativeMovement'),('GmPortraitPrepare','GmHostMovement')]:asserts+=f'.assert .bank({x})=.bank({y}),lderror,"Thomas genuine portrait/movement bank alias"\n'
 (S/'new_roster_dispatch.s').write_text(text+asserts)
 union=(U/'union.s').read_text();union='.import ThServiceVeneers,ThArExtended\n'+union
 # Reuse actual six-byte prefix for an existing six-byte private helper.
 union=union.replace('HuGenericIndex:\n lda SelectedCharacter\n jmp HuQClass','HuQuickAltTest:\n lda FmAlts\n and #32\n rts',1)
 union=union.replace('::HuQClass:\n cmp #25\n jmp HuS2Decide',' .res 5,$ff',1)
 union=union.replace('.proc HuCommon\n jmp HuGenericIndex', '''.proc HuCommon
::HuGenericIndex:
 lda SelectedCharacter
 cmp #10
 bne ThForeign
 lda FmAlts
 and #$44
 cmp #$40
 bne ThForeign
 lda #.lobyte(.bank(ThServiceVeneers)|$80)
 jmp ThFFBankReady
ThForeign:
::HuQClass:
 cmp #25
 jmp HuS2Decide''',1)
 union=union.replace('::HuQuickAltTest:\n lda FmAlts\n and #32\n rts\n','',1)
 a=union.index('HuExtendedFF:\n');b=union.index('HuExtendedSet:\n',a)
 union=union[:a]+'''HuExtendedFF:
 lda #.lobyte(.bank(FwServiceVeneers)|$80)
ThFFBankReady:
 pha
 lda #>FwServiceVeneers
 sta FarcallJmpTarget_SMC+2
 pla
 bne HuExtendedSet
HuExtendedArthur:
 lda #<ThArExtended
 sta FarcallJmpTarget_SMC+1
 lda #>ThArExtended
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(ThArExtended)|$80)
 jsr FarCallCommon
 bne HuExtendedSet
'''+union[b:]
 union=union.replace(' asl\n clc\n adc FarcallJmpTarget_SMC+1',' asl\n adc FarcallJmpTarget_SMC+1',1)
 union=union.replace('.assert *<=$ba3d','.assert *<=$ba54').replace('.res $045d-(*-HuStart)','.res $0474-(*-HuStart)')
 union+='\n.assert >ThServiceVeneers=>FwServiceVeneers,lderror,"Actual page-high shared Thomas/FF transport"\n.assert .lobyte(ThServiceVeneers)=0,lderror,"Thomas table low-byte0"\n'
 (S/'union.s').write_text(union)
 cc=R/'tools/Windows/cc65/bin';commands=[]
 def run(cmd):
  guard=validate(cmd,O,cwd=R);p=subprocess.run(list(map(str,cmd)),cwd=R,text=True,capture_output=True);row=dict(command=list(map(str,cmd)),output_guard=guard,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr);commands.append(row);dump(O/'build-commands.json',commands);assert not p.returncode,p.stderr;return row
 def recompile(recipe,name,source):
  cmd=list(json.loads(recipe.read_text())['command']);cmd[-1]=str(source)
  for opt in ['-o','-l','--create-full-dep']:
   if opt in cmd:cmd[cmd.index(opt)+1]=str(O/(name+{'-o':'.o','-l':'.lst','--create-full-dep':'.dep'}[opt]))
  if '--create-full-dep'not in cmd:cmd[1:1]=['--create-full-dep',str(O/f'{name}.dep')]
  cmd[1:1]=['-I',str(S)]
  dump(O/f'{name}-build.json',run(cmd))
 recompile(J.parent/'main-build.json','main',S/'entrypoint.s')
 recompile(U.parent/'union-build.json','union',S/'union.s')
 oldinputs=[Path(v)for v in json.loads((P/'final-link.json').read_text())['command']if str(v).endswith('.o')]
 inputs=[]
 for p in oldinputs:
  if p==J/'main.o':p=O/'main.o'
  elif p==U/'union.o':p=O/'union.o'
  elif p.parent==P:
   shutil.copyfile(p,O/p.name);p=O/p.name
  inputs.append(p)
 def link(tag):
  cmd=[cc/'cl65.exe','--cpu','6502x','-t','nes','-C',O/'candidate.cfg','-Ln',O/'candidate.lbl','--ld-args','--dbgfile,'+str(O/'candidate.dbg'),'-o',O/'candidate.nes',*inputs];dump(O/f'{tag}-link.json',run(cmd))
 link('preflight')
 raw=(O/'candidate.nes').read_bytes();fixed=raw[16+127*8192:16+128*8192];(S/'fixed127.bin').write_bytes(fixed)
 for name in ['mirror']:
  run([cc/'ca65.exe',S/f'{name}.s','-I',S,'-g','-o',O/f'{name}.o','--create-full-dep',O/f'{name}.dep'])
 # All inherited S2 DMC code mirrors derive from this same final127 source.
 clones=(R/'build/functional-roster-coherent62-v4/joint/dmc-clones.s').read_text();clones=re.sub(r'"[^"\n]*final127.bin"','"'+(S/'fixed127.bin').as_posix()+'"',clones);(S/'dmc-clones.s').write_text(clones)
 oldclone=R/'build/functional-roster-coherent62-v4/joint/dmc-clones.o';inputs=[O/'dmc-clones.o'if p==oldclone else p for p in inputs]
 run([cc/'ca65.exe',S/'dmc-clones.s','-g','-o',O/'dmc-clones.o','--create-full-dep',O/'dmc-clones.dep'])
 link('final');assert (O/'candidate.nes').read_bytes()[16+127*8192:16+128*8192]==fixed
 s=T.labels(O/'candidate.lbl');old=T.labels(P/'candidate.lbl');moved={n:dict(old=f'{v:04X}',new=f'{s[n]:04X}')for n,v in old.items()if n in s and s[n]!=v}
 public=['NrMovement','NrGraphics','NrDraw','NrPortrait','NrWeapons','NrInjury','NrLegacyInjuryStatus','NrDeath','NrVisible','NrHead']
 public+=['HuEntryBase']
 public+=[n for n in old if n.startswith('Hu')and n in ['HuMovement','HuGraphics','HuDraw','HuPortrait','HuWeapons','HuInjury','HuInjuryStatus','HuDeathStart','HuDeath','HuVisible','HuHead','HuBody','HuAdder','HuBox','HuSide','HuFresh','HuFullBox','HuMenuPortrait','HuMenuName','HuReset','HuPrepare','HuRise','HuPrivate','HuCollision','HuPickup','HuFullPower','HuColors','HuBounce','HuHeadWithin','HuUI','HuName','HuStomp','HuWorld','HuPowerup','HuWeaponTail','HuVine']]
 assert all(s[n]==old[n]for n in public)
 dump(O/'moved-symbols.json',moved)
 # Inventory every true object import of moved globals, and resolved numeric
 # appearances in all retained source/cache carriers for human review.
 imports={}
 for p in inputs:
  txt=subprocess.run([str(cc/'od65.exe'),'--dump-imports',str(p)],capture_output=True,text=True,check=True).stdout
  hits=sorted(set(re.findall(r'Name:\s*"([^"]+)"',txt))&set(moved))
  if hits:imports[str(p)]=hits
 dump(O/'moved-import-consumers.json',imports)
 before=(P/'candidate.nes').read_bytes();after=(O/'candidate.nes').read_bytes();diff=[i for i,(a,b)in enumerate(zip(before,after))if a!=b]
 dump(O/'source-stage.json',dict(passed=True,source_only=True,pending=True,native=False,private_shared_prototype=True,parent_sha256=sha(P/'candidate.nes'),candidate_sha256=sha(O/'candidate.nes'),changed_bytes=len(diff),public_entries_exact=public,moved_symbols_receipt=str(O/'moved-symbols.json'),import_consumers=str(O/'moved-import-consumers.json'),Hu_bytes=s['HuEnd']-s['HuStart'],limits=['Private classifier funding prototype only; lifecycle and naturalMain still unhooked','Specific internal Hu helper moves require full import/carrier closure before adoption'],bindings={str(p):sha(p)for p in[Path(__file__),P/'source-stage.json',source,U/'union.s',J/'entrypoint.s',J.parent/'main-build.json',U.parent/'union-build.json',*inputs,*[p for p in O.rglob('*')if p.is_file()]]}))
 print(json.dumps(dict(ROM=sha(O/'candidate.nes'),Hu_bytes=s['HuEnd']-s['HuStart'],moved=len(moved),imports=imports,stage=sha(O/'source-stage.json'))))
if __name__=='__main__':main()
