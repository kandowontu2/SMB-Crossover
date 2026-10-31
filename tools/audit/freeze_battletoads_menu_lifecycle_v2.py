"""Metadata-only successor: distinguish RAM3 image offsets from ROM offsets.

The original frozen v1 receipt/API is retained as a reporting negative. No
candidate/source/compiler output or previous receipt is changed.
"""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
P=R/'docs/qa/checkpoints/2026-10-31/battletoads-menu-lifecycle-v1'
O=R/'docs/qa/checkpoints/2026-10-31/battletoads-menu-lifecycle-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p,q):
    p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def main():
    assert not O.exists()
    assert sha(P/'handoff.json')=='3c3e22286a32fee04e5c1e12591c59362e8b31fe7dd7e3204fce5de2fb366da6'
    old=json.loads((P/'handoff.json').read_text())
    for n,h in old['bindings'].items():assert sha(n)==h,n
    O.mkdir(parents=True)
    api=json.loads((P/'row-and-cold-API.json').read_text())
    ram_names={r['target']['name'] for r in api['cache_rows']}|{'BtCacheServices','BtEnsure'}
    corrections=[]

    def correct(s):
        if s['name'] not in ram_names:return s
        before=dict(s)
        s=dict(name=s['name'],address=s['address'],storage='temporal selected RAM3 code',
               execution_raw_PRG_bank=3,temporal_RAM_bank=3,
               cache_image='joint/bt/cache.bin',cache_image_offset=s['file_offset'],
               source_carriers_CHR='919..<927; not executable ROM-bank aliases')
        assert 0<=s['cache_image_offset']<8192
        corrections.append(dict(old=before,corrected=s))
        return s

    api['symbols']=[correct(s) for s in api['symbols']]
    for row in api['cache_rows']:row['target']=correct(row['target'])
    assert all('raw_ROM_bank' not in row['target'] for row in api['cache_rows'])
    assert all(s.get('execution_raw_PRG_bank')==3 for s in api['symbols'] if s['name'] in ram_names)
    api['metadata_correction']='v1 generic helper incorrectly treated cache.bin segment offsets as NES file offsets; source/candidate/tests unchanged. Cache entries execute raw3. Genuine ROM callbacks retain their real physical bank/rawROM fields.'
    api['v1_reporting_negative_handoff']=sha(P/'handoff.json')
    write(O/'row-and-cold-API.json',api)
    write(O/'v1-reporting-negative.json',dict(
        classification='REPORTING_ONLY_INVALID_ROM_BANK_DERIVATION_FOR_RAM3_IMAGE_SEGMENTS',
        product_changed=False,original_frozen_packet_unchanged=True,
        original_API_sha256=sha(P/'row-and-cold-API.json'),corrections=corrections,
        root_and_shared_owner_notified_before_consumption=True))
    text='''BT menu/lifecycle metadata-only correction; source candidate35842285 exact

Frozen v1 API derived a ROM bank from DBG ooffs for RAM3 image segments. Those
offsets are into cache.bin, not the NES PRG payload. The corrected API explicitly
labels raw3 execution and image offsets for all cached workers. ROM loader and
cold callbacks keep true ROM-bank fields. No source, build output, tests or old
receipt changed. V1 and its reporting negative remain in the source archive.

The full inherited menu/lifecycle/source controls and limitations are unchanged:
BT remains pending actual shared mixed-cold/parser/Main and native qualification.
Installed f56 three Peach constants must still be genuinely composed. Use this
row-and-cold-API.json rather than the original v1 symbol report.
'''
    (O/'README.txt').write_text(text,encoding='utf-8')
    manifest=json.loads((P/'source-members.json').read_text())
    added=[Path(__file__),O/'row-and-cold-API.json',O/'v1-reporting-negative.json',O/'README.txt',P/'handoff.json']
    for p in added:manifest[p.relative_to(R).as_posix()]=sha(p)
    archive=O/'source-and-controls.zip'
    with zipfile.ZipFile(P/'source-and-controls.zip') as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as dst:
        for n in src.namelist():dst.writestr(n,src.read(n))
        for p in added:dst.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==len(manifest)
        for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    write(O/'source-members.json',manifest)
    q={k:v for k,v in old.items() if k!='bindings'}
    q.update(status='FROZEN_BT_MENU_LIFECYCLE_SOURCE_CORRECT_RAM3_API_NO_UNLOCK',
             metadata_only_successor=True,source_archive_members=len(manifest),
             source_archive_bytes=archive.stat().st_size,source_archive_sha256=sha(archive),
             predecessor_handoff=sha(P/'handoff.json'))
    q['bindings']=dict(old['bindings'])
    for p in added+[archive,O/'source-members.json']:
        q['bindings'][str(p.resolve())]=sha(p)
    write(O/'handoff.json',q)
    for n,h in q['bindings'].items():assert sha(n)==h,n
    print(json.dumps(dict(status=q['status'],handoff_sha256=sha(O/'handoff.json'),
                          bindings=len(q['bindings']),members=len(manifest),archive_bytes=archive.stat().st_size)))


if __name__=='__main__':main()
