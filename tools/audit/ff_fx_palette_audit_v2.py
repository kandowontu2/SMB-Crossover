"""Read-only source-cart FF palette requirements and legal action witnesses.

CPU-only declared fixtures, never a loader/admission/native claim. The actual
frozen source iterator and weapon instructions execute unchanged.
"""
from pathlib import Path
import collections, hashlib, itertools, json, sys, traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
import ff_joint_typed_controls_v1 as T
from check_tmnt_render_oa import address, location

H = T.H
P = R/'build/ff-joint-combat-hooks-1030-v5'
O = R/'build/ff-fx-palette-audit-v2'
H.O = P/'joint'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPECTED = 'c1aeff70d438788c1abbe542186c59ac10c5a7bac0f60fd53b0718b44d3d0a79'


def source(m, name, **kw):
    return H.C.run(m, name, raw=True, **kw)[0]


def data(b, name, size):
    pos = location(b, name)
    return list(b['raw'][pos:pos+size])


def pattern_indices(chr_data, page, tile):
    assert tile % 2 == 0
    block = chr_data[page*1024+tile*16:page*1024+tile*16+32]
    assert len(block) == 32
    counts = collections.Counter()
    for half in range(2):
        for y in range(8):
            lo, hi = block[half*16+y], block[half*16+8+y]
            for x in range(8):
                i = ((lo >> x) & 1) | (((hi >> x) & 1) << 1)
                if i: counts[i] += 1
    return counts


