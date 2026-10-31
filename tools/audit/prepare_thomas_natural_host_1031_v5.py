"""Named-span private Thomas natural Main/lifecycle experiment; no installation."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
import thomas_original_cpu_1031_v1 as T
P=R/'build/thomas-private-ingress-1031-v5';O=R/'build/thomas-natural-host-1031-v5';A=R/'build/future-start-masks-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 assert not O.exists();S=O/'source';S.mkdir(parents=True);(O/'sideoutputs').mkdir()
 stage=json.loads((P/'source-stage.json').read_text())
 for p,h in stage['bindings'].items():assert sha(p)==h,p
 shutil.copytree(P/'source',S,dirs_exist_ok=True)
 for p in S.rglob('*'):
  if p.is_file()and p.suffix in['.s','.inc']:
   p.write_text(p.read_text().replace(P.as_posix(),O.as_posix()).replace(str(P),str(O)))
 cfg=(P/'candidate.cfg').read_text().replace(P.as_posix(),O.as_posix()).replace(str(P),str(O));(O/'candidate.cfg').write_text(cfg)
 original=R/'build/bt-ready-menu-1031-v2/joint/src'
 entry=(S/'entrypoint.s').read_text();entry='.import ThServiceVeneers,ThMenuResolve,ThSceneInit\n.export MovePlayerVertically,VerticalForce,ThKbNativeFallback\n'+entry;(S/'entrypoint.s').write_text(entry)
 (S/'hot_render_gate.s').write_text((R/'tools/reference/thomas_hot_render_1031_v3.s').read_text())
 text=(original/'x5_bounce.s').read_text();a=text.index('.proc X5OwnMovement');b=text.index('.endproc',a)
 old=text[a:b]
 new='''.proc X5OwnMovement
 .if ::MAPPER_MMC5
 jmp ThMovementIngress
::ThMovementIngress:
 php
 pha
 lda SelectedCharacter
 cmp #10
 bne Foreign
 lda FmAlts
 and #$44
 cmp #$40
 bne Foreign
 pla
 plp
 farcall ThServiceVeneers,jmp
Foreign:
 pla
 plp
 jmp CdCameraMovementAdmission
 .res 49-(*-::X5OwnMovement),$ea
 .assert *-::X5OwnMovement=49,lderror,"Thomas exact original X5OwnMovement49B"
 .else
'''+old[old.index(' .else')+len(' .else'):]
 text=text[:a]+new+text[b:];(S/'x5_bounce.s').write_text(text)
 (S/'kirby.s').write_text((original/'kirby.s').read_text())
 text=(original/'kirby_draw.s').read_text();a=text.index('.proc KbDrawDispatch');b=text.index('.endproc',a)
 text=text[:a]+'''.proc KbDrawDispatch
 farcall ThSharedDrawHot,jmp
::ThKbNativeFallback:
 cmp #CHARACTER_SIMON
 bne Legacy
 farcall Cv3DrawDispatch,jmp
Legacy:jmp Z2DrawGuard
 .res 50-(*-::KbDrawDispatch),$ea
 .assert *-::KbDrawDispatch=50,lderror,"Thomas exact original KbDrawDispatch50B"
'''+text[b:];(S/'kirby_draw.s').write_text(text)
 text=(original/'megaman_environment.s').read_text();assert text.count('farcall HuAfterTerrainGate,jmp')==1;text=text.replace('farcall HuAfterTerrainGate,jmp','farcall ThPostNativeHot,jmp');(S/'megaman_environment.s').write_text(text)
 text=(R/'build/contra-force-menu-admission-1031-v2/joint/src/character_select.s').read_text();text=text.replace('BwMenuResolve','ThMenuResolve');(S/'character_select.s').write_text(text)
 text=(R/'build/bt-p2-cf-menu-source-1031-v2/joint/src/screen_render.s').read_text();assert 'BwScene'in text;text=text.replace('BwScene','ThSceneInit');(S/'screen_render.s').write_text(text)
 text=(R/'build/contra-force-menu-admission-1031-v2/joint/src/full_roster_menu.s').read_text();assert text.count(' lda #32\n sec\n rts')==1;text=text.replace(' lda #32\n sec\n rts',' lda #32\n clc\n rts');(S/'full_roster_menu.s').write_text(text)
 # Root-approved exact405B masks, not a new Thomas-specific mask scheme.
 (S/'cf_menu_body.inc').write_text((A/'joint/src/cf_menu_body.inc').read_text())
 # No new kernel address aliases; the original jump-reset is a true export.
 (S/'component.s').write_text((S/'component.s').read_text()+'\n.export Th_A884\n')
 text=(R/'tools/reference/thomas_cache_host_1031_v5.s').read_text()
 for n in sorted(set(re.findall(r'^([A-Za-z_]\w*):',text,re.M)),key=len,reverse=True):
  if not n.startswith(('Th','Thomas')):text=re.sub(r'\b'+n+r'\b','ThNatural'+n,text)
 (S/'cache.s').write_text(text)
 cc=R/'tools/Windows/cc65/bin';commands=[]
 def run(cmd):
  guard=validate(cmd,O,cwd=R);r=subprocess.run(list(map(str,cmd)),cwd=R,capture_output=True,text=True);v=dict(command=list(map(str,cmd)),output_guard=guard,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr);commands.append(v);dump(O/'build-commands.json',commands);assert not r.returncode,r.stderr;return v
 def asm(n):return run([cc/'ca65.exe',S/f'{n}.s','-I',S,'-g','-o',O/f'{n}.o','--create-full-dep',O/f'{n}.dep'])
 cmd=list(json.loads((P/'main-build.json').read_text())['command']);cmd[-1]=str(S/'entrypoint.s');cmd[1:1]=['-I',str(S)]
 for key,ext in[('-o','o'),('-l','lst'),('--create-full-dep','dep')]:
  if key in cmd:cmd[cmd.index(key)+1]=str(O/f'main.{ext}')
 dump(O/'main-build.json',run(cmd))
 for n in['cache','component','resident','carrier']:asm(n)
 oldinputs=[Path(v)for v in json.loads((P/'final-link.json').read_text())['command']if str(v).endswith('.o')];inputs=[]
 for p in oldinputs:
  if p.parent==P:
   if p.name not in['main.o','cache.o','component.o','resident.o','carrier.o']:shutil.copyfile(p,O/p.name)
   p=O/p.name
  inputs.append(p)
 def link(tag):
  cmd=[cc/'cl65.exe','--cpu','6502x','-t','nes','-C',O/'candidate.cfg','-Ln',O/'candidate.lbl','--ld-args','--dbgfile,'+str(O/'candidate.dbg'),'-o',O/'candidate.nes',*inputs];dump(O/f'{tag}-link.json',run(cmd))
 link('preflight');s=T.labels(O/'candidate.lbl');kernel=(O/'kernel.bin').read_bytes();state=(O/'state.bin').read_bytes();assert s['ThAllKernelEnd']-0xa000<=6144,'Repack carrier source if code becomes7pages'
 cookie=bytes([167,10,64,1])+hashlib.sha256(kernel+state).digest()[:12];(S/'cookie.bin').write_bytes(cookie)
 carrier=kernel[:6144]+state[0x1000:0x1800]+(R/'build/thomas-sparse-template-1031-v1/body.chr').read_bytes();(S/'carrier.chr').write_bytes(carrier+bytes(16384-len(carrier)))
 raw=(O/'candidate.nes').read_bytes();fixed=raw[16+127*8192:16+128*8192];(S/'fixed127.bin').write_bytes(fixed)
 for n in['resident','carrier','mirror','dmc-clones']:asm(n)
 link('final');assert (O/'kernel.bin').read_bytes()==kernel and(O/'state.bin').read_bytes()==state
 s=T.labels(O/'candidate.lbl');old=T.labels(P/'candidate.lbl');must=['HotPlayerGraphics','HotNewCharacterDraw','KbDrawDispatch','X5OwnMovement','RyuSourceBodyAfterBGBridge','FmStartRetireFlags','FmCfRestoreP1','FmPending','FmResolve','GameLoop','ThServiceVeneers','ThLoad','ThCheckCode','ThGmHeadWithinOwn','ThArExtended','BwServiceVeneers','BtServiceVeneers']
 must+=[n for n in old if n.startswith('Nr')and n in json.loads((P/'source-stage.json').read_text())['public_entries_exact']]
 assert all(s[n]==old[n]for n in must),[(n,old[n],s.get(n))for n in must if s.get(n)!=old[n]]
 moved={n:[f'{v:04X}',f'{s[n]:04X}']for n,v in old.items()if n in s and s[n]!=v};dump(O/'moved-symbols.json',moved)
 # Root405 producer bytes exactly reappear, with no filler outside its grant.
 from check_tmnt_render_oa import location
 import ff_wram_host_controls_v7 as H
 bs=[H.C.qualified(p)for p in[A/'joint/candidate.nes',O/'candidate.nes']]
 starts=[location(b,'FmCfHelperStart')for b in bs]
 assert bs[0]['raw'][starts[0]:starts[0]+405]==bs[1]['raw'][starts[1]:starts[1]+405]
 dump(O/'source-stage.json',dict(passed=True,source_only=True,native=False,installed=False,parent_sha256=sha(P/'candidate.nes'),candidate_sha256=sha(O/'candidate.nes'),private_Thomas_ready=True,code_bytes=s['ThAllKernelEnd']-0xa000,resident_bytes=s['ThAllResidentEnd']-0xb33a,root405_source_exact=True,public_PC_exact=must,limits=['Unqualified natural Main experiment; no release/admission/native claim','Original native fall only when unsupported; original donor input/B6 jump/melee remain source workers'],bindings={str(p):sha(p)for p in[Path(__file__),P/'source-stage.json',A/'source-stage.json',R/'tools/reference/thomas_cache_host_1031_v5.s',R/'tools/reference/thomas_hot_render_1031_v3.s',*inputs,*[p for p in O.rglob('*')if p.is_file()]]}))
 print(json.dumps(dict(ROM=sha(O/'candidate.nes'),kernel=s['ThAllKernelEnd']-0xa000,stage=sha(O/'source-stage.json'))))
if __name__=='__main__':main()
