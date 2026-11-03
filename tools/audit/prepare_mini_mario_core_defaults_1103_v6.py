"""Pin only the missing GB Studio default and Mini Mario sprite definitions."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from zipfile import ZipFile, ZIP_DEFLATED
import base64
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/mini-mario-defaults-1103-v6'
CORE = 'chrismaltby/gb-studio'
CORE_TREE = '49563d9ab3e8d78e10b0fc7b0797f23676d3045f'
MINI = 'Mico27/SuperMarioBrosMini'
MINI_TREE = '56d5a30ff8f58096c074ca59656efc5f787d0edb'
INPUTS = (
    (CORE, 'appData/engine/engine.json', '96cd723f39b7a01cd0ff52c60c0ce20dad836340'),
    (CORE, 'src/lib/project/loadEngineSchema.ts', '8b768ac09378d450bc2d68c2cd1408c7bc8ebcf9'),
    (CORE, 'src/lib/compiler/compileBootstrap.ts', '17ba728bc347b70e9dd816f34aa981dcaf8f2140'),
    (MINI, 'plugins/actorBehaviorPlugin/engine/engine.json', 'a1c546c341eca187c2ffe22e5cf65049947b6250'),
    (MINI, 'assets/sprites/smolmario.png.gbsres', 'b30403001ca5e89293ea9369981916416e30edfc'),
    (MINI, 'assets/sprites/supamario.png.gbsres', '2a2ac5fae2873a7bf5cf6493e23939f28d9679c1'),
)


def api(repo, route):
    return json.loads(subprocess.check_output(['gh', 'api', f'repos/{repo}/{route}']))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    # Complete immutable source tree is inspected in memory to rule out a local
    # replacement engine schema and additional plugin default overrides.
    tree = api(MINI, 'git/trees/'+MINI_TREE+'?recursive=1')
    assert not tree.get('truncated') and tree['sha'] == MINI_TREE
    rows = {r['path']: r for r in tree['tree'] if r['type'] == 'blob'}
    assert 'assets/engine/engine.json' not in rows
    plugin_schemas = {p: r['sha'] for p, r in rows.items() if p.endswith('/engine/engine.json')}
    assert len(plugin_schemas) == 5
    for p, blob in plugin_schemas.items():
        assert blob == ('6afc43e30dcff01645e1a7387fc18d35a5ed2fdb'
            if p == 'plugins/PlatformerPlus/engine/engine.json' else 'a1c546c341eca187c2ffe22e5cf65049947b6250')
    core_tree = api(CORE, 'git/trees/'+CORE_TREE+'?recursive=1')
    assert not core_tree.get('truncated') and core_tree['sha'] == CORE_TREE
    core_rows = {r['path']: r for r in core_tree['tree'] if r['type'] == 'blob'}
    for repo, path, blob in INPUTS:
        assert (core_rows if repo == CORE else rows)[path]['sha'] == blob
    def fetch(row):
        repo, path, blob = row
        result = api(repo, 'git/blobs/'+blob)
        assert result['encoding'] == 'base64'
        data = base64.b64decode(result['content'])
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == blob
        return repo+'/'+path, data
    with ThreadPoolExecutor(max_workers=3) as pool:
        items = dict(pool.map(fetch, INPUTS))
    core = json.loads(items[CORE+'/appData/engine/engine.json'])
    fields = {f['key']: f for f in core['fields'] if f.get('key')}
    assert fields['plat_hold_grav']['defaultValue'] == 512 and fields['plat_hold_grav']['cType'] == 'WORD'
    assert items[MINI+'/plugins/actorBehaviorPlugin/engine/engine.json'] == b'{"version": "4.0.0-e0"}'
    with ZipFile(ROOT/'docs/qa/checkpoints/2026-11-02/mini-mario-reference-v1/reference.zip') as z:
        project = json.loads(z.read('SuperMarioBrosMini.gbsproj'))
        plugin = json.loads(z.read('plugins/PlatformerPlus/engine/engine.json'))
        overrides = json.loads(z.read('project/engine_field_values.gbsres'))['engineFieldValues']
    assert project['_version'] == '4.2.0'
    assert not any(f.get('key') == 'plat_hold_grav' for f in plugin['fields'])
    assert not any(f['id'] == 'plat_hold_grav' for f in overrides)
    sprites = {}
    for name in ('smolmario', 'supamario'):
        sprite = json.loads(items[MINI+f'/assets/sprites/{name}.png.gbsres'])
        sprites[name] = {k: v for k, v in sprite.items() if k not in ('states', 'animations', 'metasprites')}
    target = OUT/'direct-inputs.zip'
    with ZipFile(target, 'w', ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in items.items():
            z.writestr(name, data)
    with ZipFile(target) as z:
        for name, data in items.items():
            assert z.read(name) == data
    rom = Path('C:/Users/kando/Downloads/SuperMarioBrosMini.gb')
    binary = rom.read_bytes()
    assert len(binary) == 2097152 and binary[0x148] == 6
    checksum = 0
    for value in binary[0x134:0x14D]:
        checksum = (checksum-value-1)&255
    assert checksum == binary[0x14D]
    out = dict(passed=True, core_source_version='4.2.0', core_tree=CORE_TREE, mini_tree=MINI_TREE,
        default_hold_gravity=512, no_project_or_plugin_override=True, no_local_engine_schema=True,
        plugin_schema_inventory=plugin_schemas, sprite_definitions=sprites,
        archive_bytes=target.stat().st_size, archive_SHA256=sha(target.read_bytes()),
        files={name: dict(bytes=len(data), SHA256=sha(data)) for name, data in items.items()},
        local_GB_ROM=dict(path=str(rom), bytes=len(binary), SHA256=sha(binary), header_checksum_valid=True),
        scope='Verified immutable upstream GB Studio4.2.0 engine schema, schema loading and bootstrap initialization, plus all Mini source plugin-schema identities and original sprite definitions. The source-derived held-jump gravity default is512 with no override. Local GB ROM is bound as a read-only reference; source-to-binary provenance and CPU instruction equivalence are not established.')
    (OUT/'receipt.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k: v for k, v in out.items() if k not in ('files','sprite_definitions')}, indent=2))
    print('sprite definitions:', json.dumps(sprites))


if __name__ == '__main__':
    main()
