"""Validate and publish three compact source packets, without ROM admission."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/parallel-source-review-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def bindings(q):
    for name,h in q.get('bindings',{}).items():
        p=Path(name);p=p if p.is_absolute()else R/p
        assert sha(p)==h,p


def packet(p,index):
    with zipfile.ZipFile(p)as z:
        q=json.loads(z.read(index));q=q.get('members',q)
        for name,info in q.items():
            h=info['sha256']if isinstance(info,dict)else info
            assert hashlib.sha256(z.read(name)).hexdigest()==h,(p,name)
        assert not any(n.lower().endswith(('.nes','.o','.dbg'))for n in z.namelist())
        assert all(z.getinfo(n).file_size<8192 for n in z.namelist()if n.lower().endswith('.bin'))
    return dict(sha256=sha(p),bytes=p.stat().st_size,members=len(q)+1)


def main():
    assert not O.exists()or not any(O.iterdir());O.mkdir(exist_ok=True)
    tasks=[('metal-storm-original-component-v3','metal-storm-review-packet-1101-v3','source-proof.zip','manifest.json',['source-proof.zip','source-stage.json','manifest.json','handoff.md']),('shinobi-original-component-v2','shinobi-component-1101-v2','source-proof.zip','packet-manifest.json',['source-proof.zip','handoff.json']),('excitebike-original-component-v2','excite-prince-component-1101-v2','source-and-proof.zip','component-file-hashes.json',['source-and-proof.zip','handoff.json'])]
    rows={}
    for label,root,archive,index,names in tasks:
        p=R/'build'/root;row=packet(p/archive,index)
        if label.startswith('metal'):
            q=json.loads((p/'source-stage.json').read_text());assert q['passed']and q['source_proof_sha256']==row['sha256']
            lab=R/'build/metal-storm-component-1101-v2';bindings(json.loads((lab/'source-stage.json').read_text()))
            for n in ['assembly.json','CPU-controls.json','art.json']:bindings(json.loads((lab/n).read_text()))
        elif label.startswith('shinobi'):
            q=json.loads((p/'handoff.json').read_text());assert q['source_packet']['sha256']==row['sha256']and q['CPU']['pairs']==2320
            for n in ['assembly.json','CPU-controls.json']:bindings(json.loads((p/n).read_text()))
            with zipfile.ZipFile(p/archive)as z:assert z.read('proof/CPU-controls.json')==(p/'CPU-controls.json').read_bytes()
        else:
            q=json.loads((p/'handoff.json').read_text());assert q['archive']['sha256']==row['sha256'];bindings(q);bindings(json.loads((p/'review.json').read_text()))
        dest=R/'docs/qa/checkpoints/2026-11-01'/label;assert not dest.exists()
        row.update(checkpoint=str(dest.relative_to(R)).replace('\\','/'),files=names,source_only=True,native=False,installed=False)
        rows[label]=row
    # Validation completes before publication; exact whitelists, no tree copy.
    for (label,root,archive,index,names)in tasks:
        dest=R/rows[label]['checkpoint'];dest.mkdir()
        for n in names:
            shutil.copyfile(R/'build'/root/n,dest/n)
            assert sha(dest/n)==sha(R/'build'/root/n)
    result=dict(passed=True,source_components=rows,installed_playable=85,new_native_unlocks=0,root_review=['Shinobi original/private CPU checks repeated:2320 pairs and exact receipt bytes.','Excitebike full producer repeated:2304 cases and1020 donor updates/14281 replacements. Source/code/art and semantic receipts repeat. ca65 object metadata changes on rebuild; refreshed the final bindings and packet afterward.','Metal Storm qualified laboratory kept immutable; all external binding hashes and internal corrected v3 packet members checked. No full PRG/object/debug outputs published.'],limits=['These are original-source components, not playable unlocks. Host callbacks/resources/interrupts/render/audio/native traversal remain.','Prince of Persia entry/art audit is separate; no assembled Prince actor.','Karnov private opening and current85 menu work remain separate exact-ROM checkpoints.'])
    (O/'review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
