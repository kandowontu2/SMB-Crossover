"""Root-reviewed conditional DK Jr carrier/overlay reservation; no ROM emit."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/dkjr-root-resources-1102-v20'
D=R/'docs/qa/checkpoints/2026-11-02/dkjr-admission-proposal-v20'
G=R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json'

def main():
    p=R/'build/dkjr-native-source-1102-v2';manifest=p/'admission-proposal-v20.json';q=json.loads(manifest.read_text())
    assert sha(manifest)=='e827388694f6d1fc0367d9dbb5cd6d5d071d7dd47b6f65d30c92b9ef05525a1c'
    assert q['passed']and not q['native_candidate_complete']and not q['ROM_written']
    archive=p/'admission-proposal-v20-inputs.zip';assert sha(archive)==q['archive_SHA256']=='8e0aa0376864a5288dff35c9fd567e07f1c14b08b6a00e861b9a9bb0d393488e'
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(q['members'])==61
        for row in q['members']:
            name=row['path'];assert not Path(name).is_absolute()and'..'not in Path(name).parts
            data=z.read(name);assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['SHA256']and(R/name).read_bytes()==data,name
    base=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');raw=base.read_bytes();assert sha(base)==q['base_ROM_SHA256']=='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
    carriers=json.loads((p/'carrier-proposal-v13.json').read_text());pub=json.loads((p/'publication-v14-CPU.json').read_text())
    assert carriers['passed']and carriers['complete_current_publisher_closure']and not carriers['domain_collisions']
    assert pub['passed']and pub['no_proposed_page_published']and pub['real_NMI_returns']==5057
    for row in carriers['preimages']:assert hashlib.sha256(raw[row['offset']:row['offset']+1024]).hexdigest()==row['SHA256']
    resources=q['requested_resources'];assert resources['code_pages']==[817,833,847,856,867,881,882,883]and resources['art_and_helpers']==[959,960,961]
    assert resources['raw_identity']==40 and 40 not in carriers['current_menu']['raw_values']
    assert not D.exists()and not G.exists();D.mkdir(parents=True)
    for src,name in[(archive,'inputs.zip'),(manifest,'proposal.json')]:
        (D/name).write_bytes(src.read_bytes());assert sha(D/name)==sha(src)
    grant=dict(status='APPROVED_CONDITIONAL_PRIVATE_CARRIER_AND_OVERLAY_RESERVATION_ONLY',owner='Donkey Kong Jr.',raw_identity=40,reviewed_base_SHA256=sha(base),proposal=manifest.relative_to(R).as_posix(),proposal_SHA256=sha(manifest),checkpoint=D.relative_to(R).as_posix(),code_pages=resources['code_pages'],art_and_helpers=resources['art_and_helpers'],physical_preimages=carriers['preimages'],exclusive_conditional_RAM=resources,review='Root read finite source publisher/writer rebind, actual current menu inventory, publication interrupt fixture and complete frozen proposal recipe. All61 direct packet members match live bytes. Eleven carrier preimages match actual installed9cf; finite existing consumers exclude these pages (Gimmick816/818, exact Parodius18-row tables and Arthur868..880). 806 inherited writer instructions remain exact, ten moved WWF writes retain their finite source rules, and all private writer chunks are bound. 2640 actual setter cuts,2376 native menu cuts and5057 lag-NMI returns publish none of these eleven pages. These checks reserve private resources; they do not qualify a new public dispatcher or complete native candidate.',conditions=[
        'Reserve these eleven physical pages exclusively for DK Jr private composition. A later base needs exact preimages, finite consumer rebind and preservation of all currently delivered character bytes.',
        'RAM3 A000..BFE0 and RAM2 C000..C900/D000..D800 are mutually exclusive owner overlays, never unconditional writable RAM. Retire every old owner before overwrite; invalidate both full headers before copying; copy/verify under forced blank and disabled interrupts; publish final ready byte last. Preserve headers and shared DFD0..DFD3 clock.',
        'This does not approve the proposed shared manager, selector, transport, menu, native hooks or public raw40 admission. Those need consistent final source, actual full ingress/lifecycle/IRQ/SMC/AXYP/indirect-reader proofs and a separate root-reviewed composition.',
        'The frozen proposal binds private Princev65 only. Rebind its measured successor, the exact current Bub cookie and all Sunny patches before any combined candidate. Shared cookie overlap must be semantically relinked, never called disjoint.',
        'Do not treat projected7962B body-plus-vector size as compiled proof. Complete the real38-entry vector, native services, art tile-index closure and full payload-derived cookies before a native-ready claim.',
        'Keep earned capture Main unpaused and pause the following60 original D1AE branches. Mechanical enemy/hazard motion and cannon countdown/spawns must freeze; native visual-frame effects may retain documented host pause behavior. Close nested powerup/scene/death/retirement restoration.',
        'Initial focused-only DK/Jr Select behavior and deliberate shared DK family portrait are temporary functional-pass choices. A distinct correct DONKEY KONG JR name is required; identity must persist through gameplay life/stage/game-select. No false unique portrait claim.',
        'Root owns Mesen and installation. No native admission, nightly delivery or all-stage/powerup/audio qualification is implied by this reservation.'
    ],shared_bytes_granted=0,menu_admission_authorized=False,ROM_emission_authorized=False,installation_authorized=False)
    G.parent.mkdir(exist_ok=True);G.write_text(json.dumps(grant,indent=2)+'\n',encoding='utf-8')
    O.mkdir(exist_ok=True);(O/'receipt.json').write_text(json.dumps(dict(passed=True,grant=G.relative_to(R).as_posix(),grant_SHA256=sha(G),verified_members=61,carrier_pages=11,ROM_written=False),indent=2)+'\n')
    print(json.dumps(dict(passed=True,verified_members=61,grant=G.relative_to(R).as_posix(),grant_SHA256=sha(G),ROM_written=False)))

if __name__=='__main__':main()
