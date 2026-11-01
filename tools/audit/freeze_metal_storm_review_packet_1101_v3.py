"""Publish semantic Metal Storm source/proof, excluding lab code/PRG objects."""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[2]
LAB=ROOT/'build/metal-storm-component-1101-v2'
OUT=ROOT/'build/metal-storm-review-packet-1101-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
encode=lambda q:(json.dumps(q,indent=2)+'\n').encode('utf-8')

HANDOFF='''# Metal Storm publication packet v3

This packet publishes semantic actor source, original small body assets and
aggregate component receipts. It does not unlock Metal Storm or install a ROM.
There is no native host admission, IRQ/NMI/SMC safety proof, source audio port,
earned-upgrade qualification or native 1-1 traversal.

The external laboratory objects remain read-only in
`build/metal-storm-component-1101-v2`. They include the local selected-PRG
reproduction and compiled CPU-test arenas referenced by the receipts. Those
objects, their debug/object/symbol outputs and the old v2 source-proof ZIP are
intentionally absent from this publication packet. The original donor remains
`C:/NES/Metal Storm (USA).nes`; recover/reassemble it locally using the included
recipe and that user's donor, not a PRG snapshot distributed by this packet.

`manifest.json` records exact member hashes and the external v2 input hashes.
All original v2 receipt bindings were validated read-only before packaging.
No qualified v2 object or its bound source was modified or rebuilt.

The strongest results remain 480 legal original/private actor comparisons
(960 executions), original jump/gravity reversal, 208 source graphics contexts,
and pixel-exact agreement for the archived original native idle's581 opaque
pixels. Recorded external API effects are replayed at explicit boundaries;
their implementations remain host-adapter work.

The included integration notes are the immutable v2 notes. Their laboratory
`MsPointer=$00/$01` must become the actual native foregroundR0/R1=$03/$04
before host integration, followed by real IRQ/NMI/SMC and stack-depth tests.
The6,323-byte code arena and2KiB state image also require real resource grants.
Existing menu slot11/FmAlts&$02 remains pending until those steps are complete.

Use this corrected v3 ZIP for publication, not v2/source-proof.zip.
'''

def main():
    assert not OUT.exists(),'Use a fresh bounded publication root.'
    stage_path=LAB/'source-stage.json';stage=json.loads(stage_path.read_text())
    assert stage['passed']and not stage['native']and not stage['installed']
    checked={}
    for name,h in stage['bindings'].items():
        p=ROOT/name;assert sha(p)==h,p;checked[str(p.resolve())]=h
    receipts={}
    for name in ['assembly.json','CPU-controls.json','art.json']:
        q=json.loads((LAB/name).read_text());assert q['passed'];receipts[name]=q
        for name,h in q['bindings'].items():
            p=Path(name);assert sha(p)==h,p;checked[str(p.resolve())]=h
    assert sha(LAB/'source-proof.zip')==stage['source_proof_sha256']

    members={}
    def add(member,path):
        assert member not in members
        assert Path(member).suffix.lower()not in ['.o','.dbg','.lbl','.bin','.nes']
        members[member]=Path(path).read_bytes()
    # Explicit whitelist: no glob over the lab and no copied dependency tree.
    for name in ['original-actor.inc','portable-actor.inc','portable.s','portable.cfg']:
        add('source/'+name,LAB/'source'/name)
    for name in ['body.chr','body-preview.png','native-reference-idle.png']:
        add('assets/'+name,LAB/name)
    for name in ['assembly.json','CPU-controls.json','art.json']:
        add('proof/'+name,LAB/name)
    for name in ['metal_storm_cpu_1101_v2.py','prepare_metal_storm_source_1101_v2.py','recover_metal_storm_actor_1101_v2.py','check_metal_storm_actor_1101_v2.py','prepare_metal_storm_art_1101_v2.py']:
        add('tools/audit/'+name,ROOT/'tools/audit'/name)
    add('tools/audit/freeze_metal_storm_review_packet_1101_v3.py',Path(__file__))
    add('integration-v2.md',ROOT/'tools/reference/metal_storm_component_1101_v2.md')
    members['handoff.md']=HANDOFF.encode('utf-8')
    manifest=dict(passed=True,publication_packet=True,native=False,installed=False,menu_admitted=False,donor_sha256=stage['donor_sha256'],external_laboratory_root=str(LAB.relative_to(ROOT)).replace('\\','/'),external_v2_source_stage_sha256=sha(stage_path),external_v2_assembly_sha256=sha(LAB/'assembly.json'),external_v2_CPU_controls_sha256=sha(LAB/'CPU-controls.json'),external_v2_art_sha256=sha(LAB/'art.json'),validated_external_bindings=len(checked),excluded=['whole PRG snapshots','compiled code/bin outputs','object/debug/symbol files','old v2 source-proof.zip','native emulator run or installed ROM'],scope='Publication packaging only; unchanged v2 laboratory source/art evidence. No new behavior or host admission.',members={name:dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())for name,data in sorted(members.items())})
    members['manifest.json']=encode(manifest)
    assert len(members)<32 and sum(map(len,members.values()))<1_000_000
    OUT.mkdir();archive=OUT/'source-proof.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,data in sorted(members.items()):z.writestr(name,data)
    with zipfile.ZipFile(archive)as z:
        assert sorted(z.namelist())==sorted(members)
        for name,data in members.items():assert z.read(name)==data,name
        assert all(Path(name).suffix.lower()not in ['.o','.dbg','.lbl','.bin','.nes']for name in z.namelist())
        for name,record in manifest['members'].items():
            assert hashlib.sha256(z.read(name)).hexdigest()==record['sha256']
    # Guard the original qualified inputs across packaging too.
    for name,h in checked.items():assert sha(name)==h,name
    assert sha(stage_path)==manifest['external_v2_source_stage_sha256']
    (OUT/'manifest.json').write_bytes(members['manifest.json'])
    (OUT/'handoff.md').write_bytes(members['handoff.md'])
    result=dict(passed=True,native=False,installed=False,menu_admitted=False,publication_packet=True,source_proof_sha256=sha(archive),source_proof_bytes=archive.stat().st_size,source_proof_members=len(members),manifest_sha256=sha(OUT/'manifest.json'),external_v2_lab_unchanged=True,validated_external_bindings=len(checked),excluded_PRG_and_compiled_objects=True,actor_pairs=stage['actor_pairs'],portable_bytes_external_only=stage['portable_bytes'],art_contexts=stage['art_contexts'],CHR_bytes=stage['CHR_bytes'])
    (OUT/'source-stage.json').write_bytes(encode(result));print(json.dumps(result))

if __name__=='__main__':main()
