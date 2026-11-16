"""Read-only DK Jr public/private identity recovery on exact official67.

No imports of historical producers, source mount, ROM composition or file output.
Only the two pure retained Lua text transforms are evaluated from their ASTs.
"""
import ast
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

R = Path(__file__).resolve().parents[2]
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '67e3b8e7d4b01ea549fe9dc15c09b5a0b5f7085ee396d672a9c963d24287d0b5'
PAGES = (817, 833, 847, 856, 867, 881, 882, 883, 959, 960, 961)
CHR = 1048592
COOKIE_AT = 534485
PUBLIC_PAYLOAD = '30b1118ac41a70e81c2eda030f5d93a5f56b57feb8600415f860e6007dfffc83'
PUBLIC_COOKIE = bytes.fromhex('a7280130b1118ac41a70e81c2eda030f')
FLOOR_GRANT = 'docs/qa/allocations/dkjr-floor-entry-fit-1114.json'
FLOOR_GRANT_SHA = '3ba6f0b10fe1e91265991a9240ee78fd41cef6a04a1c4b596bc6ebd9ddaeaaa7'
PUBLIC_NATIVE = (
    (6515, bytes.fromhex('0848ad0260c90ad01ab517c928d0148d6a01a9548d6c01a9b88d6d01a996205a01900568284c2c9a6828608d6a01082007b79006d004284c53b428a95c20abb92053b48d6a01a9838d6c01a9bf8d6d01a9ba4c5a01eaea')),
    (5199, bytes.fromhex('208eb9')),
    (5911, bytes.fromhex('ad0260c90bad4a0760eaea')),
    (482667, b'\xea' * 26),
    (482789, b'\xea' * 26),
)
H = lambda value: sha256(value).hexdigest()


def file_bytes(name, expected=None):
    value = (R / name).read_bytes()
    if expected is not None:
        assert H(value) == expected, name
    return value


def identity(raw):
    assert isinstance(raw, bytes) and len(raw) == 2097168 and H(raw) == PIN
    payload = b''.join(raw[CHR+p*1024:CHR+(p+1)*1024] for p in PAGES)
    assert len(payload) == 11264 and H(payload) == PUBLIC_PAYLOAD
    assert raw[COOKIE_AT:COOKIE_AT+16] == PUBLIC_COOKIE
    assert PUBLIC_COOKIE == b'\xa7\x28\x01' + sha256(payload).digest()[:13]
    native = []
    for at, before in PUBLIC_NATIVE:
        assert raw[at:at+len(before)] == before, (at, raw[at:at+len(before)].hex())
        native.append(dict(file_offset=at, bytes=len(before), SHA256=H(before)))
    # Public13-row source, not the private14-row Mushroom-helper variant.
    columns = bytes((26,30,35,39,43,47,55,59,88,161,165,177,190))
    rows_at = 9*1024 + 0x2c4
    assert payload[rows_at:rows_at+13] == columns
    helpers = [dict(stage='1-1', actor=0x28 if i == 8 else 0x25,
                    initial_left=column*16, center=column*16+(24 if i == 8 else 16),
                    initial_top=208 if i == 8 else 192,
                    width=48 if i == 8 else 32)
               for i, column in enumerate(columns)]
    own = [(CHR+p*1024, 1024) for p in PAGES] + [(COOKIE_AT, 16)]
    own += [(at, len(before)) for at, before in PUBLIC_NATIVE]
    assert sum(size for _, size in own) == 11433
    serialized = b''.join(raw[at:at+size] for at, size in own)
    return dict(actual_ROM_SHA256=PIN, public_payload_SHA256=PUBLIC_PAYLOAD,
                owner_cookie=PUBLIC_COOKIE.hex(), pages=list(PAGES),
                complete_DK_owner_bytes=11433, complete_DK_owner_SHA256=H(serialized),
                native_public_preimages=native, helpers=helpers), payload


def floor_inventory(payload):
    grant = json.loads(file_bytes(FLOOR_GRANT, FLOOR_GRANT_SHA))
    assert grant['status'] == 'granted-private-source-proposal-only'
    sources = {}
    for name, digest in grant['frozen_sources'].items():
        file_bytes(name, digest)
        sources[name] = digest
    rows = []
    for row in grant['logical_fragments']:
        at, size = row['payload_offset'], row['bytes']
        digest = H(payload[at:at+size])
        rows.append(dict(role=row['role'], payload_offset=at, bytes=size,
                         current_public_SHA256=digest,
                         matches_private09b_preimage=digest == row['preimage_SHA256'],
                         matches_floor_proposal=digest == row['proposed_SHA256']))
    assert sum(row['bytes'] for row in rows) == 1073
    assert not any(row['matches_floor_proposal'] for row in rows)
    return dict(grant_SHA256=FLOOR_GRANT_SHA,
                grant_parent=grant['frozen_private_parent_SHA256'],
                grant_public_parent=grant['current_public_parent_SHA256'],
                frozen_sources=sources, fragments=rows,
                source_grant_is_not_current67_composition_or_native_authority=True)


