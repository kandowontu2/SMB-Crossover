"""Exact613b foreign public ABI and three-owner complete-header rejection."""
from pathlib import Path
import hashlib,inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_successor_manifest_1102_v26 as M
import check_prince_shared_frame_1102_v22 as F
import check_prince_successor_services_1102_v27 as S
import check_hogan_current_bounded_v1 as N
O=M.O


def main():
 old,new,_,_=M.bundle();ss=F.seeds([old,new])
 for m in ss:
  m.ram[3][0x1b7a]=0x60 # Actualv9 private retire typed boundary; same both.
  for name in ['writes','ram_writes','ppu_log','blocked']:setattr(m,name,[])
 text=inspect.getsource(F.call);lines=text.splitlines()
 for i,line in enumerate(lines):
  if line.lstrip().startswith('cookie='):
   lines[i]=" cookie_at=16+65*8192+(0x1003 if char==39 else 0xff3)if family=='Ex'else 16+65*8192+0xa78;cookie=m.bundle['raw'][cookie_at:cookie_at+16]"
 env=dict(F.__dict__);exec(compile('\n'.join(lines)+'\n',str(Path(__file__)),'exec'),env);call=env['call'];cases=typed=0
 for family in ['Sh','Ex']:
  for char in range(40):
   if char==38:continue # New owner checked with actual source, not old ABI.
   for row in range(38 if family=='Ex'else 37):
    for flags in [0x30,0xf1]:
     pair=[call(seed,char,row,family,flags,args=((row*7+char)&255,(row*3+char)&255,(row*11+char)&255))for seed in ss];F.compare(*pair,(family,char,row,flags));cases+=1;typed+=int(row==37)
 print('Exact613b foreign public-row ABI passed.',flush=True)
 poison=0
 for family,char in [('Sh',36),('Ex',37),('Ex',39)]:
  for bank in [2,3]:
   for byte in range(16):
    pair=[call(seed,char,0,family,poison=(bank,byte))for seed in ss];F.compare(*pair,('header',family,char,bank,byte));assert not pair[1][1][3]&1;poison+=1
 # Prince headers are checked before the service tag write/private leaf.
 # A mismatch must preserve every private byte, including stale old tag.
 lab=F.L.P.T.labels(O/'owner-third-v23.lbl');at=16+65*8192+lab['PrCookie']-0xa000;cookie=new['raw'][at:at+16];seed=N.fresh(new)
 for k in [2,3]:seed.ram[k][:]=bytes([0x73])*8192;seed.ram[k][0x1fe0:0x1ff0]=cookie
 N.put(seed,SelectedCharacter=38,NmiDisable=1)
 for bank in [2,3]:
  for byte in range(16):
   n=N.fork(seed);n.ram[bank][0x1fe0+byte]^=1;state=[bytes(x)for x in n.ram];out=S.invoke(n,193,0xb08c);assert not out['regs'][3]&1 and state==[bytes(x)for x in n.ram];poison+=1
 # The private carry-only helper's actual finite selector is evaluated over
 # all256 raw bytes. Only the new38 identity adds a successful cookie domain.
 helpers=0
 for char in range(256):
  for owner in [37,38,39]:
   n=N.fork(seed);N.put(n,SelectedCharacter=char)
   off=0x1003 if owner==39 else 0xff3 if owner==37 else lab['PrCookie']-0xa000;cook=new['raw'][16+65*8192+off:16+65*8192+off+16]
   for k in [2,3]:n.ram[k][0x1fe0:0x1ff0]=cook
   state=[bytes(x)for x in n.ram];out=S.invoke(n,193,0xaef3);assert bool(out['regs'][3]&1)==(char==owner)and state==[bytes(x)for x in n.ram];helpers+=1
 q=dict(passed=True,proposal_only=True,ROM_written=False,grant=False,base_SHA256=M.A.PIN,successor_memory_SHA256=M.sha(new['raw']),actual_foreign_fixed_public_row_ABI_cases=cases,genuine_typed_contact37_cases=typed,complete_header_byte_rejections=poison,raw256_three_cookie_selector_cases=helpers,all_existing_AXYP_SP_full_SMC_all_ZP_native_private_mapper_state_exact=True,new_Prince_bad_headers_reject_before_tag_or_state_write=True,v9_BB_retire_typed_boundary=0xbb7a,existing_SourceFrame_CPU='shared-frame-CPU-v22.json',new_real_source_cold_clock_tag_Fresh_ISR='successor-services-CPU-v27.json',scope='Exact current613b old/new all public Sh/Ex/Bub foreign rows/raw0..39 excluding new38, typed private callee boundaries and original UI forwarding. All128 own header-byte corruptions and actual bounded selector over raw0..255. No new gameplay/menu/native emulator claim.',fixture_adaptation_SHA256=hashlib.sha256(('\n'.join(lines)+'\n').encode()).hexdigest(),bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),R/'tools/audit/check_prince_shared_frame_1102_v22.py',O/'successor-proposal-v26.json',O/'successor-services-CPU-v27.json',O/'owner-third-v23.bin',O/'public-selector-v24.bin',M.A.BASE]})
 (O/'successor-foreign-CPU-v28.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
