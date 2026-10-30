"""Expand Arthur's explicit archive member closure into the Git checkpoint."""
from pathlib import Path
import hashlib,json,zipfile
from checkpoint_roster_progress_1030_v2 import R,save,sha


if __name__=='__main__':
    o=R/'build/arthur-body-fair-v3'
    h=o/'handoff.json';c=o/'source-closure.json';z=o/'private-source-cpu.zip'
    assert sha(h)=='fc8b79c93dc3c036ef5ac4067b3c01f5327ee4bacc92621f0558627d8fdf40eb'
    handoff=json.loads(h.read_text());closure=json.loads(c.read_text())
    assert sha(c)==handoff['source_closure_sha256']
    assert sha(z)==handoff['source_archive_sha256']
    bindings=dict(handoff['bindings'])
    with zipfile.ZipFile(z)as archive:
        for name,d in closure['files'].items():
            p=R/name
            assert sha(p)==d==hashlib.sha256(archive.read(name)).hexdigest(),name
            bindings[str(p.resolve())]=d
    for p in [Path(__file__).resolve(),h,c]:bindings[str(p)]=sha(p)
    save('arthur-required-body-fair-source-closure',dict(
        status='PRIVATE_SOURCE_CLOSURE_PRESERVED_NATIVE_GRAPHICS_PASS_PERFORMANCE_HOLD',
        ROM_sha256=handoff['candidate_sha256'],
        original_archive_sha256=sha(z),archive_members_verified=len(closure['files']),
        note='Explicitly expanded original744memberfiles closure before filteredsourcearchive creation. Native checkpoint separately retains400controller result. Standard checkpoint filtering omits linked objects/debug/ROM/native ZIPs; original actual_linked_objects and source dependencies stay recorded for rebuild.',
        limits=['Current commonA79 overlapsjoint; no implicitsharedcomposition or RAM1grant.',
                'GraphicsPASS doesnotremove actual216lag/400frames performanceHOLD.']),bindings)
