"""Read-only exact-ROM/linked-segment allocation proposal. Never allocates."""
from pathlib import Path
import re,json,hashlib
import dragon_power_map_v1 as D
ROOT=D.ROOT
INPUTS=[('sunny-integrated-final','55e874822160c3ab20f9ccfbca8b46cfe3b71c00bc4466a9fa8c5789bf7c0217'),
        ('roster-expansion-mac-pipe-corner-v3','33d2c7a7bf58aa040f2911d44f1d59dddb4c9b40b3e8727334cf46db74915f97'),
        ('celeste-host-final','83db8bdf74dddc4055a52f5ec12526dcddc7a2fe418f24c3e9e1d5252fb6c9e0')]
PROPOSALS=[('CORE',86,0xa800,0xc000),('ART',85,0xc900,0xd900),('AUDIO_OPTIONAL',96,0xa980,0xc000)]
def segs(p):
    out=[]
    for line in p.open():
        if not line.startswith('seg\t'):continue
        d=dict(re.findall(r'(\w+)=("[^"]*"|[^,\r\n]+)',line))
        if 'ooffs'in d and int(d['size'],0):
            out.append(dict(id=int(d['id']),name=d['name'].strip('"'),start=int(d['start'],0),
                            bytes=int(d['size'],0),offset=int(d['ooffs'],0)))
    return out