def pure_function(path, name, globals_dict):
    tree = ast.parse((R / path).read_text(encoding='utf-8'))
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(nodes) == 1
    # The two functions consist only of pure local string transforms.
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(nodes[0]))
    exec(compile(ast.Module(body=nodes, type_ignores=[]), path, 'exec'), globals_dict)
    return globals_dict[name]


def literal(path, name):
    tree = ast.parse((R / path).read_text(encoding='utf-8'))
    nodes = [node for node in tree.body if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    assert len(nodes) == 1
    return ast.literal_eval(nodes[0].value)


def historical_controller():
    third = 'tools/audit/check_dkjr_third_gap_physical_1111.py'
    full = 'tools/audit/check_dkjr_full_stage_physical_1111.py'
    scope = dict(THIRD_GAP_INPUT=literal(third, 'THIRD_GAP_INPUT'))
    extend = pure_function(third, 'extend', scope)
    scope = dict(STAGE_EXIT=literal(full, 'STAGE_EXIT'), Third=SimpleNamespace(extend=extend))
    compose = pure_function(full, 'compose', scope)
    base = file_bytes('tools/playthroughs/dkjr_second_gap_stdout_1110.lua',
                      '97c4da3f2bcc228b022a01e2b8cf4aa89c480e57e6fb762905d4dc0c6bb19697')
    driver = file_bytes('tools/playthroughs/dkjr_late_stage_driver_1111.lua',
                        'b2eae50bb480049446303bdc6e56c1c771faef1a5160b62f3c5606adb91e69ee')
    text = compose(base.decode().replace('\r\n', '\n'), driver.decode().replace('\r\n', '\n'),
                   PUBLIC_COOKIE.hex(), 0xd1f0)
    # The old Windows Path.write_text serialized LF source as CRLF. Reproduce
    # that historical hash in memory, without creating its temporary file.
    digest = H(text.replace('\n', '\r\n').encode())
    assert digest == '96b6aa7760e0d9567aed999405d5aa359357f9cf86aa2f9e99f45f427e6daced', digest
    return text


ROM_LINE = "local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''\n"
CURRENT_GATE = f"assert(rom=='{PIN}','Exact public67 DK Jr replay input')\n"


def controller(raw, *, kind):
    """Strict current67 metadata facade; unchanged historic controls/endpoint.

    Root must supply SMB_DKJR_FAST_ROUTE=1, SMB_TEST_VARIANT=0 and the exact
    SMB_STDOUT_ROM_SHA as in the old delivered replay. This factory neither
    executes gameplay nor converts the old native receipt to a current one.
    """
    if kind != 'delivered-public-67':
        raise ValueError('Explicit delivered-public-67 kind required')
    identity(raw)
    text = historical_controller()
    assert text.count(ROM_LINE) == 1
    bound = text.replace(ROM_LINE, ROM_LINE + CURRENT_GATE, 1)
    assert bound.replace(CURRENT_GATE, '', 1) == text
    return bound


def main():
    raw = NIGHTLY.read_bytes()  # One immutable actual input snapshot.
    current, payload = identity(raw)
    floor = floor_inventory(payload)
    text = historical_controller()
    bound = controller(raw, kind='delivered-public-67')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(bound)
    rejected = 0
    for altered, kind in ((raw, 'untyped'), (raw[:-1] + bytes((raw[-1] ^ 1,)), 'delivered-public-67')):
        try:
            controller(altered, kind=kind)
        except (ValueError, AssertionError):
            rejected += 1
        else:
            raise AssertionError('Strict facade accepted unknown kind or bytes')
    assert rejected == 2
    result = dict(passed=True, current=current, floor=floor,
                  recovered_delivered_controller_LF_SHA256=H(text.encode()),
                  recovered_delivered_controller_CRLF_SHA256=H(text.replace('\n', '\r\n').encode()),
                  historical_controller_endpoint='active 1-2, no 25-grounded endpoint',
                  historical_native_ROM_SHA256='b1d449ebd7bbcc6f9c75be00891afc627a8354acb56a18bb9cd7a4ef40129576',
                  historical_actual_Downloads_receipt='0d8861c3102a5a1fb721b3ce6fe3dfde8feec385c2b0a6807e4d5c57c07d88fc',
                  current67_controller_LF_SHA256=H(bound.encode()),
                  current67_controller_compiles=True,
                  current67_controller_removal_recovers_historical_LF_exact=True,
                  strict_facade_negative_inputs_rejected=rejected,
                  source_or_CPU_mount=False, gameplay_execution=False,
                  candidate_composed=False, generated_or_extracted_files=0,
                  current_native_full_stage_claim=False)
    encoded = json.dumps(result, sort_keys=True, separators=(',', ':'))
    print('DKJR_CURRENT_RECOVERY ' + encoded, flush=True)
    print('DKJR_CURRENT_RECOVERY_SHA256 ' + H(encoded.encode()), flush=True)


if __name__ == '__main__':
    main()
