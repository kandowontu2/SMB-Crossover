"""Actual native GameCore with measured post-return hook; in-memory only."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_deferred_death_1102_v76 as V
O=V.O


def patch(m):
 raw=bytearray(m.bundle['raw']);off=lambda pc:16+124*8192+pc-0xa000
 for pc,file in [(0xa760,'post-return-v78.bin'),(0xa795,'post-return-second-v78.bin')]:
  blob=(O/file).read_bytes();at=off(pc);assert raw[at:at+len(blob)]==bytes([0xea])*len(blob);raw[at:at+len(blob)]=blob
 at=off(0xad75);assert raw[at:at+3]==bytes.fromhex('8d6a01');raw[at:at+3]=bytes.fromhex('2060a7')
 m.bundle=dict(m.bundle,raw=bytes(raw))
 for win,tag in enumerate(m.rawtags):
  if tag==252:m.raw_page(win,tag)


def environment():
 source=Path(V.__file__);text=source.read_text().replace('v76','v79').replace('v75','v78')
 marker=" blob,_=A.A.assemble('deferred-selector-v79'"
 text=text.replace(marker," assert text.count(' sta $c09e')==1;text=text.replace(' sta $c09e',' sta $0179')\n"+marker)
 text=text.replace('N.put(m,Mirror_PPUMASK=30);m[0x2001]=30','PATCH(m);N.put(m,Mirror_PPUMASK=30);m[0x2001]=30')
 env=dict(__file__=str(Path(__file__)),__name__='prince_postreturn_core_v79',PATCH=patch);exec(compile(text,str(source),'exec'),env)
 return env


def loaded():return environment()['loaded']()


if __name__=='__main__':environment()['main']()
