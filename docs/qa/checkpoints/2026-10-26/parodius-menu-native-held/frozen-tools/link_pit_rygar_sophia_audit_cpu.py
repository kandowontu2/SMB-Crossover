"""Bounded actual-CPU audit, frozen ROM inputs and isolated legal arenas.

No Mesen, native input route, interrupt/PPU/audio timing, or campaign claim.
The crowded Sophia arena establishes the allocation defect, not its natural
controller reachability; that remains a native integration requirement.
"""
from pathlib import Path
import argparse, hashlib, itertools, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load, Memory, address, location
from verify_native_relocation import NesMPU


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def scoped_load(path):
    b=load(path); scopes={}; symbols=[]
    for line in path.with_suffix('.dbg').read_text().splitlines():
        if not line.startswith(('scope\t','sym\t')):continue
        d=dict(x.split('=',1) for x in line.split('\t',1)[1].split(',') if '=' in x)
        if line.startswith('scope\t'):scopes[d['id']]=d
        elif 'val' in d:symbols.append(d)
    def scope_name(i):
        s=scopes.get(i,{})
        parts=([scope_name(s['parent'])] if 'parent' in s else [])+[s.get('name','').strip('"')]
        return '::'.join(p for p in parts if p)
    for d in symbols:
        prefix=scope_name(d.get('scope'))
        name=d['name'].strip('"')
        b['syms'][prefix+'::'+name if prefix else name]=d
    return b


