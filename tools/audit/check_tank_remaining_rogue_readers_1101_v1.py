"""Run the current Rogue ROM reader across pages sharing pending Tank banks."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
from check_tank_terminal_leaves_1101_v1 import O,P,PIN
def main():
 b=scoped_load(P);raw=b['raw'];assert hashlib.sha256(raw).hexdigest()==PIN
 gaps={115:(0x195,0x200),68:(0x1ecc,0x1f20),82:(0x1fc2,0x2000),13:(0x1fc3,0x2000),62:(0x1fc4,0x2000),66:(0x1957,0x19a8),73:(0x1fbe,0x2000),58:(0x1faa,0x2000),12:(0x1fad,0x2000),89:(0x1fb0,0x2000),28:(0x1fb0,0x2000),78:(0xf96,0x1000)}
 m=M.fresh(b);driverbank=128|((location(b,'RdaReadRomValue')-16)//8192)
 value=address(b,'RdaReadValue');pairs=[];calls=0
 for mode,count,banks,highs in [('lower',192,'RdaLowerBankTable','RdaLowerHighTable'),('upper',32,'RdaUpperRawBankTable','RdaUpperRawHighTable')]:
  bo=location(b,banks);ho=location(b,highs)
  for index,(tag,hi) in enumerate(zip(raw[bo:bo+count],raw[ho:ho+count])):
   bank=tag&127;physical=(hi-0xa0)*256
   assert 0<=physical<8192
   if bank in gaps:
    start,end=gaps[bank];assert physical+256<=start or physical>=end,(mode,index,bank)
    pairs.append(dict(mode=mode,index=index,bank=bank,half_open=[physical,physical+256]))
   for offset in range(256) if bank in gaps else [0,255]:
    m.raw_page(1,190);m.raw_page(2,driverbank);M.put(m,CurrentBank=190,CurrentBankC=driverbank)
    m[0xe8]=offset;m[0xe9]=(0x80+index%32) if mode=='lower' else 0xa0+index
    m[0x23]=index//32 if mode=='lower' else 0
    c=NesMPU(memory=m,pc=address(b,'RdaReadRomValue'));c.sp=224;c.stPushWord(0x5aff)
    for _ in range(1000):
     if c.pc==0x5b00:break
     assert m[c.pc]!=0;c.step()
    else:raise AssertionError('Reader failed to return')
    assert m[value]==raw[16+bank*8192+physical+offset]
    assert m.rawtags[1]==190 and M.get(m,'CurrentBank')==190 and c.sp==224
    calls+=1
 result=dict(passed=True,ROM_sha256=PIN,typed_page_rows=224,native_reader_calls=calls,shared_bank_pages=pairs,proposed_gaps=gaps,formal_grant=False,scope='Rogue reader only. Full 256-byte domains for rows sharing the twelve pending banks, edge offsets for other rows. Other graphics/music/code consumers remain separate.',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (O/'remaining-Rogue-readers.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(passed=True,calls=calls,shared_bank_pages=pairs)))
if __name__=='__main__':main()
