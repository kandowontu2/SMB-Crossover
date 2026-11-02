"""Fix source-owned direct draw reservation inside existing cached draw span."""
import hashlib,json,re,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
R=S.R;BASE=R/'build/shinobi-contact-visible-1101-v23';O=R/'build/shinobi-draw-reservation-1101-v26';PAGES=[506,507,508,509,510,513,515]
def main():
 O.mkdir(exist_ok=True);assert S.sha(BASE/'candidate.nes')=='faef4740e28d40e92aa2be7b1c72c972d5941135aff53e9e800bc32d3b332a66'
 b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw']);lab=S.labels(R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 src=(R/'tools/reference/shinobi_native_boundary_1101_v1.inc').read_text()
 old=src[src.index('ShHostDraw:'):src.index('ShRenderMasks:.byte')]
 restore=''.join(' pla\n sta R7-'+str(i)+'\n'for i in range(8))+' pla\n tay\n pla\n tax\n pla\n plp\n'
 save=' php\n pha\n txa\n pha\n tya\n pha\n'+''.join(' lda R0+'+str(i)+'\n pha\n'for i in range(8))
 old=old.replace(' ShSave\n',save).replace(' ShRestore\n',restore)
 new=(R/'tools/reference/shinobi_draw_reservation_1101_v26.inc').read_text()
 constants={n:address(b,n)for n in b['syms']if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',n)};constants.update(lab)
 constants.update({n:int(v,16)for n,v in re.findall(r'^(\w+)=\$([0-9a-fA-F]+)',src,re.M)})
 local=set(re.findall(r'^(\w+):',old+new,re.M));words=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',old+new))
 defs=''.join(f'{n}=${constants[n]:04x}\n'for n in sorted(words&constants.keys()-local))
 start=lab['ShHostDraw'];end=lab['ShRenderMasks'];size=end-start
 (O/'draw.cfg').write_text(f'MEMORY {{ B:start=${start:04x},size={size},file=%O; }} SEGMENTS {{ DRAW:load=B,type=ro; }}')
 cc=R/'tools/Windows/cc65/bin'
 def asm(name,body):
  (O/(name+'.s')).write_text('.setcpu "6502"\n'+defs+'.segment "DRAW"\n.export ShHostDraw\n'+body)
  for cmd in [[cc/'ca65.exe',O/(name+'.s'),'-o',O/(name+'.o')],[cc/'ld65.exe','-C',O/'draw.cfg',O/(name+'.o'),'-o',O/(name+'.bin'),'-Ln',O/(name+'.lbl')]]:
   z=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert z.returncode==0,z.stderr
  return (O/(name+'.bin')).read_bytes()
 original=asm('original',old);patched=asm('draw',new)
 def offset(pc):
  i=pc-0xa000;return 16+1048576+PAGES[i//1024]*1024+i%1024
 assert len(original)==size and bytes(raw[offset(pc)]for pc in range(start,end))==original
 assert len(patched)<=size
 for i,v in enumerate(patched+bytes([234])*(size-len(patched))):raw[offset(start+i)]=v
 def page(p):return raw[16+1048576+p*1024:16+1048576+(p+1)*1024]
 cookie=bytes([167,36,1])+hashlib.sha256(b''.join(page(p)for p in PAGES+[516,517,503,504,505,517])).digest()[:13]
 at=16+65*8192+0xa78;assert raw[at:at+16]==(BASE/'shinobi-cookie.bin').read_bytes();raw[at:at+16]=cookie
 (O/'candidate.nes').write_bytes(raw);(O/'shinobi-cookie.bin').write_bytes(cookie)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 (O/'combat.lbl').write_bytes((BASE/'combat.lbl').read_bytes())
 q=dict(ROM_sha256=S.sha(O/'candidate.nes'),base_sha256=S.sha(BASE/'candidate.nes'),start=start,span_bytes=size,used_bytes=len(patched),original_source_bytes_exact=True,installed=False)
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
