"""Cold palette ABI, unchanged warm rejection paths, and existing Chip HUD."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_world_palette_1101_v18 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
def main():
    s=json.loads((P.O/'assembly.json').read_text())
    for p,h in s['bindings'].items():assert P.sha(p)==h,p
    old=scoped_load(P.P.O/'candidate.nes');new=dict(old,raw=(P.O/'candidate.nes').read_bytes())
    seed=M.fresh(new);palette=0
    for area,flags in itertools.product(range(4),[0x30,0x31,0x70,0x71,0xf0,0xf1,0x39,0xf9]):
        a=M.fork(seed);M.put(a,SelectedCharacter=35,AreaType=area);z=M.fork(a)
        x=M.invoke(a,'HuWorldPalette',a=35,y=91,p=flags);y=M.invoke(z,'HuNativeWorldPalette',a=35,y=91,p=flags)
        assert tuple(x[n] for n in ['A','X','Y','P'])==tuple(y[n] for n in ['A','X','Y','P'])
        assert bytes(a[:11])==bytes(z[:11]) and a.ram==z.ram and x['Y']==6*(area+1)
        palette+=1
    left=M.fresh(old);right=M.fresh(new)
    omit=set(range(0x100,0x200))|set(range(0x2000,0x5c00))|{address(old,n) for n in ['CurrentBank','CurrentBankC','safecall_a']}
    def state(m):return bytes(v for i,v in enumerate(m[:0x8000]) if i not in omit),[bytes(r) for r in m.ram]
    hud=0
    for mode,disabled,offset in itertools.product([0,1],[0,1],[0,60,76,77,80]):
        a=M.fork(left);z=M.fork(right)
        for m in [a,z]:M.put(m,SelectedCharacter=14,OperMode=mode,DisableScreenFlag=disabled,VRAM_Buffer1_Offset=offset);M.invoke(m,'CdHud')
        assert state(a)==state(z),(mode,disabled,offset);hud+=1
    q=dict(passed=True,ROM_sha256=s['ROM_sha256'],cold_palette_cases=palette,unchanged_Chip_HUD_cases=hud,installed=False,native=False)
    (P.O/'palette-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
