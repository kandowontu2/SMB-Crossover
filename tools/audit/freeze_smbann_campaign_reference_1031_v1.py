"""Retain the exact ANN reference, stage comparison and new Doki donor request."""
from pathlib import Path
import hashlib,json,zipfile

R=Path(__file__).resolve().parents[2]
S=R/'build/smbann-original-source-1031-v1'
A=R/'build/smbann-campaign-audit-1031-v1'
D=R/'docs/qa/checkpoints/2026-10-31/smbann-campaign-reference-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert not D.exists()
    audit=json.loads((A/'source-audit.json').read_text());assert audit['passed']and audit['rebuilt_disk_byte_exact']
    for n,h in audit['bindings'].items():assert sha(n)==h,n
    donor=Path('C:/NES/fds/Yume Koujou - Doki Doki Panic (Japan) (DV 1).fds')
    assert sha(donor)=='937894f56890d4c90d63037b656b9aede82f913c8eb1411511b6f7d52594192a'
    request=R/'docs/qa/additional-campaign-and-doki-donors-2026-10-31.json'
    assert not request.exists()
    save(request,dict(status='ACTIVE_INCOMPLETE',installed_ready=74,installed_menu_identities=86,
         campaigns_requested=['SUPER MARIO BROS.','SUPER MARIO BROS 2J','ALL NIGHT NIPPON'],
         campaign_status='SMB1 installed. Private1/2J frontend passes source/native. ANN exact reference recovered; third frontend and full added campaign engines unfinished.',
         Doki_Doki_Panic=dict(path=str(donor),bytes=donor.stat().st_size,sha256=sha(donor),
             requested=['Imajin','Lina','Papa','Mama'],scope='Four original-character skins/identities for the SMB2 family, as specified in updated goal.',
             status='LOCATED_NOT_PORTED',menu_count_increase_installed=0),
         preserve_prior_choices=['Sonic3 remains the selected Genesis reference.',
                                 'Earlier Kamikaze correction still selects Kamikaze_V1_SMB1_Hack.nes sprites.',
                                 'All prior new roster identities and final1-1/every-powerup checks remain active.']))
    D.mkdir(parents=True)
    mapping={'5-3':'4-3','5-4':'2-4','6-4':'4-4','7-2':'6-2','7-3':'6-3','8-4':'8-4'}
    rows=[]
    for stage,ref in mapping.items():
        row=next(x for x in audit['routes']if x['stage']==stage)
        top=row['nearest_terrain_matches'][0]
        assert top['game']=='SMB2J'and top['stage']==ref
        rows.append(dict(ANN=stage,SMB2J_layout=ref,object_sequence_similarity=top['similarity'],
                         raw_terrain_byte_exact=top['raw_terrain_byte_exact'],header_exact=top['header_exact']))
    save(D/'requirements.json',dict(status='ACTIVE_INCOMPLETE',installed=False,
         choice='ALL NIGHT NIPPON',worlds=12,stages=48,world9=False,
         six_main_stage_layout_replacements=rows,
         other_changes='Full54-area ordered source catalog retains familiar-stage edits, pipe intros, enemies and distinct A-D variants. Similarity is a comparison aid; port the exact ANN streams.',
         required=['Third campaign choice after character selection with B return preserving identity.',
                   'Exact48 stages, bonus/pipe links and ANN-specific object protocol.',
                   'Original graphics, enemy/retainer substitutions and ending.',
                   'Original star/save and letter-world progression; no imported2J World9, poison or wind rules that ANN omits.',
                   'Native verification and full guest compatibility.']))
    refs=[Path(__file__),R/'tools/audit/audit_smbann_campaign_1031_v1.py',
          A/'source-audit.json',A/'changes-summary.json',S/'assemble.json',S/'link.json',
          S/'original/layout',S/'original/Makefile',S/'original/README.md',
          request,D/'requirements.json',*sorted((S/'original').glob('*.asm'))]
    members={p.relative_to(R).as_posix():sha(p)for p in refs}
    with zipfile.ZipFile(D/'source-reference.zip','x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in refs:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(D/'source-reference.zip')as z:
        for n,h in members.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    save(D/'source-members.json',members)
    save(D/'handoff.json',dict(passed=True,source_reference_only=True,installed=False,
         campaign_implemented=False,donor_sha256=audit['donor_sha256'],byte_exact=65500,
         source_repository=audit['source_repository'],source_commit=audit['source_commit'],
         source_credit=audit['source_credit'],worlds=12,numbered_stages=48,ordered_area_entries=54,
         archive_bytes=(D/'source-reference.zip').stat().st_size,archive_sha256=sha(D/'source-reference.zip'),
         bindings={**audit['bindings'],str(donor):sha(donor),**{str(p.resolve()):sha(p)for p in refs}}))
    lines=['# All Night Nippon campaign reference','',
        'The pinned source rebuilds all65,500 bytes of the supplied disk exactly. The actual tables contain48 numbered stages in worlds1-8/A-D and54 ordered areas including pipe intros; no World9 table is present.','',
        '| ANN stage | SMB2J layout |','| --- | --- |']
    lines += [f'| {a} | {b} |'for a,b in mapping.items()]
    lines += ['', 'These six main stages replace SMB1 layouts. Familiar stages and letter worlds also have changes, so their exact ANN streams need to be retained. The comparison catalog records terrain objects, headers and enemy streams separately; nearest-object similarity is not a rendered-level or gameplay equivalence claim.','',
              'ANN uses distinct graphics, rescues and an ending, retains star/save progression, and omits several2J features. This packet contains source and an integration ledger without ROMs or CHR. The campaign and third choice are not installed.']
    (D/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    owned=[p.relative_to(R).as_posix()for p in refs if p.is_relative_to(R/'tools')or p==request]
    owned += [p.relative_to(R).as_posix()for p in D.iterdir()if p.is_file()]
    owned.append((D/'owned-files.json').relative_to(R).as_posix())
    save(D/'owned-files.json',dict(files=sorted(set(owned))))
    print(json.dumps(dict(passed=True,installed=False,handoff_sha256=sha(D/'handoff.json'),archive_bytes=(D/'source-reference.zip').stat().st_size)))


if __name__=='__main__':main()
