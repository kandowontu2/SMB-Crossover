"""Real ten-row loader and combat in actual Main; no executable RAM fixture."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_karnov_combat_main_1101_v6 as T
O=R/'build/karnov-combat-native-1101-v7'
EXPECTED='0ffb1d79c4fbc52bb337a4726f8e61f984f30e4795fd2555b204322140c0a717'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    O.mkdir(exist_ok=True);assert not(O/'binding.json').exists()
    T.INTEGRATED=True;T.EXPECTED=EXPECTED
    q=dict(passed=False,ROM_sha256=EXPECTED,no_executable_overlay=True,native_emulator=False,installed=False)
    try:
        raw=(T.BASE/'candidate.nes').read_bytes();tiles=(T.BASE/'kr-shot-tiles.bin').read_bytes()
        bounds=[]
        for tile in tiles:
            base=1048592+410*1024+((tile&254)*16&1023)
            rows=[y for y in range(16)if raw[base+(y//8)*16+y%8]|raw[base+(y//8)*16+y%8+8]]
            assert rows and min(rows)>=8 and max(rows)<=15
            bounds.append(dict(tile=tile,opaque_rows=[min(rows),max(rows)]))
        q['projectile_CHR_bounds']=bounds
        q['Main']=T.main_checks();q['passed']=q['Main']['passed']
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['scope']='Actual cold Select/Start/parser/ten-row copy/readback, authenticated4/34 and original actor/source-shot update. Enemy/block data fixtures create combat contacts; IRQ/NMI cuts preserve full live frame/SMC/maps. No executable RAM injection and no controller-earned combat claim.'
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(T.__file__),T.BASE/'candidate.nes',T.BASE/'candidate.dbg',T.BASE/'terrain-assembly.json',T.BASE/'kr-combat.bin',T.BASE/'kr-kernel.bin']}
    (O/'combat-Main-controls.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=q['passed'],error=q.get('error'),minimum_ISR=q.get('Main',{}).get('minimum_Main_ISR_SP'),cuts=sum(len(x['interrupts'])for x in q.get('Main',{}).get('cases',[])))));assert q['passed'],q.get('error','Main stack reserve')


if __name__=='__main__':main()
