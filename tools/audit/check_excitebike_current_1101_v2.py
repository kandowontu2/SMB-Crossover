"""Run the complete menu/parser/Main on the repaired current in-memory image."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_excitebike_current_1101_v1 as C
import check_excitebike_cold_1101_v1 as L
from compose_excitebike_current_1101_v2 import bundle
from prepare_excitebike_dispatch_1101_v1 import O,save,sha
from prepare_excitebike_host_1101_v1 import BASE,PIN


def main():
    # Reuse the same real menu/Start/parser/Main sequence. Only the composed
    # input image and receipt name change; add concrete PPU/OAM publication
    # checks at normal-NMI completion in active gameplay.
    C.bundle=bundle;C.save=lambda name,q:save('current2-CPU.json',q)
    consume=C.M.consume;seen=0
    def checked(m):
        nonlocal seen
        consume(m)
        if C.M.get(m,'OperMode_Task')!=3 or C.M.get(m,'GameEngineSubroutine')!=8:return
        assert m.ram[2][0x800]==167
        obj=C.address(m.bundle,'ObjectMetasprite');ptr=C.address(m.bundle,'SmPosePtr')
        assert m[obj]==0 and m[ptr]+256*m[ptr+1]==obj
        assert C.M.get(m,'CurrentOAMOffset')%4==0
        assert m.chr_latches[4:8]==[736,737,738,739],m.chr_latches
        assert bytes(m.vram[0x3f11:0x3f14])==bytes([32,22,15]),list(m.vram[0x3f10:0x3f14])
        assert bytes(m.vram[0x2043:0x204a])==bytes([14,33,11,18,20,14,36]),list(m.vram[0x2040:0x2050])
        seen+=1
    C.M.consume=checked
    try:C.main()
    finally:C.M.consume=consume
    q=json.loads((O/'current2-CPU.json').read_text());assert q['passed']and seen>=270
    q.update(actual_completed_NMI_CHR_palette_HUD_aligned_OAM_checks=seen,
             source_terrain_native32px_intentional=True,
             bindings={**q['bindings'],Path(__file__).relative_to(R).as_posix():sha(__file__)})
    save('current2-CPU.json',q)
    # Run actual cold copy/verify with the same new image, including every
    # distinct code/stateheader commit and upper-latch caller boundary.
    L.bundle=bundle;L.save=lambda name,q:save('cold2-CPU.json',q);L.main()

if __name__=='__main__':main()
