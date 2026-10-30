"""Reserve a private banked-WRAM experiment, with no shared header adoption."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'docs/qa/checkpoints/2026-10-30/mmc5-overlay-private-allocation'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    quick=R/'build/quickman-host-cpu-v4/candidate.nes'
    expected='774a78ed9b9ca4bee3276019fac40a0233abc71f5d5d26f9dacb2963b7bd329d'
    assert sha(quick)==expected
    raw=quick.read_bytes()
    assert len(raw)==16+1048576+1048576
    first=16+1048576+884*1024
    original=R/'build/character-host-union-v5/candidate.nes'
    pn_start=16+1048576+832*1024
    assert raw[pn_start:]==original.read_bytes()[pn_start:]
    dense=R/'build/parodius-chr-compact-v1/candidate.nes'
    assert dense.read_bytes()[first:first+9*1024]==bytes(9*1024)
    lab=R/'build/mmc5-overlay-lab-v1/native/result.json'
    result=json.loads(lab.read_text())
    assert result['passed']and result['frames']==2
    paths=[Path(__file__).resolve(),quick,original,dense,lab,R/'build/mmc5-overlay-lab-v1/ready.json',
           R/'build/quickman-wram-whole-cpu-v3/handoff.json',
           R/'docs/qa/checkpoints/2026-10-30/arthur-quick-private-allocation/root-review-and-reservations.json',
           R/'docs/qa/checkpoints/2026-10-30/parodius-dense-chr/root-review-and-reservations.json']
    report=dict(status='PRIVATE_LOADER_EXPERIMENT_ALLOCATION_ONLY_NO_SHARED_FORMAT_CHANGE',
        immutable_Quick_parent_sha256=expected,
        CHR=dict(owner='Quick selected-owner code/data stream',first_page=884,page_count=9,end_exclusive=893,
                 code_pages=7,data_pages=2,verified_zero_in_compacted_parent=True,
                 Quick_parent_still_has_original_192page_Parodius=True,
                 condition='First compose the exact dense Parodius832..<868 source producer and split cfg. Quick774a78 still has the original192page atlas and MUST NOT receive this stream before that source composition. Arthur868..<884 remains reserved; original Quick251..<256 body graphics remain unchanged.'),
        PRG_RAM=dict(private_header_bytes=32768,shared_current_header_bytes=8192,
            bank0='Existing6000..7FFF global game state remains bank0; no new aliases here.',
            bank1='Quick code raw01 throughA000..BFFF, selected-owner exclusive.',
            bank2='Quick data raw02 throughC000..DFFF; may temporally alias a separately qualified Arthur draw cache after owner retirement.',
            bank3='Unallocated; no implicit staging reservation.'),
        retained_PRG='Use the existing10060B Quick lease for genuine loader/route bridges. No new resident space or other owner lease is granted.',
        rejected_precondition='The first allocation check correctly failed: Quick884..<893 is not currently blank. Exact parent comparison proves retained old Parodius art, rather than an available physical hole. This grant is conditional on the already qualified dense source composition.',
        requirements=['Private source-linked successor only; retain frozen774a78 CPU packet unchanged.',
            'Loader must reach actual forced-blank scene boundary; no active-display PPU transfers.',
            'Use real buffered2007 reads and verify exact code/data copies. Restore all PPU/CHR/scroll and software/hardware bank state.',
            'Cold/warm resets, player alternation and owner retirement must invalidate/rebuild the selected-owner cache before execution.',
            'Preserve every original source routine/field, actual source/world callback and complete normal/lag NMI/IRQ contracts with rawRAM tags.',
            'Menu preview must remain visible before gameplay construction; no uninitializedRAM reads.',
            'Actual32KB header baseline and Quick native controller/cadence must pass before adoption. No physical-cartridge compatibility claim.'],
        bindings={str(p):sha(p)for p in paths})
    D.mkdir(parents=True)
    p=D/'root-review-and-reservations.json'
    p.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(path=str(p),sha256=sha(p))))


if __name__=='__main__':main()
