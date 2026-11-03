"""Current32-slot silhouette oracle; preserve the obsolete139 native negative."""
from pathlib import Path
import inspect,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_first_native_1103_v139 as V


def main():
 base,_=V.C.image();base=dict(base,raw=V.ROM.read_bytes());N=V.C.N
 screen=N.fresh(base);N.put(screen,CrossoverMenuState=1,Mirror_PPUMASK=0,DisableScreenFlag=1);N.invoke(screen,'CrossoverMenuInput')
 silhouette=[[(12+y)*32+25+x,screen.vram[0x2000+(12+y)*32+25+x]]for y in range(4)for x in range(3)]
 assert any(cell[1]!=36 for cell in silhouette),'Actual current Battletoads silhouette populated'
 source=Path(V.__file__);text=inspect.getsource(V.main)
 text=text.replace("hooks=hooks)","hooks=hooks,silhouette=SILHOUETTE)")
 marker="body=source.read_text();extension=";assert text.count(marker)==1
 adaptation='''body=source.read_text()
 old="  for _,cell in ipairs({{676,245},{677,246},{708,247},{709,248}})do assert(ppu(0x2000+cell[1])==cell[2],'Actual same-span NT copy/icon survives rebuild')end"
 assert body.count(old)==1;body=body.replace(old,"  for _,cell in ipairs(Q.silhouette)do assert(ppu(0x2000+cell[1])==cell[2],'Actual current Battletoads silhouette survives selection')end")
 start=body.index('  if s.slot==32 then');end=body.index("  if s.family=='BT'",start);body=body[:start]+body[end:]
 assert "assert(n==33,'All33 positions actually visited')"in body
 body=body.replace("assert(n==33,'All33 positions actually visited')","assert(n==32,'All32 positions actually visited')")
 extension='''
 text=text.replace(marker,adaptation)
 old="O/('native-first-'+a.mode+'-v139')";assert old in text;text=text.replace(old,"O/('native-first-'+a.mode+'-v142')")
 text=text.replace('refs={Path(__file__),source,extension,','refs={Path(__file__),R/"tools/audit/prepare_prince_first_native_1103_v139.py",R/"tools/audit/prepare_menu_family_native_1102_v1.py",source,extension,')
 env=dict(V.__dict__,__file__=str(Path(__file__)),SILHOUETTE=silhouette);exec(compile(text,str(source),'exec'),env);env['main']()


if __name__=='__main__':main()
