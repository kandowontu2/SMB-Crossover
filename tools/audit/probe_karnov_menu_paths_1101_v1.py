"""Observe actual typed UI callers before adding Karnov's cold ROM handlers."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address
O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    b=H.C.qualified(O/'candidate.nes');results=[]
    for name in ['GetPlayerColors','QueueSelectName','DrawPlayer_Intermediate','X5PortraitRender','QueueVariantHint','HuMenuPortrait','HuMenuName','HuStatus','HuWorldPalette']:
        m=C.fresh(b);H.put(m,SelectedCharacter=34,CrossoverMenuIndex=7,FmAlts=1,CurrentOAMOffset=0,VRAM_Buffer1_Offset=0)
        row=dict(entry=name,typed_services=[],RAM_cache_reads_before=m.ppu_reads)
        c=H.start(m,name,a=1,x=7,y=30)
        def watch(mem,c,i):
            if c.pc==address(b,'KrDispatch')and mem.rawtags[1]==157:
                at=address(b,'FarcallJmpTarget_SMC');target=mem[at+1]|mem[at+2]<<8
                row['typed_services'].append(dict(row=(target-address(b,'KrServiceVeneers'))//3,A=mem[address(b,'SafecallA_SMC')+1],X=c.x,Y=c.y,P=c.p))
        try:
            c,low=H.finish(m,c,watch);row.update(returned=[c.a,c.x,c.y,c.p,c.sp],minimum_SP=low,queue_bytes=H.get(m,'VRAM_Buffer1_Offset'),OAM_bytes=H.get(m,'CurrentOAMOffset'),RAM_cache_reads_after=m.ppu_reads)
        except Exception as e:row.update(error=repr(e),traceback=traceback.format_exc())
        results.append(row)
    q=dict(source_CPU=True,native=False,diagnostic_only=True,menu_admitted=False,ROM_sha256=sha(O/'candidate.nes'),rows=results,bindings={str(p.resolve()):sha(p)for p in [Path(__file__),O/'candidate.nes',O/'candidate.dbg']})
    (O/'menu-path-probe.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(results))

if __name__=='__main__':main()
