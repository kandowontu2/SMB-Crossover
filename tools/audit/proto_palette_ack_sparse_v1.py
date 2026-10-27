"""One sparse private Proto palette-cache candidate on exact current8487."""
from pathlib import Path
import configparser,difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build';BASE=B/'bass_corner_current.nes';EXPECTED='8487c439ded9bc6274e1dc8f8e051494fa96ee518553d9c2f382eccf2e71d0e6'
sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HELPER='; Existing cache acknowledgement after a real complete normal Proto palette.\n; No NMI, new RAM or physical palette mutation; all caller AXYP preserved.\n.pushseg\n.segment "PROTO_PALETTE_ACK"\n.proc ProtoFixAndAcknowledgePalette\n jsr ProtoFixQueuedPalette\n php\n pha\n txa\n pha\n tya\n pha\n lda SelectedCharacter\n cmp #CHARACTER_MEGAMAN\n bne Restore\n lda ProtoVariant\n beq Restore\n lda InvSelected+CHARACTER_MEGAMAN\n bne Restore\n lda GuestPowerupActive\n ora StarInvincibleTimer\n ora MmChargeFrames\n bne Restore\n lda PlayerStatus\n cmp #2\n bcs Restore\n ldx VRAM_Buffer1_Offset\n ; Legacy GetColors appended exactly6(face)+6(weapon)+7(body) bytes.\n ; An unsigned19-byte append cannot wrap into this safe19..83 range.\n cpx #19\n bcc Restore\n cpx #.sizeof(VRAM_Buffer1)\n bcs Restore\n lda VRAM_Buffer1,x\n bne Restore\n ; The successfully queued tail has the real4-color body command.\n lda VRAM_Buffer1-7,x\n cmp #$3f\n bne Restore\n lda VRAM_Buffer1-6,x\n cmp #$10\n bne Restore\n lda VRAM_Buffer1-5,x\n cmp #4\n bne Restore\n lda VRAM_Buffer1-3,x\n cmp #$0f\n bne Restore\n lda VRAM_Buffer1-2,x\n cmp #$16\n bne Restore\n lda VRAM_Buffer1-1,x\n cmp #$10\n bne Restore\n lda #1\n sta SsLastPalette\nRestore:\n pla\n tay\n pla\n tax\n pla\n plp\n rts\n.endproc\n.assert *-ProtoFixAndAcknowledgePalette<=192,error,"Explicit bank66 BE40..BEFF bound"\n.popseg\n'
def main():
 assert sha(BASE)==EXPECTED
 b=scoped_load(BASE);at=16+66*8192+0x1e40
 for p in [BASE,B/'mm_body_reserve.nes']:
  q=scoped_load(p);assert q['raw'][at:16+67*8192]==b'\xff'*(0x2000-0x1e40)
  for g in q['segs'].values():
   if'ooffs'in g:
    x,n=int(g['ooffs'],0),int(g['size'],0);assert not(n and x<16+67*8192 and at<x+n)
 changed={}
 old=(R/'src/x5_palette.s').read_bytes();token=b'  farcall ProtoFixQueuedPalette,jmp';assert old.count(token)==1
 changed['src/x5_palette.s']=old.replace(token,b'  farcall ProtoFixAndAcknowledgePalette,jmp')
 changed['src/proto_palette_ack.s']=HELPER.encode()
 old=(R/'src/entrypoint.s').read_bytes();nl=b'\r\n'if b'\r\n'in old else b'\n';changed['src/entrypoint.s']=old+nl+nl.join([b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'.include "proto_palette_ack.s"',b'.endif',b''])
 old=(R/'smb1base-mmc5-expanded.cfg').read_bytes();nl=b'\r\n'if b'\r\n'in old else b'\n';i=old.index(nl+b'}'+nl+b'SYMBOLS');changed['smb1base-mmc5-expanded.cfg']=old[:i]+nl+b'    PROTO_PALETTE_ACK: load=X5_NEW_42_TAIL,type=ro,start=$be40;'+old[i:]
 paths={}
 for name,blob in changed.items():
  p=B/('proto_palette_ack_'+Path(name).name);p.write_bytes(blob);paths[name]=p
 # Only entrypoint and the changed direct child are shadowed; all other
 # existing source/assets are read in place, not copied into a new tree.
 ep=paths['src/entrypoint.s'];v=ep.read_bytes();v=v.replace(b'.include "x5_palette.s"',b'.include "'+paths['src/x5_palette.s'].name.encode()+b'"').replace(b'.include "proto_palette_ack.s"',b'.include "'+paths['src/proto_palette_ack.s'].name.encode()+b'"');ep.write_bytes(v)
 c=B/'proto_palette_ack_main.c';c.write_bytes((R/'src/main.c').read_bytes())
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 out=B/'proto_palette_ack.nes';cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(paths['smb1base-mmc5-expanded.cfg']),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(B),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
 for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
 cmd +=[str(c),str(ep)];z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stdout+z.stderr
 sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare;prepare(R,out)
 new=out.read_bytes();diff={bank:sum(x!=y for x,y in zip(b['raw'][16+bank*8192:16+(bank+1)*8192],new[16+bank*8192:16+(bank+1)*8192]))for bank in range(128)};diff={k:v for k,v in diff.items()if v}
 patch=[]
 for name,blob in changed.items():patch+=difflib.unified_diff((R/name).read_text().splitlines(True)if(R/name).exists()else[],blob.decode().splitlines(True),fromfile='current8487/'+name,tofile='private/'+name)
 pp=B/'proto_palette_ack.patch';pp.write_text(''.join(patch),newline='\n')
 receipt=dict(source_only=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=sha(out),sparse_files={n:dict(path=str(p),sha256=sha(p))for n,p in paths.items()},changed_banks=diff,all_header_CHR_exact=b['raw'][:16]==new[:16]and b['raw'][16+128*8192:]==new[16+128*8192:],allocation='Decimal66/$42 BE40..BEFF max192B, actual8487andf1dd tailFF/unallocated verified',command=cmd,patch_sha256=sha(pp),limits='Native pending; CPU equivalence/queue controls next. No installed/default/source writes or source/runtime tree copies.')
 (B/'proto_palette_ack_build.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n');print(json.dumps(receipt))
if __name__=='__main__':main()
