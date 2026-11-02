"""Patch only the granted cached combat span; retain latest camera and cookie."""
import hashlib,json,re,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=S.R;BASE=R/'build/shinobi-camera-1101-v20';O=R/'build/shinobi-contact-visible-1101-v23'
PAGES=[506,507,508,509,510,513,515]
def main():
 O.mkdir(exist_ok=True)
 assert S.sha(BASE/'candidate.nes')=='fe4e9a6d5aef0c2e3848a501f487e7791cd75b9db5cf5297ebad395162560ad9'
 b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw']);lab=S.labels(R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 old=(R/'tools/reference/shinobi_native_combat_1101_v1.inc').read_text()
 lo=old.index(' lda Enemy_Y_Position,x\n sec\n ldx ShContactSlot')
 hi=old.index(' lda ShState+$0008\n',lo)
 new=old[:lo]+(R/'tools/reference/shinobi_contact_visible_1101_v23.inc').read_text()+old[hi:]
 # Save8 temporary bytes at C203..C20A; this aliases result/world scratch.
 # Recompute world for each enemy and clear result after restoring both boxes.
 world_start=new.index(' lda ShState+$0379,x\n')
 world_end=new.index(' lda #5\n sta ShContactEnemy\n',world_start)
 world=new[world_start:world_end];new=new[:world_start]+new[world_end:]
 new=new.replace('ShShotEnemy:\n ldx ShContactEnemy','ShShotEnemy:\n ldx ShContactSlot\n'+world+' ldx ShContactEnemy')
 new=new.replace(' php\n ldy #3\nShRestoreContactBox:',' php\n ldy #7\nShRestoreContactBox:')
 new=new.replace(' plp\n bcc ShShotNext',' plp\n lda #0\n sta ShContactResult\n bcc ShShotNext')
 new=new.replace(' sta ShContactResult\n jmp ShShotDone',' sta ShContactResult\n bne ShShotDone ; A=1, STA retains Z=0')
 start,end=lab['ShSourceBounds'],lab['ShNativeCombatEnd'];size=end-start
 constants={n:address(b,n)for n in b['syms']if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',n)}
 constants.update(lab);constants.update(ShState=0xc000,ShScratch=3)
 constants['Bank_GetEnemyBoundBox']=128|((location(b,'GetEnemyBoundBox')-16)//8192)
 local=set(re.findall(r'^(\w+)[=:]',old,re.M));local|={'Bank'}
 words=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',old+new))
 defs=''.join(f'{n}=${constants[n]:04x}\n'for n in sorted(words&constants.keys()-local))
 cfg=f'MEMORY {{ B:start=${start:04x},size={size},file=%O; }} SEGMENTS {{ SHINOBI_KERNEL:load=B,type=ro; }}'
 (O/'combat.cfg').write_text(cfg);cc=R/'tools/Windows/cc65/bin'
 def assemble(name,body):
  (O/(name+'.s')).write_text('.setcpu "6502"\n.macpack longbranch\n.export ShSourceBounds,ShNativeShotContact,ShNativeCombatEnd\n'+defs+body)
  for cmd in [[cc/'ca65.exe',O/(name+'.s'),'-o',O/(name+'.o')],[cc/'ld65.exe','-C',O/'combat.cfg',O/(name+'.o'),'-o',O/(name+'.bin'),'-Ln',O/(name+'.lbl')]]:
   z=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert z.returncode==0,z.stderr
  return (O/(name+'.bin')).read_bytes()
 original=assemble('original',old);patched=assemble('combat',new)
 assert len(original)==size and len(patched)<=size
 def offset(pc):
  i=pc-0xa000;return 16+1048576+PAGES[i//1024]*1024+i%1024
 assert bytes(raw[offset(pc)]for pc in range(start,end))==original
 for i,v in enumerate(patched+bytes([234])*(size-len(patched))):raw[offset(start+i)]=v
 def page(p):return raw[16+1048576+p*1024:16+1048576+(p+1)*1024]
 cookie=bytes([167,36,1])+hashlib.sha256(b''.join(page(p)for p in PAGES+[516,517,503,504,505,517])).digest()[:13]
 at=16+65*8192+0xa78;assert raw[at:at+16]==(BASE/'shinobi-cookie.bin').read_bytes();raw[at:at+16]=cookie
 (O/'candidate.nes').write_bytes(raw);(O/'shinobi-cookie.bin').write_bytes(cookie)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 q=dict(ROM_sha256=S.sha(O/'candidate.nes'),base_sha256=S.sha(BASE/'candidate.nes'),combat_start=start,span_bytes=size,used_bytes=len(patched),original_source_bytes_exact=True,installed=False)
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
