"""One sparse private 2082 projectile-HUD alternative. No native launch."""
from pathlib import Path
import configparser,difflib,hashlib,json,subprocess,sys

R=Path(__file__).resolve().parents[2];B=R/'build'
BASE=B/'smb-crossover-mmc5-expanded.nes'
EXPECTED='2082c19a7364920f828e97f70040d37f1f7059bde1ea136b5c2c4532324abf36'
sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HELPER='''; HUD-only authentic missile projectile; original world capsule stays.
; Full RemainingDraw owns flag/scratch liveness, not a new public ABI.
.pushseg
.segment "SPECIAL_ROSTER"
.proc SamusMissileHudArt
 jsr RemainingDraw::PickupArt
 cmp #AV_ART_SAMUSPICKUP7
 bne Ready
 lda #AV_ART_SAMUSSHOT7
Ready:
 ora #0                         ; Preserve the genuine zero-art rejection.
 rts
.endproc
.assert SamusMissileHudArt=$bfae,error,"Verified existing SPECIAL_ROSTER tail"
.assert *-SamusMissileHudArt=12,error,"Exact twelve-byte helper"
.popseg
'''

def main():
 assert sha(BASE)==EXPECTED
 b=scoped_load(BASE);raw=b['raw'];at=16+61*8192+0x1fae
 assert raw[at:at+12]==bytes([255])*12
 assert address(b,'RemainingDraw::PickupArt')==0xba9c
 assert address(b,'AV_ART_SAMUSPICKUP7')==84 and address(b,'AV_ART_SAMUSSHOT7')==44
 for seg in b['segs'].values():
  if 'ooffs'in seg:
   pos,n=int(seg['ooffs'],0),int(seg['size'],0)
   assert not(n and pos<at+12 and at<pos+n),'Helper fill is allocated'
 changed={}
 old=(R/'src/remaining_weapons.s').read_bytes();nl=b'\r\n'if b'\r\n'in old else b'\n'
 token=nl.join([b'  jsr PickupArt',b'  jeq Next',b'  sta AvDrawArt',b'  lda #192'])
 assert old.count(token)==1
 replacement=nl.join([b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'  jsr SamusMissileHudArt',b'.else',b'  jsr PickupArt',b'.endif',*token.split(nl)[1:]])
 changed['src/remaining_weapons.s']=old.replace(token,replacement)
 changed['src/samus_projectile_hud.s']=HELPER.encode()
 old=(R/'src/entrypoint.s').read_bytes();nl=b'\r\n'if b'\r\n'in old else b'\n'
 changed['src/entrypoint.s']=old+nl+nl.join([b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'.include "samus_projectile_hud.s"',b'.endif',b''])
 paths={}
 for name,blob in changed.items():
  p=B/('samus_projectile_hud_'+Path(name).name);assert not p.exists();p.write_bytes(blob);paths[name]=p
 ep=paths['src/entrypoint.s'];text=ep.read_bytes()
 for name in ['remaining_weapons.s','samus_projectile_hud.s']:
  text=text.replace(b'.include "'+name.encode()+b'"',b'.include "'+paths['src/'+name].name.encode()+b'"')
 ep.write_bytes(text)
 c=B/'samus_projectile_hud_main.c';assert not c.exists();c.write_bytes((R/'src/main.c').read_bytes())
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini')
 defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 out=B/'samus_projectile_hud.nes';assert not out.exists()
 cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(R/'smb1base-mmc5-expanded.cfg'),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(B),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
 for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
 cmd +=[str(c),str(ep)]
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stdout+z.stderr
 sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare;prepare(R,out)
 new=scoped_load(out);after=new['raw'];pickup=address(b,'RemainingDraw::PickupArt')
 expected=bytearray(raw);expected[at:at+12]=bytes([0x20,pickup&255,pickup>>8,0xc9,84,0xd0,2,0xa9,44,0x09,0,0x60])
 call=16+61*8192+(0xb8e1&8191);assert raw[call:call+3]==bytes([0x20,pickup&255,pickup>>8]);expected[call+1:call+3]=bytes([0xae,0xbf])
 assert after==expected,'Only exact approved helper and HUD call may change'
 assert all(new['syms'].get(n,{}).get('val')==s.get('val')and new['syms'].get(n,{}).get('seg')==s.get('seg')for n,s in b['syms'].items())
 assert sha(BASE)==EXPECTED,'Current baseline changed during build'
 patch=[]
 for name,blob in changed.items():
  before=(R/name).read_bytes().decode().splitlines(True)if(R/name).exists()else[]
  patch+=difflib.unified_diff(before,blob.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)
 pp=B/'samus_projectile_hud.patch';pp.write_bytes(''.join(patch).encode())
 proof=dict(source_only=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=sha(out),ROM=str(out),changed_PRG_bytes=14,changed_PRG_bank=61,helper_PC='BFAE',helper_bytes=12,HUD_JSR_PC='B8E1',all_old_symbol_addresses_and_segments_exact=len(b['syms']),header_CHR_and_all_art_records_exact=True,new_RAM=0,source_overlay={n:dict(path=str(p),sha256=sha(p))for n,p in paths.items()},patch_sha256=sha(pp),command=cmd,limits='Private alternative, not b403. Two-part original missile projectile pal2/family6/page215; world capsule record/art/CHR unchanged. Actual family arbitration/per-update world admission differs. Near-full OAM can newly admit this smaller HUD and cost more. Foreign selected HUD lookup adds19cycles. No native/cadence/visibility/IRQ verdict yet.')
 target=B/'samus_projectile_hud_build.json';target.write_text(json.dumps(proof,indent=2)+'\n',newline='\n');print(json.dumps(proof))

if __name__=='__main__':main()
