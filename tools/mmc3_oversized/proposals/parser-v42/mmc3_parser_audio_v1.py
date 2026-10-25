from pathlib import Path
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover')
s=(R/'tools/audit/check_gradius_linked_nv.py').read_text()
s=s.replace("ROOT = Path(__file__).resolve().parents[2]",'ROOT = Path('+repr(str(R))+')')
s=s.replace('prg = rom[16:16 + 1024 * 1024]','prg = rom[16:16 + 2 * 1024 * 1024]')
s=s.replace('prg[0x7a * 8192:0x7b * 8192]','prg[0xfd * 8192:0xfe * 8192]').replace('prg[0x7f * 8192:0x80 * 8192]','prg[0xff * 8192:0x100 * 8192]')
s=s.replace('self.events = []; self.writes = set()','self.events = []; self.writes = set(); self.rom_reads = set()')
anchor='        def __setitem__(self, key, value):'
read='''        def __getitem__(self, key):
            if isinstance(key, int) and 0xa000 <= key < 0xc000:
                assert key < 0xb725, ('Native Gradius read reaches new cold tail',hex(key))
                self.rom_reads.add(key)
            return list.__getitem__(self,key)
'''
assert s.count(anchor)==1;s=s.replace(anchor,read+anchor)
s=s.replace('bounded_RAM_writes=True)','bounded_RAM_writes=True, native_ROM_unique_reads=len(bus.rom_reads), highest_native_ROM_read=max(bus.rom_reads), cold_tail_read_count=0)')
s=s.replace("tracks=results,", "tracks=results, highest_native_ROM_read=max(z['highest_native_ROM_read']for z in results.values()), cold_tail_start=0xb725, cold_tail_read_count=0,")
s=s.replace("Actual linked music code plus actual linked flag-preserving APU buffering helpers, executed against original NSF events. Native NMI/mixer/gameplay validation is separate.","Actual linked MMC3 FD music code plus actual FF flag-preserving APU buffering helpers, all32 original NSF songs/227000 frames with ordered APU golden events and bounded native RAM. Every CPU read from the mapped FD ROM window is guarded belowB725; instruction/data reads never consume the appended warp tail in this complete existing source corpus. Native NMI/mixer/gameplay validation and hypothetical corrupted/native state are separate.")
exec(compile(s,str(R/'tools/audit/check_gradius_linked_nv.py'),'exec'),globals())
