"""Actual current Ex/Bub full-cold and every published hot row differential."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_cold_1102_v98 as C
N,O,I=C.N,C.O,C.I


def view(m):return([bytes(z)for z in m.ram],bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x15a:0x17b]),m.rawtags[:],list(m.ppu_log))


def main():
 old,_=C.M.parent();new,manifest=C.image();count=0;rows=[]
 for owner in [37,39]:
  a,ca=C.cold(old,owner);b,cb=C.cold(new,owner)
  assert view(a)==view(b),('Full foreign cold state differs',owner)
  for cwindow in [2,201]:
   for row in range(37):
    for flags in [0x21,0x60,0xa1,0xe1]:
     pair=[N.fork(a),N.fork(b)];out=[]
     for m in pair:
      C.clear(m);m.raw_page(2,cwindow);N.put(m,CurrentBankC=cwindow,FrameCounter=1)
      y=6 if row==10 else 9 if row==14 else 109
      out.append(I.invoke(m,193,0xb08c+3*row,(83,0,y,flags)))
     assert out[0]['regs']==out[1]['regs']and view(pair[0])==view(pair[1]),('Current foreign hot mismatch',owner,cwindow,row,flags,out[0]['regs'],out[1]['regs'])
     count+=1
  rows.append(dict(owner=owner,published_rows=37,C_windows=[2,201],flag_states=4,full_cold_old_CPU=ca['CPU'],full_cold_new_CPU=cb['CPU']))
 q=dict(passed=True,CPU_only=True,ROM_written=False,parent_memory_SHA256=manifest['parent_memory_SHA256'],successor_memory_SHA256=manifest['expected_memory_only_SHA256'],actual_current_foreign_cold_pairs=2,actual_current_foreign_hot_pairs=count,owners=rows,private_native_ZP_0200_07FF_SMC_mapper_PPU_and_returned_AXYP_SP_exact=True,scope='Root Bub66 current parent versus Prince97 successor, using actual complete cold on each side before all37real published rows. Every foreign native/private byte in declared view, full transportSMC, mapper, PPUlog and returnedAXYP/SP match. Existing frame-factor all-raw/source closure remains separately frozen. No DK/performance manager/admission or ROM emission.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(C.__file__),O/'post-return-manifest-v97.json',O/'current-shared-cold-CPU-v99.json']})
 (O/'current-foreign-hot-CPU-v103.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'current-foreign-hot-negative-v103.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
