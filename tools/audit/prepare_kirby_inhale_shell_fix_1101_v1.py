"""Capture only current Kirby code/symbol witnesses for an isolated repair."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/kirby-inhale-shell-fix-1101-v1';LIVE=R/'build/karnov-host-resource-base-1101-v1/candidate.nes'
PIN='1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    O.mkdir(exist_ok=True);assert sha(LIVE)==PIN
    b=scoped_load(LIVE);assert hashlib.sha256(b['raw']).hexdigest()==PIN
    source_names=['kirby_weapons.s','kirby_core.s','kirby_dispatch.s','kirby_state.inc']
    tokens=set()
    for n in source_names:tokens.update(re.findall(r'\b[A-Za-z_]\w*\b',(R/'src'/n).read_text()))
    tokens.update(['GameLoop','GameCoreRoutine','PlayerEnemyCollision','SprObjectCollisionCore','ShellOrBlockDefeat','EnemyObjectsCore','PlayerCtrlRoutine','NonMaskableInterrupt','CurrentBank','CurrentBankC'])
    selected={n:s for n,s in b['syms'].items()if n in tokens or n.startswith(('KbWeapons::','KbBodyContact::','KbFamilyForEnemy::','KbInhaleVertical::','KbInhaleTargetY::'))}
    segids={s['seg']for s in selected.values()if'seg'in s and int(s['val'],0)>=0x8000 and(n:=b['segs'][s['seg']]).get('name','').startswith('"KIRBY')}
    chunks=[];records=[];blob=bytearray()
    for sid in sorted(segids,key=int):
        s=b['segs'][sid];start,size,at=[int(s[k],0)for k in['start','size','ooffs']]
        assert size<16384 and size>0
        data=b['raw'][at:at+size];assert len(data)==size
        records.append(dict(id=sid,name=s['name'].strip('"'),CPU=start,bytes=size,physical_PRG=(at-16)//8192,file_offset=at,witness_offset=len(blob),sha256=hashlib.sha256(data).hexdigest()));blob+=data
    assert len(blob)<65536
    (O/'current-kirby-code.bin').write_bytes(blob)
    references={n:dict(CPU=address(b,n),physical_PRG=(location(b,n)-16)//8192,bytes=b['raw'][location(b,n):location(b,n)+48].hex())for n in['KbWeapons','KbBodyContact','KbInhaleVertical','KbWeapons::Suction','KbWeapons::Spawn','KbWeapons::EnemyContacts','KbWeapons::CopyAttack','KbBodyDispatch']}
    call_order={}
    for name,count in [('GameLoop',125),('GameCoreRoutine',512),('ProcFireball_Bubble',768),('PlayerEnemyCollision',640)]:
        if name not in b['syms']:continue
        at=location(b,name);data=b['raw'][at:at+count]
        call_order[name]=dict(CPU=address(b,name),physical_PRG=(at-16)//8192,bytes=data.hex(),scope='Exact call-order snippet, not a complete standalone native routine.')
    bank_owners={}
    for sid,s in b['segs'].items():
        if 'ooffs'in s and 16<=int(s['ooffs'],0)<1048592 and (int(s['ooffs'],0)-16)//8192 in[72,74]:bank_owners[sid]=s
    q=dict(passed=True,ROM_sha256=PIN,historical_DBG_sha256=sha(LIVE.with_suffix('.dbg')),source_CPU=False,native=False,host_modified=False,
        segments=records,symbols=selected,all_segments={k:v for k,v in b['segs'].items()if k in segids},entry_witnesses=references,call_order_snippets=call_order,bank72_74_owners=bank_owners,
        canonical_sources={n:dict(path=str(R/'src'/n),sha256=sha(R/'src'/n))for n in source_names},
        scope='Compact actual1c Kirby code/symbol witness. No full ROM/DBG copy, no native run or repair claim.',
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),O/'current-kirby-code.bin',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py']})
    (O/'current-witness.json').write_text(json.dumps(q,indent=2)+'\n')
    assert sha(LIVE)==PIN
    print(json.dumps(dict(passed=True,ROM_sha256=PIN,code_bytes=len(blob),symbols=len(selected),segments=records,entry_witnesses=references)))
if __name__=='__main__':main()