def binding(p):return D.binding(ROOT/p if isinstance(p,str)else p)
def main():
    rows=[]
    for name,expected in INPUTS:
        p=ROOT/'build'/f'{name}.nes';dbg=p.with_suffix('.dbg');r=p.read_bytes();assert D.digest(r)==expected
        prg=r[4]*16384;ss=segs(dbg);spans=[]
        for role,bank,a,b in PROPOSALS:
            off=16+bank*8192+(a&8191);end=off+b-a
            collisions=[s for s in ss if s['offset']<end and s['offset']+s['bytes']>off]
            assert not collisions,(name,role,collisions)
            assert r[off:end]==bytes([255])*(b-a),(name,role,'nonFF')
            prior=[s for s in ss if s['offset']>=16+bank*8192 and s['offset']+s['bytes']<=off]
            spans.append(dict(role=role,bank=bank,bank_hex=f'{bank:02X}',cpu_start=f'{a:04X}',
                cpu_end_exclusive=f'{b:04X}',bytes=b-a,sha256=D.digest(r[off:end]),unallocated_by_linked_segments=True,
                all_FF=True,preceding_segments=prior))
        off=16+prg+788*1024;end=off+8192
        cc=[s for s in ss if s['offset']<end and s['offset']+s['bytes']>off]
        assert not cc and r[off:end]==bytes(8192),(name,'CHR not empty')
        rows.append(dict(rom=binding(p),dbg=binding(dbg),spans=spans,
            CHR_proposal=dict(pages=list(range(788,796)),bytes=8192,all_zero=True,linked_segment_collisions=cc,
                              sha256=D.digest(r[off:end]),publication_upper=3)))
    art=(ROOT/'src/tmnt_art.inc').read_text();part=art.split('TnBodyChr:',1)[1].split('TnHealthTiles:',1)[0]
    vals=[int(v)for line in part.splitlines()if '.byte'in line for v in line.split('.byte',1)[1].split(',')]
    assert len(vals)==99 and min(vals)==92 and max(vals)==114
    # Every legal body lookup supplies high2. Two physical1KB pages form a2KB window.
    tmnt=set(p for v in vals for p in [512+v,513+v])|{628,629}
    assert not tmnt&set(range(788,796))
    refs=['smb1base-mmc5-expanded.cfg','src/x5_bounce.s','src/cv3_art.inc','src/mike_jones.s',
          'src/mike_jones_core.s','src/mike_jones_motion.s','src/mike_jones_pickups.s','src/mike_jones_dispatch.s',
          'src/mike_jones_render.s','src/mike_jones_weapons.s','src/tmnt.s','src/tmnt_state.inc','src/tmnt_draw.s',
          'src/tmnt_art.inc','src/tmnt_equipment_draw.s','src/parodius_adapter.s','src/parodius_native.s',
          'src/roster_audio.s']
    source_refs=[binding(p)for p in refs]
    # This snapshot is a source-role audit, not a claim these mutable source files
    # produced all three immutable ROMs. Linked segment+ROM evidence is separate.
    j=dict(status='READ_ONLY_FEASIBLE_SPLIT_PROPOSAL_NOT_RESERVED_NOT_IMPLEMENTED',
        frozen_source_audit=binding('build/dragon-power-source-v1/handoff.json'),inputs=rows,
        source_consumer_snapshot=source_refs,
        consumer_findings=[
            'CORE86: X5_BOUNCE emitted extent plus gap independently checked in all3DBGs; x5_bounce source has direct local/farcall routes, no indirect JMP or incbin into the proposed tail. Existing padding is retained, not reclaimed.',
            'ART85: current CV3_GFX_85 is data records emitted by cv3_art.inc; all named linked segments end beforeC900 in all3DBGs. Append separate segment, retain all original record/pointer bytes.',
            'AUDIO96: existing MIKE_CORE extent checked independently; new audio is a separate append-only segment. BankA restore/shadow and all old public labels are future implementation gates.',
            'CHR788..795: zero and not covered by emitted segment in all3ROMs. Current cfg TMNT_CHR_TAIL is fill-only with no loaded segment; tmnt.s emits only its64KB TMNT_CHR lower allocation. Legal99body entries publish upper2, pages604..627, equipment628/629; none reads proposed tail.',
            'CHR FF756..787 and Goku788..795 remain disjoint; no allocation or cfg edits made. Other pending future owners need ROOT approval before any link.',
            'RAM5FD0..DB is only an identity-owned overlay proposal. Parodius initialization clears5F00..DF, while its native history5F40..BF and4-byteCapAnim5FDC..DF are not overlap-free global flags. Raw24 admission and genuine lifecycle initialization mandatory.',
            'Existing RgAudioZp160 is a potential exclusive audio-owner slab, not approved free global RAM; all foreign owner dispatch/reset and borrowed foregroundZP must be proved in actual adapter.'
        ],tmnt_body_table=dict(entries=len(vals),low_min=min(vals),low_max=max(vals),physical_pages=sorted(tmnt)),
        reduced_plan=dict(CORE_bytes=6144,ART_bytes=4096,AUDIO_optional_bytes=5760,CHR_bytes=8192,
            active_RAM_bytes=128,persistent_proposal='5FD0..5FDB12B, exclusively raw24-owned; no global admission flag',
            audio_state_proposal='132B within160B owner slab only after actual ownership/borrow proof',
            source_projection='Translate required original side-view routines, not original world/NPC/camera loops; separately declared overhead weapon adaptations only if approved.',
            estimated_original_audio_bytes=5086,audio_adapter_headroom=674,
            limits='Budgets are not assembled fit/cost proof. Stop/report if authentic closure plus safe adapter exceeds span; no stream/voice/channel/sample suppression or silent spill.'),
        excluded_ROOT_reservations=['FF62AA00..BFFF/ART93B000..BFFF','Celeste98B000..BDD7/81BB10..C000',
            'Rogue124B000..BFFF+AUXAE00..AFFF','ProposedRogueHost95A600..BFFF','Possible94DF50..DFFF'],
        tool=binding(Path(__file__)))
    p=ROOT/'build/dragon-power-allocator-v1.json';p.write_text(json.dumps(j,indent=2)+'\n')
    print(json.dumps(dict(output=binding(p),core=6144,art=4096,audio_optional=5760,CHR=8192,status=j['status']),indent=2))
if __name__=='__main__':main()