def render_requirements(b):
    m = T.base(b)
    raw = b['raw']
    prg_bytes = (raw[4] | ((raw[9] & 15) << 8))*16384
    chr_data = (R/'chr/characters/final-fantasy.chr').read_bytes()
    assert raw[16+prg_bytes+756*1024:16+prg_bytes+788*1024] == chr_data
    rows = []
    family_roles = {}
    for entry, face, outlines_off in itertools.product(range(158), [1, 2], [0, 1]):
        chunks = []
        for chunk in range(8):
            H.put(m, FfSlot=face, PlayerOutlinesOff=outlines_off)
            c = source(m, 'FfRenderChunk', a=entry, x=chunk, y=0)
            if not c.p & 1: break
            length = H.get(m, 'FfRenderBuffer')
            page = H.get(m, 'FfRenderPage')
            assert length % 4 == 0 and length <= 60
            roles = collections.defaultdict(collections.Counter)
            part_roles = collections.Counter()
            for offset in range(0, length, 4):
                start = address(b, 'FfRenderBuffer')+1+offset
                tile, attr, _, _ = m[start:start+4]
                role = attr & 3
                roles[role].update(pattern_indices(chr_data, page, tile))
                part_roles[role] += 1
            chunk_data = dict(chunk=chunk, page=page, parts=length//4,
                roles={str(k): dict(sorted(v.items())) for k, v in sorted(roles.items())},
                parts_by_role=dict(sorted(part_roles.items())))
            chunks.append(chunk_data)
        assert chunks
        family = ('body'+str(entry//36)) if entry < 144 else 'Fire' if entry < 147 else 'Ice_White' if entry < 152 else 'Bolt'
        for ch in chunks:
            for role, counts in ch['roles'].items():
                family_roles.setdefault(family, {}).setdefault(role, set()).update(int(i) for i in counts)
        rows.append(dict(entry=entry, face=face, outlines_off=outlines_off, family=family, chunks=chunks))
    H.exact(m)
    # Both facings preserve all palette requirements and optional-ink admission.
    for entry, off in itertools.product(range(158), [0, 1]):
        pair = [r['chunks'] for r in rows if r['entry'] == entry and r['outlines_off'] == off]
        assert len(pair) == 2 and pair[0] == pair[1]
    return dict(actual_source_iterator_calls=len(rows), source_CHR_equals_actual_cart=True,
        body_classes=['Fighter', 'White', 'Black', 'Thief'],
        aggregate_role_indices={k: {role: sorted(s) for role, s in v.items()} for k, v in family_roles.items()},
        rows=rows)


def state(m):
    at = address(m.bundle, 'FfProjectile')
    return [(m[at+s], m[at+s+1]) for s in [0, 12, 24]]


def lifetimes(b):
    rows = []
    for kind, phase in itertools.product([2, 3, 4], range(9)):
        m = T.base(b)
        H.put(m, FfSpell=kind, FfModerateClock=(phase*500)&255)
        m[address(b, 'FfModerateClock')+1] = (phase*500)>>8
        c = source(m, 'FfAllocate')
        assert c.p & 1
        ticks = 0
        while state(m)[0][0]:
            source(m, 'FfWeapons'); ticks += 1
            assert ticks < 40
        rows.append(dict(kind=kind, initial_clock=phase*500, lifetime_updates=ticks))
    assert max(r['lifetime_updates'] for r in rows if r['kind']==2)==27
    assert max(r['lifetime_updates'] for r in rows if r['kind'] in [3,4])==23
    return rows


def action_trace(b, variant, sequence, count=180, start_x=40):
    m = T.base(b)
    H.put(m, FfVariant=variant, FfPower=1, FfEarned=2, FfHealCharges=3,
        Player_X_Position=start_x, Player_PageLoc=0)
    rows=[]
    # Source action cadence with genuine fresh-edge calculation, followed by
    # genuine weapon update. Ground A cancels action as in real FfMovement.
    for tick in range(count):
        joy=sequence.get(tick, 0)
        H.put(m, SavedJoypadBits=joy)
        source(m, 'FfMovement')
        source(m, 'FfWeapons')
        shots=state(m)
        rows.append(dict(tick=tick, joy=joy, action=H.get(m,'FfAction'),
            age=H.get(m,'FfAge'), pose=H.get(m,'FfPose'), shots=shots))
        # This declared fixture supplies a flat supported floor after movement;
        # A-cancel witnesses intentionally use that ground contact next update.
        H.put(m, Player_State=0, Player_Y_Position=160, Player_Y_HighPos=1)
    H.exact(m)
    return rows


def legal_witnesses(b):
    cases={
      'black_fire_then_bolt': (2, {0:64, 49:72}),
      'black_fire_then_ice': (2, {0:64, 49:68}),
      'white_light_then_staff': (1, {0:68, 31:128, 32:64}),
      'white_heal_no_projectile': (1, {0:72}),
      'fighter_melee_only': (0, {0:64, 50:72, 100:68}),
      'thief_melee_only': (3, {0:64, 50:72, 100:68}),
      'black_bolt_then_ice_cancel': (2, {0:72, 31:128, 32:68}),
      'black_fire_fire_fire_cancel': (2, {0:64, 31:128, 32:64, 63:128, 64:64}),
    }
    out={}
    for name, (variant, sequence) in cases.items():
        rows=action_trace(b,variant,sequence,start_x=0 if name=='black_fire_fire_fire_cancel' else 40)
        coexist=[]
        for r in rows:
            kinds=[kind for kind,frame in r['shots'] if kind]
            if len(kinds)>1 or (kinds and r['action']==1):
                coexist.append(dict(tick=r['tick'], action=r['action'], kinds=kinds))
        out[name]=dict(variant=variant, input_pulses=sequence, initial_player_x=0 if name=='black_fire_fire_fire_cancel' else 40, coexisting_frames=coexist, rows=rows)
    assert any(set(r['kinds'])=={1,2} for r in out['black_fire_then_bolt']['coexisting_frames'])
    assert any(set(r['kinds'])=={1,3} for r in out['black_fire_then_ice']['coexisting_frames'])
    assert any(r['action']==1 and 4 in r['kinds'] for r in out['white_light_then_staff']['coexisting_frames'])
    assert not any(kind for r in out['white_heal_no_projectile']['rows'] for kind,frame in r['shots'])
    assert not any(kind for name in ['fighter_melee_only','thief_melee_only'] for r in out[name]['rows'] for kind,frame in r['shots'])
    assert not any({2,3} <= set(r['kinds']) for r in out['black_bolt_then_ice_cancel']['coexisting_frames'])
    assert any(len(r['kinds'])==3 for r in out['black_fire_fire_fire_cancel']['coexisting_frames'])
    return out


def world(b):
    palettes={}
    for n in ['WaterPaletteData','GroundPaletteData','UndergroundPaletteData','CastlePaletteData']:
        v=data(b,n,36);assert v[:3]==[63,0,32]
        palettes[n]={f'P{i}':v[19+i*4:23+i*4] for i in range(4)}
    donors=data(b,'QueueMegaManFacePalette::FacePalette',30)
    p3={str(i):donors[6+i*6+3:6+i*6+6] for i in range(4)}
    return dict(base_palette_packets=palettes, native_area_P3_visible=p3,
       mushroom_world_P2=[22,48,39], Bowser_P1_packet=data(b,'BowserPaletteData',8),
       native_P1_consumers=['green Koopa/Paratroopa','Piranha','HammerBro','Lakitu','Bowser','1UP','flagpole flag','fireflower lower parts'],
       native_P2_consumers=['mushroom','red Koopa/Paratroopa','coin','platform','floatey number','fireball/explosion','Podoboo','Spiny','Jumpspring'],
       native_P3_consumers=['Goomba','BuzzyBeetle','BulletBill','Blooper','hammer','debris'])


def main():
    O.mkdir(exist_ok=False)
    p=dict(passed=False, native=False, admitted=False, read_only_cart_and_sources=True,
        source_fixture_limits=['Legal fixed-class controller action witnesses; a declared flat-floor contact is supplied between updates.',
           'No campaign, physical-NMI, full-render cost, palette-ownership implementation, or admission claim.'])
    try:
        assert sha(H.O/'candidate.nes')==EXPECTED
        b=H.C.qualified(H.O/'candidate.nes')
        p['palette_rows']={n:data(b,n,16 if n in ['FfPaletteRed','FfPaletteBlue'] else 4)
           for n in ['FfPaletteRed','FfPaletteBlue','FfPaletteIce','FfPaletteBolt']}
        p['requirements']=render_requirements(b)
        print('source render requirements PASS',flush=True)
        p['lifetimes']=lifetimes(b)
        p['legal_witnesses']=legal_witnesses(b)
        print('legal action witnesses PASS',flush=True)
        p['world']=world(b)
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    paths=[Path(__file__), Path(T.__file__), Path(H.__file__), Path(H.C.__file__),
       H.O/'candidate.nes',H.O/'candidate.dbg',H.O/'ram3.bin',H.O/'ff-render.s',
       R/'src/final_fantasy_weapons.s',R/'src/final_fantasy_render.s',R/'src/final_fantasy_core.s',
       R/'src/final_fantasy_state.inc',R/'src/final_fantasy_art.inc',R/'chr/characters/final-fantasy.chr',
       H.O/'src/characters.s',H.O/'src/reset.s',H.O/'src/metasprite.s',H.O/'src/sprite_render.s']
    p['bindings']={str(f.resolve()):sha(f) for f in paths}
    target=O/('audit.json' if p['passed'] else 'negative-v1.json')
    target.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],path=str(target),error=p.get('error'))),flush=True)
    assert p['passed']


if __name__=='__main__':main()
