"""Freeze the preview repair and actual new-host evidence with admission limits."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save,sha


def add(bindings,*paths):
    bindings.update({str(p):sha(p)for p in paths})


def rogue():
    o=R/'build/rogue-current-menu-v6'
    bp=o/'build-proof.json';cp=o/'controls.json';pp=o/'preview-priority-controls.json'
    b,c,p=[json.loads(x.read_text())for x in [bp,cp,pp]]
    digest=sha(o/'candidate.nes')
    assert b['ROM_sha256']==c['ROM_sha256']==p['ROM_sha256']==digest
    assert c['passed']and p['passed']and len(p['cases'])==80
    n=json.loads((o/'native/menu/result.json').read_text())
    assert n['passed']and n['alternates']==80 and n['Rogue_hardware_parts']==5
    cadence=json.loads((o/'native/bill-cadence-review.json').read_text())
    assert cadence['passed']and not cadence['cadence_nonregression']
    assert cadence['runs'][0]['lag_NMIs']==4 and cadence['runs'][1]['lag_NMIs']==33
    bindings=dict(b['source_bindings'])
    bindings.update(c['source_bindings']);bindings.update(p['source_bindings'])
    bindings.update(cadence['source_bindings'])
    add(bindings,bp,cp,pp,o/'native/bill-cadence-review.json',Path(__file__).resolve())
    for folder in ['menu','bill-parent-v1','bill-candidate-v1','bill-profile-v1']:
        f=o/'native'/folder
        bind=json.loads((f/'binding.json').read_text())
        assert bind['exit_code']==0
        for path,h in bind['inputs'].items():assert sha(path)==h,path
        bindings.update(bind['inputs'])
        for path in f.iterdir():
            if path.is_file():add(bindings,path)
    passive=json.loads((o/'native/bill-profile-v1/binding.json').read_text())
    assert passive['passive_only']and passive['inverse_controller_exact']
    for name in passive['byte_identical_native_outputs']:
        assert(o/'native/bill-profile-v1'/name).read_bytes()==(o/'native/bill-candidate-v1'/name).read_bytes()
    save('rogue-preview-priority-and-timing',dict(
        status='NATIVE_MENU_REPAIR_PASS_LEGACY_BILL_CADENCE_FAIL_PRIVATE_ONLY',
        ROM_sha256=digest,native_menu=n,source_preview_cases=80,
        root_visual_review='Root viewed actual rogue-preview.png: genuine colored Rogue body visible over the blue menu panel.',
        repair='Clear priority bit5 only in emitted native preview OAM; all80 old/new OAM comparisons equal except that exact attribute mask.',
        native_Bill=cadence,passive_profile_exact=True,
        limits=['Legacy Bill skips33NMIs vs4on the current download; this candidate must not replace the shared build.',
                'New per-character wrappers add repeated foreign bank trips; typed joint routing/optimization is required.',
                'V5Rogue route parity is separate. ExactV6Rogue1-1 replay/all-powerups remain unqualified.',
                'Private48ready/32pending flags do not establish full-roster gameplay completion.']),bindings)


def arthur():
    o=R/'build/arthur-host-integration-v2'
    hp=o/'arthur-handoff.json';h=json.loads(hp.read_text())
    assert sha(hp)=='325e573fcfdac0998eeebb7246c081ff36dda7d2327b3a567fda693bc19dc531'
    assert sha(h['ROM']['path'])==h['ROM']['sha256']=='4fb11bca5ac7abfeffef461fd15de73d32b574bc3c60ae41573c45c15ce1a2b2'
    closure=json.loads(Path(h['source_closure']['path']).read_text())
    assert sha(h['source_closure']['path'])==h['source_closure']['sha256']
    entries=closure['source_and_evidence']
    bindings={x['path']:x['sha256']for x in entries}
    assert len(bindings)==773
    archive=Path(h['source_archive']['path'])
    assert sha(archive)==h['source_archive']['sha256']
    # Verify every archived member against its frozen compiled-source closure.
    with zipfile.ZipFile(archive)as z:
        for name in z.namelist():
            raw=z.read(name)
            matching=[p for p in bindings if Path(p).resolve().is_relative_to(R)and Path(p).resolve().relative_to(R).as_posix()==name]
            if matching:assert hashlib.sha256(raw).hexdigest()==bindings[matching[0]],name
    add(bindings,hp,Path(h['source_closure']['path']),Path(__file__).resolve())
    native=closure['native'];timing=closure['native_timing']
    assert native['passed']
    save('arthur-visible-native-smoke',dict(
        status=h['status'],ROM_sha256=h['ROM']['sha256'],native=native,native_timing=timing,
        root_visual_review='Root independently viewed actual menu, double-jump and source-lance PNGs: visible authentic body, ARTHUR HUD and blue overworld. Agent reviewed all six selections.',
        controls='13CPUgroups, including216completeMain→nativePlayerBankReady→normalNMI/lag page commits; previous868→768overwrite failure retained.',
        limits=h['limits']),bindings)


def quick():
    o=R/'build/quickman-host-cpu-v4'
    hp=o/'handoff.json';h=json.loads(hp.read_text())
    assert sha(hp)=='91239729bdd6bcf95684d022dded525f19eab9f2c668f857c090fbc1a1dfad59'
    assert h['ROM_sha256']==sha(o/'candidate.nes')=='774a78ed9b9ca4bee3276019fac40a0233abc71f5d5d26f9dacb2963b7bd329d'
    assert not h['native_qualification']and not h['shared_install']
    bindings=dict(h['bindings'])
    for path,digest in bindings.items():assert sha(path)==digest,path
    # Include the genuine compiled sources stored in the compact source ZIP.
    sourcezip=o/'source-closure.zip'
    with zipfile.ZipFile(sourcezip)as z:
        for name in z.namelist():
            p=R/name
            assert p.resolve().is_relative_to(R)and p.is_file(),name
            assert p.read_bytes()==z.read(name),name
            add(bindings,p)
    add(bindings,hp,Path(__file__).resolve())
    save('quickman-actual-host-cpu',dict(
        status=h['status'],ROM_sha256=h['ROM_sha256'],original_source_sha256=h['source_original_sha256'],
        code_bytes=h['code_bytes'],retained_lease=h['retained_PRG_lease'],headroom=h['headroom_bytes'],
        root_checks='All frozen bindings and compact compiled-source ZIP members verified. Physical251CHR order correction retained; other parent CHR exact.',
        source_checks=['1520source updates/all535fields','300OAMcases','282foreignMain cases',
                       '160actualserial-input Main updates','65pause/resume updates','164actualISR cases',
                       'genuine source bonk plus native question-block response'],
        limits=['No native controller or cadence admission; actual active Main can exceed39KCPU.',
                'Source original audio/theme and native hit cadence remain open.',
                'Private WRAM successors are separate and not adopted.']),bindings)


if __name__=='__main__':
    rogue()
    arthur()
    quick()