class Arena:
    def __init__(self, bundle, char):
        self.b = bundle
        self.m = Memory(bundle)
        self.put(SelectedCharacter=char, CrossoverBehaviorVersion=1,
                 PlayerStatus=1, OperMode=1, GameEngineSubroutine=8,
                 Player_Y_HighPos=1, Player_X_Position=96, Player_PageLoc=1,
                 Player_Y_Position=160, PlayerFacingDir=1,
                 ScreenLeft_PageLoc=1, DisableScreenFlag=1)

    def set(self, name, value, i=0):
        self.m[address(self.b, name)+i] = value

    def get(self, name, i=0):
        return self.m[address(self.b, name)+i]

    def put(self, **values):
        for n, v in values.items(): self.set(n, v)

    def array(self, name, values):
        for i, v in enumerate(values): self.set(name, v, i)

    def invoke(self, name, a=0, x=0, y=0):
        s = self.b['syms'][name]; g = self.b['segs'][s['seg']]
        bank = (int(g['ooffs'], 0)-16)//8192
        pc = address(self.b, name); window = (pc-0x8000)//8192
        self.m.page(window, bank)
        if window in (1, 2):
            self.set('CurrentBank' if window == 1 else 'CurrentBankC', bank|128)
        self.m.writes = []
        c = NesMPU(memory=self.m, pc=pc)
        c.a, c.x, c.y, c.p, c.sp = a, x, y, 0x30, 0xfd
        c.stPushWord(0x5aff)
        trace = []
        for _ in range(100000):
            if c.pc == 0x5b00:
                assert c.sp == 0xfd
                return c, trace
            before = len(self.m.writes); at = c.pc
            bank_now = self.m.banks[(at-0x8000)//8192] if at >= 0x8000 else -1
            c.step()
            trace += [dict(pc=at, bank=bank_now, address=p, value=v)
                      for p, v in self.m.writes[before:]]
        raise AssertionError(('CPU timeout', name, hex(c.pc), self.m.banks))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--expect-fixed', action='store_true')
    a = p.parse_args(); a.output.mkdir(exist_ok=False, parents=True)
    b = scoped_load(a.rom)
    proof = dict(ROM_sha256=sha(a.rom), script_sha256=sha(__file__),
                 scope=__doc__, checks={}, passed=False)
    value = lambda n, i=0: b['raw'][location(b, n)+i]
    # Authenticated historical web engines. Pit/Rygar are custom additions.
    refs = [ROOT/'reference/crossover/super-mario-crossover.swf',
            ROOT/'reference/crossover2/source.swf',
            Path('C:/NES/Rygar (USA).nes'),
            Path('C:/NES/Zelda II - The Adventure of Link (USA).nes')]
    proof['reference_sha256'] = {str(q):sha(q) for q in refs}
    assert sha(refs[1]) == '6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af'
    assert sha(refs[2]) == '965330fed9f5b8492452f3b53084752e83b7f899a1f88f3c475ece2fde6f9231'
    assert sha(refs[3]) == '9fca03064a5113e6a92f550d9f42bac9ac1ae248a84df1f653d7cd7f76a1803d'
    # Native table layout, compared to pinned 2.02 declaration values.
    for char, costs, initial, maxima in [
        (4, [0,1,1,0,0,0,0], [0,5,5,0,0,0,0], [0,20,20,0,0,0,0]),
        (11,[0,3,1,1,0,0,0,0], [0,15,5,8,0,0,0,0], [0,60,20,8,0,0,0,0])]:
        assert value('InvItemCount',char) == len(costs)-1
        for item in range(len(costs)):
            i = 16*char+item
            assert value('InvCosts',i) == costs[item]
            assert value('InvInitialAmmo',i) == initial[item]
            assert value('InvMaxAmmo',i) == maxima[item]
    proof['checks']['link_sophia_source_ammo_tables'] = dict(passed=True, entries=15)

    # Actual Diskarmor positions in body-centered coordinates, matching native
    # controller/OAM measurements. Powered reach is an intentional adaptation.
    rows = []
    for tier, face, crouch, xpos, page in itertools.product(range(3), [1,2], [0,1], [0,96,250], [0,1]):
        q = Arena(b,7)
        q.put(PlayerStatus=tier, PlayerFacingDir=face, RgCrouch=crouch,
              Player_X_Position=xpos, Player_PageLoc=page, ScreenLeft_PageLoc=page,
              ScreenLeft_X_Pos=xpos, RgSlot=9, XgDiskReach=20)
        q.set('RgShotType',2,9); q.set('RgShotDir',face,9)
        maximum=[40,64,88][tier]
        sequence=list(range(24,maximum+1,4))+list(range(maximum-4,19,-4))
        observed=[]
        for reach in sequence:
            q.invoke('ExpandedWeapons::MoveShot')
            assert q.get('RgShotType',9)==2
            actual=q.get('RgShotX',9)+256*q.get('RgShotPage',9)
            center=xpos+256*page+8
            want=(center+(reach if face==1 else 2-reach)) & 65535
            assert actual==want,(tier,face,crouch,reach,actual,want)
            assert q.get('RgShotY',9)==160+(15 if crouch else 8)
            observed.append((actual-center+32768)%65536-32768)
        q.invoke('ExpandedWeapons::MoveShot')
        assert q.get('RgShotType',9)==0 and q.get('RgShootPose')==0
        rows.append(dict(tier=tier,face=face,crouch=crouch,x=xpos,page=page,centers=observed))
    (a.output/'rygar-disk.json').write_text(json.dumps(rows,indent=2)+'\n')
    proof['checks']['rygar_native_disk_and_adapted_reach'] = dict(passed=True, cases=len(rows))

    count=0
    poses=[value('ExpandedWalkPose::Cycle',i) for i in range(3)]
    for face in [1,2]:
        q=Arena(b,7);q.set('PlayerFacingDir',face)
        for i in range(63):
            c,_=q.invoke('ExpandedWalkPose')
            assert c.a==poses[(i//7)%3]
            count+=1
        q.set('PlayerFacingDir',3-face)
        c,_=q.invoke('ExpandedWalkPose');assert c.a==poses[0]
        count+=1
    proof['checks']['rygar_three_native_walk_frames_seven_updates'] = dict(passed=True,cases=count)

    # Empty authored block buffers, complete in-bounds player position; actual
    # map probes run, rather than a stub pretending every roof is clear.
    count=0
    for tier, state, wet, down, fuel in itertools.product(range(3),[0,1,3],[0,1],[0,4],[0,1,60]):
        q=Arena(b,6)
        q.put(PlayerStatus=tier,Player_State=state,MmUnderwater=wet,
              SavedJoypadBits=down,A_B_Buttons=128,XgPitFuel=fuel,XgPitFlight=1,
              XgGravity=1)
        q.invoke('PitFlightUpdate')
        active=state==1 and tier==2 and not wet and not down and fuel>0
        assert q.get('XgPitFlight')==int(active)
        assert q.get('XgPitFuel')==(60 if state==0 else fuel-int(active))
        if active: assert [q.get('MmVY',i) for i in range(3)]==[0,128,254]
        count+=1
    q=Arena(b,6)
    q.put(PlayerStatus=2,Player_State=1,A_B_Buttons=128,XgPitFuel=60,XgPitFlight=1)
    for _ in range(60): q.invoke('PitFlightUpdate')
    assert q.get('XgPitFuel')==0
    q.invoke('PitFlightUpdate'); assert q.get('XgPitFlight')==0
    proof['checks']['pit_custom_flight_gates_recharge_and_duration'] = dict(passed=True,cases=count+61)

    # Both flight phase IDs deliberately bind the complete existing native
    # wing/body pose, including bow variants. There is no extra painted wing.
    count=0
    for tier, face, (fly,base) in itertools.product(range(3),['Left','Right'],[
        ('FLAP1','JUMP'),('FLAP2','JUMP'),('FLAPSHOT1','JUMPSHOOT'),
        ('FLAPSHOT2','JUMPSHOOT'),('FLAPUP1','JUMPUP'),('FLAPUP2','JUMPUP')]):
        dest=tier*address(b,'XG_POSE_COUNT')+address(b,'XG_POSE_'+fly)
        origin=tier*address(b,'XG_POSE_COUNT')+address(b,'XG_POSE_'+base)
        for suffix in [face+'Lo',face+'Hi','Banks']:
            assert value('XgPIT'+suffix,dest)==value('XgPIT'+suffix,origin)
        count+=1
    proof['checks']['pit_flight_uses_existing_complete_native_wing_body_records'] = dict(passed=True,cases=count,
        limitation='Each pair aliases the same existing native body, so toggling logical phase does not animate separate wing pixels.')

    # Source-authenticate the numeric tables independently from the original
    # local cartridge bytes, then execute current packed levels and casting.
    refjson=ROOT/'build/verification/zelda2-link-candidate-agent/original-source-authentication/native-ranges.json'
    auth=json.loads(refjson.read_text()); original=refs[3].read_bytes()
    for table,d in auth['tables'].items():
        start=16+d['bank']*16384+(int(d['cpu'],0)&0x3fff)
        native=original[start:start+len(d['values'])]
        assert hashlib.sha256(native).hexdigest()==d['sha256']
        assert list(native)==d['values']
        assert bytes(value(table,i) for i in range(len(native)))==native
    count=0
    for attack,magic,life in itertools.product(range(8),repeat=3):
        q=Arena(b,4)
        q.put(Z2LevelsHi=128)
        for cat,level in enumerate([attack,magic,life]):q.invoke('Z2SetLevel',a=level,x=cat)
        for cat,level in enumerate([attack,magic,life]):
            c,_=q.invoke('Z2GetLevel',a=cat);assert c.a==level;count+=1
        assert q.get('Z2LevelsHi')&128
    cast=0
    for spell,magic,delta,learned,same in itertools.product(range(8),range(8),[-2,-1,0,1],[False,True],[False,True]):
        cost=auth['tables']['SpellCosts']['values'][spell*8+magic]
        q=Arena(b,4)
        q.put(Z2LevelsLo=magic*8,Z2LevelsHi=128,Z2Mp=cost+delta,
              Z2LearnedSpells=255 if learned else 0,
              Z2Selection=((spell+1)*16 if same else 0))
        c,_=q.invoke('Z2TryCast',a=spell)
        expected=learned and not same and delta>=-1
        assert bool(c.p&1)==expected
        assert q.get('Z2Mp')==(max(0,delta) if expected else cost+delta)
        cast+=1
    proof['checks']['zelda2_authenticated_numeric_tables_packed_levels_casting'] = dict(passed=True,
        authenticated_tables=len(auth['tables']),packed_get_cases=count,cast_cases=cast,
        source_manifest_sha256=sha(refjson),scope='No terrain, body, moving-platform, pause visuals, audio, or full spell world-effect claim.')

    songs=[]
    for label,base in [('area',7),('event',7)]:
        prefix='XgArea' if label=='area' else 'XgEvent'
        for i in range(7):
            songs.append((value(prefix+'Banks',base+i),value(prefix+'Lo',base+i)+256*value(prefix+'Hi',base+i)))
    # Native bit-index order is normal/water/underground/castle/cloud/intro/
    # star. The pipe bonus reuses underground; event index6 reuses star/hurry.
    native_unique=set(songs[:7])
    assert len(set(songs[:6]))==6 and len(native_unique)==7 and songs[6]==songs[13]
    proof['checks']['rygar_native_song_selection_variants'] = dict(passed=True,
        unique_area_songs=6,unique_with_star=7,mapped_pointers=songs,
        scope='Bound source playlist/mapped pointers, not a new waveform, decoder-loop, or timing test.')

    # Isolated real input-handler counterexample: no active standard missiles,
    # four homing missiles and up to six short cannon-impact actors. Impact
    # actors legally have type6/positive impact countdown but retain pool slots.
    rows=[]
    for free, face, up in itertools.product(range(11),[1,2],[0,8]):
        q=Arena(b,11)
        q.put(InvFresh=32,PlayerFacingDir=face,SavedJoypadBits=up)
        q.set('InvOwnedLo',3,11);q.set('InvSelected',1,11);q.set('InvAmmo',15,177)
        for i in range(10-free):
            q.set('RgShotType',45 if i<4 else 6,i)
            q.set('RgShotImpact',0 if i<4 else 10,i)
        before=[q.get('RgShotType',i) for i in range(10)]
        _,trace=q.invoke('RemainingWeapons::SophiaInput')
        made=sum(q.get('RgShotType',i)==44 and before[i]==0 for i in range(10))
        spent=15-q.get('InvAmmo',177)
        bad=free<3 and (made!=0 or spent!=0)
        if a.expect_fixed:
            assert not bad,(free,face,up,made,spent)
        else:
            assert bad==(free<3)
        if free>=3:assert (made,spent)==(3,3)
        wrong=next((t for t in trace if t['address']==address(b,'InvAmmo')+177 and t['value']==12),None) if bad else None
        rows.append(dict(free_slots=free,face=face,up=bool(up),spawned=made,spent=spent,
                         defect=bad,first_wrong_write=wrong))
    (a.output/'sophia-triplet-allocation.json').write_text(json.dumps(rows,indent=2)+'\n')
    proof['checks']['sophia_atomic_triplet'] = dict(passed=not any(r['defect'] for r in rows),
        cases=len(rows),defect_cases=sum(r['defect'] for r in rows),
        natural_reachability='Not established by native controller playback. Legal isolated actor states; a native wall/firing stress scene is required before adoption.')
    proof['passed']=all(c['passed'] for c in proof['checks'].values())
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))
    return 0 if a.expect_fixed or not proof['passed'] else 0


if __name__=='__main__':raise SystemExit(main())
