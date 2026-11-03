"""Actual39bb drift repair: native small-player anchor and source solids.

The source owns six-pixel collisions. Native wide queries still deliver exact
coin/vine/flag packets; only unswept solid head/side results are suppressed.
"""
from pathlib import Path
import json,re,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_host_1103_v22 as H
W,R,O=H.W,H.R,H.O
def main():
 prior=json.loads((O/'mini-host-v26.json').read_text());src=(O/'mini-host-v26.s').read_text();changes=[]
 def replace(a,b,reason,count=1):
  nonlocal src
  assert src.count(a)==count,(reason,src.count(a));src=src.replace(a,b);changes.append(reason)
 replace('@correcty:\n lda #8\n jsr MiniHostImportY','@correcty:\n lda #24\n jsr MiniHostImportY','Normal native small anchor is sourceY−24; preserve fractional correction')
 a=src.index('MiniHostMain:\n');b=src.index('MiniHostWallJump:\n',a);part=src[a:b];assert part.count(' sbc #8\n')==1;src=src[:a]+part.replace(' sbc #8\n',' sbc #24\n')+src[b:];changes.append('Native exportsourceY−24; source render remains sourceY−8')
 a=src.index('MiniHostBox:\n');b=src.index('MiniHostSide:\n',a);part=src[a:b];assert part.count(' adc #8\n')==2;src=src[:a]+part.replace(' adc #8\n',' adc #24\n')+src[b:];changes.append('Transport source body bounds with nativeY+24')
 replace('MiniHostSide:\n jmp BlockBufferColli_Side','MiniHostSide:\n jsr BlockBufferColli_Side\n jmp MiniHostFilterSolid','Preserve real native side packet, suppress only solid response owned by source')
 replace('@native:\n jmp BlockBufferColli_Head','@native:\n jsr BlockBufferColli_Head\n jmp MiniHostFilterSolid','Source-swept pending head retains exact native transaction; unswept solid native query is silent')
 replace('MiniHostEnd:\n','''MiniHostFilterSolid:
 php
 cmp #$C2
 beq @keep
 cmp #$C3
 beq @keep
 tax
 lda MiniTileAttributes,x
 and #3
 cmp #1
 beq @solid
@keep:
 ldx #0
 plp
 lda R3
 rts
@solid:
 ldx #0
 plp
 lda #0
 rts
MiniHostEnd:
''','Native coin C2/C3 remain collectable even though old attr low2 alsoequals1')
 # Coin classification is a source-grounded native exception, exactly as
 # CheckForCoinMTiles/ChkForNonSolids process them before ordinary solids.
 replace('Tile_Classify:\n sta MiniQueryTile\n tax\n lda MiniTileAttributes,x','Tile_Classify:\n sta MiniQueryTile\n tax\n cpx #$C2\n beq Tile_Done\n cpx #$C3\n beq Tile_Done\n lda MiniTileAttributes,x','Native coins are passable in source8px terrain as in actual native collision')
 p=O/'mini-host-v28';p.with_suffix('.s').write_text(src);p.with_suffix('.cfg').write_bytes((O/'mini-host-v26.cfg').read_bytes());cc=R/'tools/Windows/cc65/bin'
 for cmd in[[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')],[cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
  r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert r.returncode==0,r.stderr
 data=p.with_suffix('.bin').read_bytes();L={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)};assert len(data)<=5120
 out=dict(passed=True,compiled_only=True,CPU_qualified=False,native_admitted=False,bytes=len(data),SHA256=W.sha(data),labels=L,vectors=[int.from_bytes(data[i*3+1:i*3+3],'little')for i in range(38)],old_SHA256=prior['SHA256'],changes=changes,native_small_anchor='NativeY=(sourceY>>4)−24; sourcecanvas=(sourceY>>4)−8; nativefeet+32=sourcecanvas+16. Body nativeY+24+[top,bottom].',actual_negative=dict(ROM_SHA256='39bb02f36819f88772584bed311992762de74b1099aeb262e8ee71cfd2deb5a4',receipt='build/mini-mario-native-packet-1103-v25/smoke/capture/result.json',sourceX=[47,63,79],nativeX=[63,79,95],cause='Old canvas192 causes native side+24 to sampleground216. Source SamusStopAtWallBanked::LeftClamp ((X+1)&F0)|15 exactly maps47→63→79→95.'),bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),O/'mini-host-v26.s',O/'mini-host-v26.json',R/'src/collision.s',R/'src/samus.s']})
 (O/'mini-host-v28.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','bytes','SHA256','labels']}))
if __name__=='__main__':main()
