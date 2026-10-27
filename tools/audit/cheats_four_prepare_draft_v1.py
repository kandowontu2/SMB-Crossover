from pathlib import Path
import json,shutil,hashlib,difflib,subprocess,sys
ROOT=Path(r'C:/Users/kando/Documents/ChatGPT/SMB Crossover')
D=Path(r'C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'root-current-roster-composition-v1'
O=D/'current3b-cheats-four-draft-v8'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,o):Path(p).write_text(json.dumps(o,indent=2)+'\n',newline='\n')
raise SystemExit('Historical clone preparer disabled after storage-priority change; reuse current3b-cheats-four-draft-v8 only.')
assert not O.exists();O.mkdir();S=O/'source';S.mkdir()
m=json.loads((P/'source-manifest.json').read_text())
for n,h in m.items():
 assert sha(P/'source'/n)==h,n
 f=S/n;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,f)
changes=[];patch=[]
def edit(n,old,new):
 f=S/n;b=f.read_bytes();e='\r\n' if b'\r\n' in b else '\n';t=b.decode().replace('\r\n','\n');assert t.count(old)==1,(n,old[:100],t.count(old));t=t.replace(old,new,1);f.write_bytes(t.replace('\n',e).encode())
 changes.append({'path':n,'old':sha(P/'source'/n),'new':sha(f)})
 patch.extend(difflib.unified_diff(b.decode().splitlines(True),f.read_bytes().decode().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
def proc(n,name,span,target):
 f=S/n;t=f.read_bytes().decode().replace('\r\n','\n');a=t.index('.proc '+name+'\n');b=t.index('.endproc',a)+len('.endproc');old=t[a:b]
 new=f'.proc {name}\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  farcall {target},jmp\n  .res {span}-18,$ea\n.else\n'+old.split('\n',1)[1].rsplit('.endproc',1)[0]+'.endif\n.endproc'
 edit(n,old,new)
proc('src/cheats.s','CheatsMenuInput',94,'CheatsSixInput')
proc('src/cheats.s','QueueCheats',174,'CheatsSixQueue')
proc('src/cheats.s','CheatsPatchPage',54,'CheatsSixPage')
edit('src/cheats.s','bank14 A tail','bank20/$14 A tail')
edit('src/guest_injury.s','  lda GuestHurtKind\n  beq Run\n  farcall GuestInjuryGameRoutines, jmp\nRun:\n  farcall GameRoutines, jmp','''  lda GuestHurtKind
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  ora CheatInvincible
  beq Run
  farcall CheatsGameRoutinesGate,jmp
Run:
  farcall GameRoutines,jmp
  .byte $ea
.else
  beq Run
  farcall GuestInjuryGameRoutines,jmp
Run:
  farcall GameRoutines,jmp
.endif''')
edit('src/guest_source_stomp.s','.segment "OAMALIGNED"\n.proc GuestWaterStompPolicy','.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.segment "LOWCODE"\n.else\n.segment "OAMALIGNED"\n.endif\n.proc GuestWaterStompPolicy')
# Genuine moved policy must be emitted immediately after predicate, not here.
f=S/'src/guest_source_stomp.s';t=f.read_bytes().decode().replace('\r\n','\n');a=t.index('.proc GuestWaterStompPolicy');b=t.index('.endproc',a)+len('.endproc');old=t[a:b]
edit('src/guest_source_stomp.s',old,'.if .not (::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5)\n'+old+'\n.endif')
edit('src/common.s','  lda InjuryTimer\n  ora CheatInvincible\n  rts',''' .if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  jmp CheatsInjuryMask
::GuestWaterStompPolicy:
  lda GuestBodyStompAllowed
  rts
 .else
  lda InjuryTimer
  ora CheatInvincible
  rts
 .endif''')
edit('src/mmc5.s','Cv3AdderOther:jmp Cv3LegacyAdderOther\n  .res 136-(*-StartPublication),$ea','''Cv3AdderOther:jmp Cv3LegacyAdderOther
::CheatsInjuryMask:
  lda CheatInvincible
  and #1
  ora InjuryTimer
  rts
  .res 136-(*-StartPublication),$ea''')
edit('src/vic_adapter.s',' lda CheatInvincible\n jne Done\n ldx #0\n jmp KillPlayer',''' .if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
 lda CheatInvincible
 and #1
 beq CheatSolidDeath
 rts
CheatSolidDeath:
 ldx #0
 jmp KillPlayer
 .else
 lda CheatInvincible
 jne Done
 ldx #0
 jmp KillPlayer
 .endif''')
edit('smb1base-mmc5-expanded.cfg','    X5_NEW_3F: start=$a000','    X5_NEW_3F: start=$a000') if False else None
edit('smb1base-mmc5-expanded.cfg','    X5_MENU_UI:load=X5_NEW_63,type=ro;','    CHEATS_FOUR:load=X5_NEW_3F,type=ro; # decimal63/$3F; isolated cold Cheats\n    X5_MENU_UI:load=X5_NEW_63,type=ro;')
f=S/'src/entrypoint.s';b=f.read_bytes();e=b'\r\n'if b'\r\n'in b else b'\n';f.write_bytes(b+b'\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "cheats_four.s"\n.endif\n'.replace(b'\n',e));changes.append({'path':'src/entrypoint.s','old':sha(P/'source/src/entrypoint.s'),'new':sha(f)})
shutil.copyfile(ROOT/'tools/audit/cheats_four_cold_draft_v1.s',S/'src/cheats_four.s')
put(O/'source-manifest.json',{str(f.relative_to(S)).replace('\\','/'):sha(f)for f in S.rglob('*')if f.is_file()});put(O/'changes.json',changes)
(O/'implementation.patch').write_bytes(''.join(patch).encode())
cmd=[sys.executable,'-B',str(ROOT/'tools/build_mmc5_expanded.py'),'--source-overlay',str(S),'--output',str(O/'candidate.nes')]
z=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);put(O/'build.json',dict(command=cmd,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));print(z.stdout[-9000:]);print(z.stderr[-1000:]);assert z.returncode==0
print(sha(O/'candidate.nes'))
