"""Require an identical heading on every physical menu-transition frame."""
from pathlib import Path
import json,sys
import prepare_roster_flicker_native_bounded_v2 as V
from prepare_selected_native_packet_v1 import sha


def main():
    V.main();output=Path(sys.argv[sys.argv.index('--output')+1]).resolve();path=output/'controller.lua';text=path.read_text()
    changes=[
        ("local phase,done='title',false","local phase,done='title',false\nlocal headingBase,headingErrors,lateMasks=0,0,0"),
        (' local lit,hash=0,0',' local lit,hash,heading=0,0,0'),
        ("if screen[y*256+x+1]&0xffffff~=black then lit=lit+1 end","heading=((heading*33)~(screen[y*256+x+1]&0xffffff))&0x7fffffff;if screen[y*256+x+1]&0xffffff~=black then lit=lit+1 end"),
        (' return lit,hash',' return lit,hash,heading'),
        ('local lit,hash=pixels()','local lit,hash,heading=pixels()'),
        ("baseline=hash;shot('initial')","baseline=hash;headingBase=heading;shot('initial')"),
        ('portrait_hash,OAM_DMA','portrait_hash,header_hash,OAM_DMA'),
        ("lit,hash,oam,chr,#maskEvents","lit,hash,heading,oam,chr,#maskEvents"),
        ("  if lit<100 or hash~=baseline", "  if heading~=headingBase then headingErrors=headingErrors+1 end\n  if lit<100 or hash~=baseline"),
        ("if scan>=0 and scan<240 then events[#events+1]={frame=frame,action=step,reg=reg,value=value,scanline=scan,cycle=s['ppu.cycle'],pc=s['cpu.pc']}end", "if scan>=0 and scan<240 then lateMasks=lateMasks+1;events[#events+1]={frame=frame,action=step,reg=reg,value=value,scanline=scan,cycle=s['ppu.cycle'],pc=s['cpu.pc']}end"),
        (" if done then return end;done=true;shot('endpoint')", " if done then return end;ok=ok and headingErrors==0 and lateMasks==0;reason=reason..'; heading errors='..headingErrors..', visible mask writes='..lateMasks;done=true;shot('endpoint')"),
        ('passed=ok,reason=reason,ROM_sha256','passed=ok,heading_errors=headingErrors,heading_hash=headingBase,visible_mask_writes=lateMasks,reason=reason,ROM_sha256'),
    ]
    for old,new in changes:
        assert text.count(old)==(2 if old=='local lit,hash=pixels()'else 1),(old,text.count(old));text=text.replace(old,new)
    path.write_text(text,encoding='utf-8',newline='\n')
    ready_path=output/'ready.json';ready=json.loads(ready_path.read_text())
    for p in[path,Path(V.__file__).resolve(),Path(__file__).resolve()]:ready['bindings'][str(p)]=sha(p)
    ready['scope']+=' Require pixel-identical heading on all2400 observed transition frames and zero visible-scanline PPUMASK writes. Static-portrait hashes also include harmless colored-preview overlap and are diagnostic only.'
    ready_path.write_text(json.dumps(ready,indent=2)+'\n')


if __name__=='__main__':main()
