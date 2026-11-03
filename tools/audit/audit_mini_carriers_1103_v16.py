"""Rebind the finite upper3 source hole962..968 to the actual shared83 image."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_mini_private_owner_1103_v15 as M
import build_storage_guard_v1 as G
O=M.O;sha=M.sha


def main():
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=2,fresh=True)
    raw=M.BASE.read_bytes();assert sha(raw)==M.PIN
    paths={
        'dk':R/'build/dkjr-native-source-1102-v2/carrier-proposal-v13.json',
        'old':R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json',
        'prince':R/'docs/qa/checkpoints/2026-11-02/prince-resource-pool-v1/pool-proposal.json',
        'private':R/'build/prince-actor-1101-v1/writer-preservation.json',
        'loaders':R/'build/karnov-carrier-loader-bounds-1101-v5/loader-bounds.json',
        'smb3plus':R/'build/karnov-combat-carrier-design-1101-v3/design.json',
        'dkgrant':R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json',
        'current':R/'docs/qa/allocations/combined-owner-auth-1103-v116.json'}
    q={n:json.loads(p.read_text())for n,p in paths.items()}
    targets=set(M.CODE+[M.META,M.ART]);domains=dict(q['dk']['current_finite_domains'])
    # Retain the complete historical source storage ranges even though the
    # current compact SMB3 selector is narrower. No old over-approximate
    #832..1023 blanket reservation is treated as an actual consumer.
    for row in q['loaders']['workers']:domains[row['owner']+' exact original cold']=row['pages']
    domains['Benjamin retained cold']=list(range(901,915))
    domains['Historical SMB3Plus retained conservative emission']=list(range(969,1019))
    domains['Granted DK code/art']=list(q['dk']['proposed_code'])+list(q['dk']['proposed_art'])
    assert max(q['smb3plus']['SMB3Plus_pages'])<1019 and min(q['smb3plus']['SMB3Plus_pages'])==969
    assert not any(targets&set(v)for v in domains.values())
    tables=[]
    for row in q['dk']['current_table_bindings']:
        at=row['offset'];assert sha(raw[at:at+row['bytes']])==row['SHA256'],row['name'];tables.append(row)
    for name,row in q['prince']['current_table_proofs'].items():
        at=row['file_offset'];size=row.get('rows',row.get('bytes',0))
        assert sha(raw[at:at+size])==row['sha256'],name
        tables.append(dict(name=name,offset=at,bytes=size,SHA256=row['sha256']))
    # Current complete inherited writer instructions, with the ten moved
    # helper writes and four retired Arthur page883 writes counted honestly.
    direct=0;helpers=[];retired=[]
    helper=R/'build/wwf-helper-stable-1102-v2';hb=(helper/'proposed.bin').read_bytes();ht=(helper/'source.s').read_text();at=16+26*8192+0x800
    assert raw[at:at+len(hb)]==hb
    assert not any(x in ht for x in ['X5SetPhysicalChr','X5PublishChr','CurrentCHRBank','ChrPhysicalMap','SmChrBank'])
    for row in q['old']['unchanged_inherited_writers']:
        if Path(row['file']).suffix!='.nes':continue
        at=row['file_offset'];old=bytes.fromhex(row['old_bytes'])
        if raw[at:at+len(old)]==old:direct+=1;continue
        if row['segment']=='CROSSOVER_HELPERS'and row['source']['text']in ht:
            helpers.append(dict(source=row['source']['text'],rule=row['rule']));continue
        assert row['segment']=='ARTHUR_CACHE_EXEC'and (at-1048592)//1024==883,row
        retired.append(dict(old_offset=at,page=883,rule=row['rule']))
    assert direct==802 and len(helpers)==10 and len(retired)==4
    # The page883 legacy Arthur instructions were formally retired: genuine
    # Arthur descriptors publish868..880, DK now owns883 as private source.
    # Bind the actual replacement page to the current reviewed composition.
    layer=q['current']['reviewed_layers'][0]
    dkrows=[r for r in layer['patches']if 'physical_CHR'in r]
    assert {r['physical_CHR']for r in dkrows}==set(domains['Granted DK code/art'])
    for row in dkrows:
        at=row['file_offset'];assert sha(raw[at:at+row['bytes']])==row['after_SHA256']
    private=[]
    for row in q['private']['private_writer_bindings']:
        actual=[p for p in row['source_page_matches']if sha(raw[1048592+p*1024:1048592+(p+1)*1024])==row['source_chunk_SHA256']]
        assert actual,row;private.append(dict(segment=row['segment'],source_offset=row['source_offset'],pages=actual,SHA256=row['source_chunk_SHA256']))
    # Current cold worker bytes and typed descriptors remain exact. Future
    # Mini use is separate; this audit only closes all preexisting consumers.
    common=R/'build/bubble-bobble-source-1101-v1'
    for name,pc in [('common-split.bin',0xaf40),('common-split-map.bin',0xb9d6)]:
        data=(common/name).read_bytes();at=16+123*8192+pc-0xa000;assert raw[at:at+len(data)]==data
    assert q['current']['expected_candidate_SHA256']==M.PIN
    domains['Current shared Ex common descriptor']=list(range(728,736))
    domains['Current shared Bub common descriptor']=[301,305,337,362,363,440,819,666,441]
    assert not any(targets&set(v)for v in domains.values())
    preimages=[dict(page=p,file_offset=1048592+p*1024,bytes=1024,SHA256=sha(raw[1048592+p*1024:1048592+(p+1)*1024]))for p in sorted(targets)]
    result=dict(passed=True,proposal_only=True,resource_granted=False,ROM_written=False,
        current_ROM_SHA256=M.PIN,proposed_code=M.CODE,proposed_immutable=M.META,proposed_art=M.ART,preimages=preimages,
        exact_finite_domains=domains,current_table_bindings=tables,inherited_native_writer_instructions_exact=direct,
        source_relocated_helper_writers=helpers,retired_Arthur_writers=retired,inherited_private_writer_chunks_exact=private,
        current_DK_replacement_pages_exact=11,current_shared_cold_worker_exact=True,
        source_basis='Physical source-domain hole962..968: ContraForce original cold ends958; newly grantedDK959..961; historicalSMB3Plus emission starts969 and ends1018; Karnov1019..1023. FF893..900 andBenjamin901..914 explicitly retained. Genericlegacy publishesupper0; special/HUDupper≤2. Actual source tables and complete inherited writer ledger rebound to80d3; existing newPrince44/Bub9/DK11/Sh/Ex/Metal allocations remain occupied.',
        limitations=['Proposal only; root current-source/selector review and physical allocation required before page writes.','Publication/lagNMI protocol replay is separate; this does not assert native Mini render/scene/lifecycle.','Metadata967 must leave D25E..D2D0 coldcopier and D300..D400nativeattributes outside live animation tables.'],
        bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),Path(M.__file__),M.BASE,*paths.values(),helper/'source.s',helper/'proposed.bin',common/'common-split.bin',common/'common-split-map.bin',R/'tools/audit/audit_dkjr_carriers_1102_v13.py',R/'tools/audit/audit_karnov_loader_bounds_1101_v5.py',R/'tools/audit/design_karnov_combat_carrier_1101_v3.py']})
    (O/'carrier-audit-v16.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['passed','current_ROM_SHA256','proposed_code','proposed_immutable','proposed_art','inherited_native_writer_instructions_exact','current_DK_replacement_pages_exact','source_basis']}))


if __name__=='__main__':main()
