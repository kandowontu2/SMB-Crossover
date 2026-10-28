"""Freeze compact FF source component manifest; no build/native/shared edit."""
from pathlib import Path
import json,hashlib
from prepare_final_fantasy_component_v1 import ROOT,OUT,bind,sha
from prepare_final_fantasy_controls_v1 import HOST,EXPECTED
def main():
    audit=ROOT/'build/final_fantasy_source_assets_v1.json'
    assert sha(audit.read_bytes())=='f530f83a438ed366ffdd1776e59c9102386f3127a10ccd87856d9908dd115f4b'
    frozen=json.loads(audit.read_text())
    for row in frozen['owned']+[frozen['rogue_art_handoff_unchanged']]:
        assert bind(row['path'])==row,('frozen packet drift',row['path'])
    for ext,h in EXPECTED.items():assert sha(HOST.with_suffix('.'+ext).read_bytes())==h
    q=json.loads((OUT/'controls.json').read_text());assert q['passed']and not q['native']
    for row in q['outputs']+[q['sparse_candidate']]:assert bind(row['path'])==row
    source=[*sorted((ROOT/'src').glob('final_fantasy*')),ROOT/'chr/characters/final-fantasy.chr',
            ROOT/'tools/prepare_final_fantasy_component_v1.py',ROOT/'tools/prepare_final_fantasy_controls_v1.py',
            Path(__file__),ROOT/'docs/qa/final-fantasy-component-source-2026-10-28.txt']
    generated=[OUT/n for n in ['assets.json','controls.json','component.s','component.cfg','component.bin','component.lbl','component.dbg','art.bin','chr.bin']]
    # First draft errors retained compactly; no failed native/Flash oracle was run.
    negative=OUT/'draft-notes.json'
    negative.write_text(json.dumps(dict(native_failure=False,notes=[
        'Initial strict body RGB catalog rejected actual cyan sword colors; retained them as a separate authenticated layer, no flattening.',
        'Initial uncompressed ART4237B exceeded4KB; exact body grid compression reduced final ART3410B without dropping pixels.',
        'Initial drafts had missing host imports/long-branch and Python syntax errors; never a native/gameplay result.',
        'OAM+1/half-pixel bounds and shared-vs-instance animation clocks corrected before final frozen controls; no original VM golden claimed.',
        'Earlier61Bolt-part estimate included purple atlas guide pixels; final actual part census max53.',
    ]),indent=2)+'\n')
    refs=[audit,*[HOST.with_suffix('.'+e)for e in EXPECTED],
          ROOT/'tools/prepare_rogue_dawn_art_v1.py',ROOT/'tools/rogue_dawn_map_v1.py',ROOT/'tools/audit/verify_native_relocation.py',
          ROOT/'reference/crossover2/extracted/scripts/com/smbc/main/LevObj.as',
          ROOT/'reference/crossover2/extracted/scripts/com/explodingRabbit/display/CustomMovieClip.as',
          ROOT/'src/mmc5.s',ROOT/'src/metasprite_engine.s',ROOT/'src/reset.s']
    public=source+[OUT/'assets.json',OUT/'controls.json',negative]
    proof=dict(status='FROZEN standalone source component; host integration and native unqualified',
               raw_identity=22,menu_slot=21,class_order=['Fighter','WhiteMage','BlackMage','Thief'],
               parent=bind(HOST.with_suffix('.nes')),sparse_candidate=q['sparse_candidate'],
               native=False,canonical_edits=False,shared_edits=[],active_owned_processes=[],
               bounds=dict(CORE=['physical62/$3E',0xaa00,0xaa00+q['CORE_bytes']-1],
                           ART=['physical93/$5D A/B mirrored C/D',0xd000,0xd000+q['ART_bytes']-1],
                           CHR=[756,787],persistent=[0x5fc1,0x5fce],variant=0x5fef,active=[0x5c00,0x5c7f]),
               finite_controls=bind(OUT/'controls.json'),source_assets=bind(OUT/'assets.json'),
               reference_inputs=[bind(p)for p in refs],owned_sources=[bind(p)for p in source],
               generated=[bind(p)for p in generated+[negative]],
               public_review_files=[bind(p)for p in public],public_bytes=sum(p.stat().st_size for p in public),
               mandatory_integration=['intercept raw22 before all old indexed paths','actual enemy eligibility/HP damage/score consumer and genuine reuse notification',
                    'exact14x26/crouch bounds and native terrain/climb/spring/camera adapters','complete body/effect chunk loop and physical CHR epoch',
                    'world/pickup P2/optional ink P3/Star/transform palette composition','full shared caller/NMI/native raster/OAM/8sprite/campaign checks'],
               source_original_vs_adaptation_note=bind(ROOT/'docs/qa/final-fantasy-component-source-2026-10-28.txt'),
               commands=['python tools/prepare_final_fantasy_component_v1.py','python tools/prepare_final_fantasy_controls_v1.py','python tools/prepare_final_fantasy_handoff_v1.py'])
    (OUT/'handoff.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(handoff=bind(OUT/'handoff.json'),candidate=q['sparse_candidate']['sha256'],public_bytes=proof['public_bytes'])))
if __name__=='__main__':main()
