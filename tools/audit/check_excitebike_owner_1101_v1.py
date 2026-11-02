"""Execute proposed loader at real PRG65 in a memory-only cartridge fixture."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
import check_hogan_current_bounded_v1 as M
O=R/'build/excitebike-pose-1101-v3'


def main():
    candidate=O/'candidate.nes'
    actual_cartridge=candidate.exists()
    b=scoped_load(candidate if actual_cartridge else R/'build/shinobi-camera-1101-v20/candidate.nes')
    raw=bytearray(b['raw']);start=16+65*8192+0xe00
    loader=(O/'owner-loader.bin').read_bytes()
    assert raw[start:start+len(loader)]==(loader if actual_cartridge else bytes([255])*len(loader))
    raw[start:start+len(loader)]=loader
    payload=(O/'owner-actor.bin').read_bytes()+(O/'owner-metadata.bin').read_bytes()+(O/'body-native.chr').read_bytes()
    for index,page in enumerate(range(728,739)):
        at=1048592+page*1024
        assert raw[at:at+1024]==(payload[index*1024:index*1024+1024] if actual_cartridge else bytes(1024))
        raw[at:at+1024]=payload[index*1024:index*1024+1024]
    b['raw']=bytes(raw)
    b['segs']['excitebike_proposal']={'start':str(0xae00),'ooffs':str(start)}
    for line in (O/'owner-loader.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
        if m and m[2].startswith('Ex'):
            b['syms'][m[2]]={'val':str(int(m[1],16)),'seg':'excitebike_proposal'}
    m=M.fresh(b)
    M.put(m,SelectedCharacter=37,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
          Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,ReloadCHRBank=1)
    m.ppuctrl=160
    before=M.fork(m);reads=m.ppu_reads
    cold=M.invoke(m,'ExLoad')
    assert cold['P']&1 and m.ppu_reads-reads==16400,(cold,m.ppu_reads-reads)
    assert bytes(m.ram[3][:6144])==(O/'owner-actor.bin').read_bytes()
    assert bytes(m.ram[2][4096:6144])==(O/'owner-metadata.bin').read_bytes()
    assert bytes(m.ram[2][:2048])==bytes(2048)
    cookie=(O/'excitebike-cookie.bin').read_bytes()
    for bank in [2,3]:assert bytes(m.ram[bank][8160:8176])==cookie
    assert [bytes(x) for x in m.ram[:2]]==[bytes(x) for x in before.ram[:2]]
    reads=m.ppu_reads;warm=M.invoke(m,'ExLoad');assert warm['P']&1 and m.ppu_reads==reads
    rejected=0
    for bank in [2,3]:
      for index in range(16):
        n=M.fork(m);n.ram[bank][8160+index]^=1
        assert not M.invoke(n,'ExCheckCode')['P']&1
        rejected+=1
    guards=[dict(SelectedCharacter=36),dict(SelectedCharacter=0),dict(OperMode=0),
            dict(FamilyMainCommit=0),dict(DisableScreenFlag=0),dict(Mirror_PPUMASK=24),dict(NmiDisable=0)]
    for field in guards:
        n=M.fork(before);M.put(n,**field);snapshot=[bytes(x) for x in n.ram];reads=n.ppu_reads
        assert not M.invoke(n,'ExLoad')['P']&1
        assert snapshot==[bytes(x) for x in n.ram] and n.ppu_reads==reads
    M.invoke(m,'ExRetire')
    assert m.ram[2][8160]==m.ram[3][8160]==0
    result=dict(passed=True,cartridge_SHA256=hashlib.sha256(raw).hexdigest(),
        actual_PRG_bank=65,resident_CPU_start=44544,cold=cold,warm=warm,
        buffered_PPU_reads=16400,complete_header_corruptions_rejected=rejected,
        rejected_cold_guards=len(guards),foreign_RAM0_1_unchanged=True,retired_both_headers=True,
        actual_composed_cartridge=actual_cartridge,ROM_file_written_by_test=False,
        scope='Native FarCallCommon and actual PRG65 loader placement; exact original actor/metadata copied and verified. No menu/runtime admission or native emulator claim.')
    (O/'owner-CPU.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
