"""Retain the reviewed compact Bub source packet without expanding it."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-landing-root-freeze-1102-v27'
D=R/'docs/qa/checkpoints/2026-11-02/bub-landing-v27'

def main():
    source=R/'build/bub-menu-candidate-1102-v2'
    receipt=source/'landing-source-checkpoint-v27.json';q=json.loads(receipt.read_text())
    archive=source/'landing-source-checkpoint-v27.zip'
    assert q['passed']and not q['native_full11_passed']and not q['installed']
    assert sha(archive)==q['archive_SHA256']=='538bdcdc681ba01a7ecd8aacf6dce10f4906dd96247da59e818f256b8c19eb0d'
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(q['files'])and sum(x.file_size for x in z.infolist())<2_000_000
        for name,meta in q['files'].items():
            assert not name.endswith(('.nes','.mp4'))and not Path(name).is_absolute()and '..'not in Path(name).parts
            data=z.read(name);assert len(data)==meta['bytes']and hashlib.sha256(data).hexdigest()==meta['SHA256']
            assert(R/name).read_bytes()==data,name
    proposal=source/'landing-rebase-v27-proposal.json';p=json.loads(proposal.read_text())
    current=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(current)==p['current_base_ROM_sha256']=='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'
    memory=bytearray(current.read_bytes())
    for patch in p['patches']:
        at=patch['offset'];old=bytes.fromhex(patch['old']);new=bytes.fromhex(patch['new'])
        assert len(old)==len(new)and memory[at:at+len(old)]==old
        memory[at:at+len(new)]=new
    assert hashlib.sha256(memory).hexdigest()==p['expected_rebased_ROM_sha256']
    assert p['Sunny_five_patches_preserved']and p['exact_byte_intervals_disjoint']
    assert not D.exists();D.mkdir(parents=True)
    for src,name in [(archive,'inputs.zip'),(receipt,'receipt.json'),(proposal,'rebase-proposal.json')]:
        target=D/name;target.write_bytes(src.read_bytes());assert sha(target)==sha(src)
    O.mkdir(exist_ok=True)
    (O/'receipt.json').write_text(json.dumps(dict(passed=True,private_source_checkpoint=True,installed=False,ROM_written=False,files=len(q['files']),checkpoint=str(D.relative_to(R)),ZIP_SHA256=sha(D/'inputs.zip'),memory_only_rebase_SHA256=hashlib.sha256(memory).hexdigest(),scope='Root verified all75 archived files against live inputs and exact three-span current16a9 preimages in memory. SolePNG is a CPU facing raster; noROM or emulatorcapture copied. Fullstage remains negative, source packet only.'),indent=2)+'\n')
    print('Frozen reviewed private source packet; no ROM created or installed.')

if __name__=='__main__':main()
