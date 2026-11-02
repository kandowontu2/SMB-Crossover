"""Measure source-equivalent Sh transport factoring; no resident grant/patch."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from private_build_outputs_v1 import validate
O=L.O


def main():
 b=scoped_load(L.BASE);raw=b['raw'];base=16+65*8192;current=raw[base+0xaf7:base+0xbd4];prior=(R/'build/shinobi-bbox-design-1101-v29/resident-design.bin').read_bytes()[0x2f7:0x3d4];assert current==prior and len(current)==221
 src=R/'tools/reference/shinobi_resident_dispatch_1101_v1.inc';s=src.read_text();s=s[s.index('ShDispatch:\n'):]
 blocks=list(re.finditer(r' \.repeat 5,I\n.*? \.endrepeat',s,re.S));assert len(blocks)==2
 for match,replace in reversed(list(zip(blocks,[''' ldx #0
PrShSave:
 ldy ShSavedSmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne PrShSave''',''' ldx #4
PrShRestore:
 pla
 ldy ShSavedSmcOffsets,x
 sta $0100,y
 dex
 bpl PrShRestore''']))):s=s[:match.start()]+replace+s[match.end():]
 start=s.index(' ldx #3\nShDispatchAuthBank:');end=s.index(' lda FarcallJmpTarget_SMC+1\n',start)
 s=s[:start]+' jsr ShCheckCode\n jcc ShDispatchNo\n'+s[end:]
 needle=' ; Header loop ends with C2 mapped. Restore original live arguments.\n';assert needle in s;s=s.replace(needle,' lda #2\n sta CurrentBankC\n sta $5116\n'+needle)
 start=s.index(' tsx\n lda $0101,x\n');end=s.index(' jmp ShDispatchRestore\n',start)
 s=s[:start]+''' tsx
 ldy #4
PrShResult:
 lda $0101,x
 sta $010b,x
 inx
 dey
 bne PrShResult
 txs
'''+s[end:]
 names=['SelectedCharacter','CurrentBankC','NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC','FarCallCommon'];defs={n:address(b,n)for n in names}
 # Recover the private table symbol from actual assembled ShCookie and the
 # source-declared adjacent five-byte SMC/nine-byte low/nine-byte high tables.
 # AA73 was an incorrect hand binding in the first insufficient measurement.
 loader=R/'tools/reference/shinobi_resident_loader_1101_v1.inc';ld=loader.read_text();tail=ld[ld.index('ShSavedSmcOffsets:\n'):]
 m=re.fullmatch(r'ShSavedSmcOffsets:\n \.byte ([^\n]+)\nShCarrierLow:\.byte ([^\n]+)\nShCarrierUpper:\.byte ([^\n]+)\nShCookie:\.incbin "shinobi-cookie.bin"\nShResidentEnd:\n',tail);assert m
 counts=[len(z.split(','))for z in m.groups()];assert counts==[5,9,9]
 origlabels=R/'build/shinobi-bbox-design-1101-v29/resident-design.lbl';orig=L.P.T.labels(origlabels);saved=orig['ShCookie']-sum(counts)
 defs.update(ShCacheServices=0xa000,ShCheckCode=orig['ShCheckCode'],ShCookie=orig['ShCookie'],ShSavedSmcOffsets=saved,ShServiceVeneers=orig['ShServiceVeneers'])
 expected=bytes((defs[n]+1)&255 for n in ['NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC'])+bytes([(defs['FarcallJmpTarget_SMC']+2)&255,(defs['SafereturnA_SMC']+1)&255])
 assert saved==0xaa61 and raw[base+saved-0xa000:base+saved-0xa000+5]==expected
 assert current==prior and raw[base+orig['ShCookie']-0xa000:base+orig['ShCookie']-0xa000+3]==bytes([167,36,1])
 # Restore original Y explicitly: old inline auth never changed Y; the reused
 # helper also preserves Y, but the result/transport ABI is kept explicit.
 assert ' lda $0108,x\n tax\n plp' in s;s=s.replace(' lda $0108,x\n tax\n plp',' lda $0108,x\n pha\n lda $0107,x\n tay\n pla\n tax\n plp')
 text='.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${v:04x}\n'for n,v in defs.items())+'.segment "FACTOR"\n.export ShDispatch,ShDispatchEnd\n'+s
 # Relax only named local long branches; no instruction semantics changed.
 sites=[]
 def mark(m):
  name=f'PrShBranch{len(sites)}';sites.append((name,m[1],m[2]));return name+':\n '+m[0].strip()
 text=re.sub(r'(?m)^ j(eq|ne|cc|cs|mi|pl|vc|vs) (\w+)$',mark,text)
 text+='\n.export '+','.join([*[n for n,_,_ in sites],*[t for _,_,t in sites]])+'\n';cfg=O/'dispatch-factor-v21.cfg';cfg.write_text('MEMORY{M:start=$aaf7,size=$dd,file=%O;}SEGMENTS{FACTOR:load=M,type=ro;}');cc=R/'tools/Windows/cc65/bin'
 for _ in range(4):
  asm=O/'dispatch-factor-v21.s';asm.write_text(text)
  for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/'dispatch-factor-v21.o'],[cc/'ld65.exe','-C',cfg,O/'dispatch-factor-v21.o','-o',O/'dispatch-factor-v21.bin','-Ln',O/'dispatch-factor-v21.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
  lab=L.P.T.labels(O/'dispatch-factor-v21.lbl');changes=[]
  for label,cond,target in sites:
   old=label+':\n j'+cond+' '+target
   if old in text and-128<=lab[target]-lab[label]-2<=127:changes.append((old,label+':\n b'+cond+' '+target))
  if not changes:break
  for a,z in changes:text=text.replace(a,z)
 blob=(O/'dispatch-factor-v21.bin').read_bytes();q=dict(measured=True,qualified=False,ROM_written=False,shared_sources_written=False,base_ROM_SHA256=L.PIN,original_half_open=[0xaaf7,0xabd4],original_bytes=221,new_half_open=[0xaaf7,0xaaf7+len(blob)],new_bytes=len(blob),source_funding_if_full_ABI_proof_passes=221-len(blob),source_original_exact_on1966=True,public_37_veneer_addresses_unchanged=True,other_resident_addresses_unchanged=True,remaining=['Actual all-row raw36 and allforeign register/state/SMC/map differentials.','Complete two-header poison and IRQ/lag-NMI instruction cuts.','No freed byte is granted or allocated until these checks and root review.','Even this factor is insufficient alone for120B added owner manager plus Prince public routing.'],bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),src,R/'build/shinobi-bbox-design-1101-v29/resident-design.bin',O/'dispatch-factor-v21.bin',L.BASE]})
 q['source_derived_private_symbol']=dict(name='ShSavedSmcOffsets',value=saved,source_adjacent_table_bytes=counts,assembled_ShCookie=orig['ShCookie'],actual_current_table_hex=expected.hex(),derivation='Actual original compiled ShCookie minus three contiguous source-declared tables; exact five native SMC offsets compared against current ROM.')
 for p in [loader,origlabels]:q['bindings'][str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 (O/'dispatch-factor-measurement-v21.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
