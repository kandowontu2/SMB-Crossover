"""Authenticate actual2.02 Rush lineup; additive correction, no ROM/native work."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from current_ee115_shared_star_life_prepare_v1 import EXPECTED
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    root=R/'reference/crossover2';swf=root/'source.swf';asroot=root/'extracted/scripts/com/smbc'
    assert sha(swf)=='6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af'
    files=[asroot/'characters/MegaMan.as',asroot/'characters/base/MegaManBase.as',asroot/'pickups/Rush.as',asroot/'data/CharacterInfo.as']
    mega,base,rush,chars=[p.read_text()for p in files]
    assert sha(files[1])=='3aca147b666fe10c4f35f74307f3e8a690c29bb3bbc443f2cae4db063a1b7fdb'
    def declaration(text,name):
        q=re.search(r'\b'+name+r':(?:Array|Vector\.<String>)\s*=\s*(.+?);',text)
        assert q,name
        return q.group(1),text[:q.start()].count('\n')+1
    declarations={}
    for name in ['OBTAINABLE_UPGRADES_ARR','MUSHROOM_UPGRADES','SINGLE_UPGRADES_ARR','REPLACEABLE_UPGRADES_ARR','ICON_ORDER_ARR','AMMO_ARR']:
        text,line=declaration(mega,name);declarations[name]=dict(expression=text,line=line)
    for name in ['OBTAINABLE_UPGRADES_ARR','MUSHROOM_UPGRADES','SINGLE_UPGRADES_ARR','REPLACEABLE_UPGRADES_ARR']:
        assert 'MM_RUSH_JET'not in declarations[name]['expression']and'MM_MAN_RUSH_MARINE'not in declarations[name]['expression']
    assert 'MM_RUSH_COIL'in declarations['OBTAINABLE_UPGRADES_ARR']['expression']
    assert 'MM_RUSH_JET'in declarations['ICON_ORDER_ARR']['expression']and'MM_RUSH_JET'in declarations['AMMO_ARR']['expression']
    vector,line=declaration(base,'WEAPON_VEC_DEF');assert 'MM_RUSH_COIL'in vector and'MM_RUSH_JET'not in vector
    assert base.count('MM_RUSH_JET')==1 and 'case MM_RUSH_COIL:'in base and 'case MM_RUSH_JET:'not in base
    assert 'FL_FLIGHT'not in rush and 'private static const ST_EXIT:String = "exit";'in rush
    rom=R/'build/roster-20261028-fixes.nes';assert sha(rom)==EXPECTED
    b=scoped_load(rom);raw=b['raw'];loc=lambda n:location(b,n);adr=lambda n:address(b,n)
    assert raw[loc('InvItemCount')+1]==10
    owners=[]
    for n in ['MegaManRushAttack','MegaManRushBounce','SpecialWeapons::RushMotion','SpecialWeapons::RushFly','SpecialWeapons::RushFall']:
        p=loc(n);size=int(b['syms'][n].get('size','0'),0)
        owners.append(dict(symbol=n,pc=adr(n),bank=(p-16)//8192,declared_bytes=size,sha256=hashlib.sha256(raw[p:p+max(1,size)]).hexdigest()))
    out=R/'docs/qa/rush-2.02-lineup-correction-2026-10-28.json';assert not out.exists()
    z=dict(passed=True,source_only=True,native_run=False,ROM_sha256=EXPECTED,
           original_SWF_sha256=sha(swf),source_declarations=declarations,weapon_vector=dict(expression=vector,line=line),
           conclusion='Rush Jet is not an obtainable or selectable MegaMan2.02 upgrade. Jet/Marine names survive only in shared icon/ammo declarations; the concrete acquisition/replacement arrays and executable weapon vector/attack switch admit RushCoil only. Do not implement an invented Jet obligation.',
           matrix_addendum=dict(frozen_matrix='docs/qa/all37-powerup-native-coverage-2026-10-28.json',frozen_sha256='41168d1c642f9561e55e3d4ed17cc50b8acd14ff2a8d0ca6d1f420979a09f113',identities=['megaman','proto'],previous_label='RushJet (same Rush item, other ability)',corrected='NOT_APPLICABLE_TO_AUTHENTIC2.02_LINEUP',reason='Port variants share the same character1 inventory row. Existing earned RushCoil item/use is valid original-lineup coverage; no new Jet native cell required. Original matrix kept byte-exact.'),
           compiled_scope='Current SS_RUSH modes0/1/2/3/4 are fall/wait/Coil spring/exit animation/fly-away. Mode4 is departure, not player riding; prior nativeCoil already exercised all5 modes.',compiled_owners=owners,
           bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in [Path(__file__),swf,*files,rom,rom.with_suffix('.dbg'),R/'src/megaman_rush.s',R/'src/special_weapons.s',R/'tools/audit/current_mega_arsenal_prepare_v1.py']])
    out.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(report=str(out),sha256=sha(out),native_run=False)))


if __name__=='__main__':main()
