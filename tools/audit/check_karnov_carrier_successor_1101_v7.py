"""Bind the final ROM's exact changes to the old-owner carrier grant."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import check_karnov_combat_integrated_1101_v7 as T
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    j=T.T.BASE;old=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    grant=R/'build/karnov-carrier-final-1101-v6/carrier-grant.json'
    assert sha(grant)=='d012a79d81bd7fe45f1f6c288154ae002626b3c07001fe67e09459de213854cd'
    g=json.loads(grant.read_text());assert g['passed']and g['carrier_granted']and sha(old)==g['base_ROM_sha256']
    assert sha(j/'candidate.nes')==T.EXPECTED
    b=scoped_load(j/'candidate.nes');a=old.read_bytes();raw=b['raw']
    lo,hi=[location(b,n)for n in ['KrResidentBegin','KrResidentLimit']]
    allowed=[(lo,hi),(1048592+399*1024,1048592+407*1024),tuple(g['NES_file_byte_interval'])]
    veneer=location(b,'KrServiceVeneers');previous_target=a[veneer+1]|a[veneer+2]<<8
    for row in range(37):
        at=veneer+3*row
        assert a[at]==raw[at]==76
        assert a[at+1]|a[at+2]<<8==previous_target
        assert raw[at+1]|raw[at+2]<<8==address(b,'KrDispatch')
        # Only the existing table's destination operand may relocate.
        allowed.append((at+1,at+3))
    operands=[]
    for name,offset in [('InitScreen',12),('FmResolve::Native',4),('FmStartFlags',4)]:
        at=location(b,name)+offset-1
        # Exact native farcall template: only its target-low immediate moves.
        template=raw[at:at+15]
        assert template[0]==169 and template[2]==141 and template[5]==169 and template[7]==141
        assert template[10]==169 and template[12]in [32,76]
        assert template[2:5]==bytes([141,(address(b,'FarcallJmpTarget_SMC')+1)&255,1])
        assert template[7:10]==bytes([141,(address(b,'FarcallJmpTarget_SMC')+2)&255,1])
        assert template[11]==157 and template[13:15]==address(b,'FarCallCommon').to_bytes(2,'little')
        assert a[at:at+1]==raw[at:at+1]and a[at+2:at+15]==raw[at+2:at+15]
        allowed.append((at+1,at+2));operands.append(dict(owner=name,offset=offset,old=a[at+1],new=raw[at+1]))
    assert len(a)==len(raw)
    delta=[i for i,(x,y)in enumerate(zip(a,raw))if x!=y]
    outside=[i for i in delta if not any(l<=i<h for l,h in allowed)]
    assert not outside,('Unexpected other-owner mutation',outside[:20])
    assert raw[1048592+1019*1024:1048592+1019*1024+1280]==(j/'kr-combat.bin').read_bytes()
    q=dict(passed=True,ROM_sha256=T.EXPECTED,base_ROM_sha256=sha(old),carrier_granted=True,
           changed_bytes=len(delta),exact_allowed_intervals=allowed,three_native_farcall_operands=operands,
           genuine_JMP_veneer_rows=37,
           unchanged_other_owner_bytes=True,grant_sha256=sha(grant),
           scope='Old-owner resource grant is inherited only through exact byte preservation outside Karnov resident/kernel/carrier and three existing private-target-low relocations. Actual new-loader/Main/native qualification is separate.',
           bindings={str(p.resolve()):sha(p)for p in [Path(__file__),grant,j/'candidate.nes',j/'candidate.dbg',j/'kr-combat.bin']})
    (T.O/'carrier-successor.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
