"""Sparse private fixed-page missile HUD prototype on preserved2082. No native."""
from pathlib import Path
import configparser,difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build';P='samus_fixed_hud'
BASE=B/'proto_palette_ack.nes'
EXPECTED='2082c19a7364920f828e97f70040d37f1f7059bde1ea136b5c2c4532324abf36'
sys.path.insert(0,str(R/'tools/audit'));sys.path.insert(0,str(R/'tools/reference'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from patch_samus_fixed_hud import plan
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HELPER='''; HUD-only fixed page20/pairs6,7; original world capsule untouched.
; SPECIAL_ROSTER is mapped in A. The renderer needs the same physical record
; at its genuine C-window alias, because farcall maps A to METASPRITE.
.pushseg
.segment "SPECIAL_ROSTER"
.proc SamusFixedMissileHud
 sta AvDrawDirection
 lda AvDrawArt
 cmp #AV_ART_SAMUSPICKUP7
 bne Native
 lda #<(SamusFixedHudRecord+$2000)
 sta R0
 lda #>(SamusFixedHudRecord+$2000)
 sta R1
 BankPRGC #.bank(SamusFixedHudRecord)
 jmp RemainingDraw::FixedHudRender
Native:
 jmp RemainingDraw::Draw
.endproc
SamusFixedHudRecord:
 .byte 8
 .byte $4d,$c2,-4,-5
 .byte $4f,$c2,-4,3
.assert SamusFixedMissileHud=$bfae,error,"Verified existing bank61 tail"
.assert *-SamusFixedMissileHud<=82,error,"Verified tail capacity"
.assert .bank(SamusFixedHudRecord)=61,error,"C alias must map physical61"
.popseg
'''

def main():
 assert sha(BASE)==EXPECTED
 b=scoped_load(BASE);raw=b['raw'];at=16+61*8192+0x1fae
 assert raw[at:16+62*8192]==bytes([255])*82
 for s in b['segs'].values():
  if 'ooffs'in s:
   pos,n=int(s['ooffs'],0),int(s['size'],0)
   assert not(n and pos<at+82 and at<pos+n),'Tail is allocated'
 table=raw[location(b,'RemainingDraw::PickupArts'):location(b,'RemainingDraw::PickupArts')+80]
 assert table.count(84)==1 and table[2]==84
 changed,recipe=plan(R,BASE)
 old=(R/'src/remaining_weapons.s').read_bytes();nl=b'\r\n'if b'\r\n'in old else b'\n'
 token=nl.join([b'  sta R7',b'  sta AvDrawDirection',b'Draw:',b'  lda AvDrawArt'])
 assert old.count(token)==1
 replacement=nl.join([b'  sta R7',b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'  jmp SamusFixedMissileHud',b'.else',b'  sta AvDrawDirection',b'.endif',b'Draw:',b'  lda AvDrawArt'])
 source=old.replace(token,replacement)
 token=nl.join([b'  jsr ArtPointer',b'  jcc Next',b'  lda #0',b'  sta R3',b'  farcall MetaspriteRenderLoop'])
 assert source.count(token)==1
 source=source.replace(token,token.replace(nl+b'  lda #0',nl+b'FixedHudRender:'+nl+b'  lda #0'))
 changed['src/remaining_weapons.s']=source;changed['src/samus_fixed_hud.s']=HELPER.encode()
 epold=(R/'src/entrypoint.s').read_bytes();nl=b'\r\n'if b'\r\n'in epold else b'\n'
 changed['src/entrypoint.s']=epold+nl+nl.join([b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'.include "samus_fixed_hud.s"',b'.endif',b''])
 paths={}
 for name,data in changed.items():
  p=B/(P+'_'+Path(name).name);assert not p.exists();p.write_bytes(data);paths[name]=p
 ep=paths['src/entrypoint.s'];text=ep.read_bytes()
 for name in ['remaining_weapons.s','samus_fixed_hud.s']:
  text=text.replace(b'.include "'+name.encode()+b'"',b'.include "'+paths['src/'+name].name.encode()+b'"')
 text=text.replace(b'.incbin "chr/characters/packed-mmc5-expanded.chr"',b'.incbin "build/'+paths['chr/characters/packed-mmc5-expanded.chr'].name.encode()+b'"');ep.write_bytes(text)
 c=B/(P+'_main.c');assert not c.exists();c.write_bytes((R/'src/main.c').read_bytes())
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini')
 defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 out=B/(P+'.nes');assert not out.exists()
 cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(R/'smb1base-mmc5-expanded.cfg'),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(B),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
 for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
 cmd+=[str(c),str(ep)]
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stdout+z.stderr
 sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare;prepare(R,out)
 new=scoped_load(out);after=new['raw'];basechr=16+128*8192
 hook=location(b,'RemainingDraw::Draw')-3;assert raw[hook:hook+3]==bytes([0x8d,address(b,'AvDrawDirection')&255,address(b,'AvDrawDirection')>>8])
 size=address(new,'SamusFixedHudRecord')+9-address(new,'SamusFixedMissileHud')
 expected=bytearray(raw);expected[hook:hook+3]=bytes([0x4c,0xae,0xbf]);expected[at:at+size]=after[at:at+size]
 expected[basechr+20*1024+192:basechr+20*1024+256]=changed['chr/mmc5/sprites_enemies.chr'][3072+192:3072+256]
 assert after==expected,'Only HUD hook, allocated tail and authenticated64B asset region may change'
 assert all(new['syms'].get(n,{}).get('val')==s.get('val')and new['syms'].get(n,{}).get('seg')==s.get('seg')for n,s in b['syms'].items()),'Old symbol moved'
 _,idem=plan(R,out,{n:changed[n]for n in ['chr/mmc5/sprites_enemies.chr','chr/characters/packed-mmc5-expanded.chr']});assert idem['idempotent']and idem['changed_asset_bytes']==0
 patch=[]
 for name,blob in changed.items():
  if not name.endswith('.chr'):patch+=difflib.unified_diff((R/name).read_bytes().decode().splitlines(True)if(R/name).exists()else[],blob.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)
 pp=B/(P+'.patch');pp.write_bytes(''.join(patch).encode())
 receipt=dict(source_only=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=sha(out),ROM=str(out),hook_PC=hex(address(b,'RemainingDraw::Draw')-3),helper_PC='BFAE',helper_and_record_bytes=size,record_A_PC=hex(address(new,'SamusFixedHudRecord')),record_C_alias=hex(address(new,'SamusFixedHudRecord')+8192),PRG_changed_bytes=sum(x!=y for x,y in zip(raw[:basechr],after[:basechr])),CHR_changed_bytes=sum(x!=y for x,y in zip(raw[basechr:],after[basechr:])),only_PRG_bank=61,only_CHR_page=20,all_old_symbols_exact=len(b['syms']),new_RAM=0,all_runtime_NMI_and_audio_bytes_exact=True,recipe=recipe,idempotence=idem,source_overlay={n:dict(path=str(p),sha256=sha(p))for n,p in paths.items()},command=cmd,bindings={str(p):sha(p)for p in [Path(__file__),R/'tools/reference/patch_samus_fixed_hud.py',BASE,BASE.with_suffix('.dbg'),BASE.with_suffix('.lbl'),R/'src/remaining_weapons.s',R/'src/entrypoint.s',R/'smb1base-mmc5-expanded.cfg',R/'build_options.ini',pp]})
 p=B/(P+'_build.json');p.write_text(json.dumps(receipt,indent=2)+'\n',newline='\n');print(json.dumps(dict(ROM_sha256=sha(out),proof_sha256=sha(p),helper_bytes=size)))
if __name__=='__main__':main()
