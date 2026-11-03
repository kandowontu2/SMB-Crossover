"""Pin a small direct-input Mini Mario source packet, without a full clone."""
import base64,concurrent.futures,hashlib,json,subprocess,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-reference-1102-v1'
REPO='Mico27/SuperMarioBrosMini'
TREE='56d5a30ff8f58096c074ca59656efc5f787d0edb'
PATHS=['README.md','SuperMarioBrosMini.gbsproj','project/engine_field_values.gbsres','project/settings.gbsres','plugins/PlatformerPlus/engine/engine.json','plugins/PlatformerPlus/engine/include/states/platform.h','plugins/PlatformerPlus/engine/include/states/playerstates.h','plugins/PlatformerPlus/engine/src/states/platform.c','plugins/PlatformerPlus/engine/src/states/playerstates.c','plugins/GameSpecific/engine/include/actor.h','plugins/GameSpecific/engine/src/core/actor.c','assets/sprites/smolmario.png','assets/sprites/supamario.png','project/palettes/mario.gbsres','project/palettes/fire_mario.gbsres']
def api(path):return json.loads(subprocess.check_output(['gh','api','repos/'+REPO+'/'+path]))
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    # Query the immutable tree; all blobs are independently Git-object verified.
    tree=api('git/trees/'+TREE+'?recursive=1');assert not tree.get('truncated')and tree['sha']==TREE
    rows={row['path']:row for row in tree['tree']if row['type']=='blob'}
    assert all(name in rows for name in PATHS)
    assert sum(rows[name]['size']for name in PATHS)<200_000
    def fetch(name):
        row=rows[name];q=api('git/blobs/'+row['sha']);assert q['encoding']=='base64'
        data=base64.b64decode(q['content']);assert len(data)==row['size']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['sha']
        return name,data
    with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:items=dict(pool.map(fetch,PATHS))
    O.mkdir(exist_ok=True);archive=O/'reference.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,data in sorted(items.items()):z.writestr(name,data)
    with zipfile.ZipFile(archive)as z:
        for name,data in items.items():assert z.read(name)==data
    engine=json.loads(items['project/engine_field_values.gbsres']);settings=json.loads(items['project/settings.gbsres'])
    hitlines={}
    for name in['plugins/PlatformerPlus/engine/src/states/platform.c','plugins/PlatformerPlus/engine/src/states/playerstates.c']:
        lines=items[name].decode().splitlines()
        hitlines[name]=[dict(line=i,text=line.strip())for i,line in enumerate(lines,1)if any(word in line.lower()for word in['wall','jump_vel','walk_vel','run_vel','gravity'])][:100]
    receipt=dict(passed=True,private_reference_only=True,source='https://github.com/'+REPO,project='https://mico27.itch.io/super-mario-bros-mini',tree=TREE,total_repository_entries=len(tree['tree']),selected_files=len(items),uncompressed_bytes=sum(map(len,items.values())),archive_bytes=archive.stat().st_size,archive_SHA256=sha(archive.read_bytes()),files={name:dict(git_blob=rows[name]['sha'],SHA256=sha(data),bytes=len(data))for name,data in sorted(items.items())},engine_fields=engine,settings_keys=sorted(settings),source_navigation=hitlines,scope='Exact selected original platformer source, engine settings and two Mario sprite sheets; no full clone or scene/dependency rehydration. No original compilation, runtime physics port, NES CHR conversion, wall-grab implementation or roster admission yet. Innate wall-grab is a requested possible adaptation, pending traversal evidence. Credit Mico27; audio credit Michirin as upstream README states.')
    (O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items()if k not in['files','engine_fields','source_navigation','settings_keys']}))

if __name__=='__main__':main()
