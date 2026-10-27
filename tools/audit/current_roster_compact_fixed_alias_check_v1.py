"""Small source-only controls for the declared CV3 fixed-E observer copies."""
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import json

from current_roster_compact_11_v1 import linked


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    source = Path(__file__).with_name('current_roster_compact_11_v1.py')
    harness = source.with_suffix('.lua')
    raw, syms, address, location, hook = linked(a.rom)
    assert digest(raw) == '8487c439ded9bc6274e1dc8f8e051494fa96ee518553d9c2f382eccf2e71d0e6'
    prepare = next(n for n in ast.parse(source.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'prepare')
    block = next(n for n in prepare.body if isinstance(n, ast.For) and isinstance(n.target, ast.Tuple)
                 and [e.id for e in n.target.elts] == ['owner', 'keys'])
    code = compile(ast.fix_missing_locations(ast.Module(body=[block], type_ignores=[])), str(source), 'exec')
    load_bytes = 2 if address('Mirror_PPUMASK') < 256 else 3
    hooks = dict(nmi=hook('NonMaskableInterrupt'), nmi_return=hook('NonMaskableInterrupt', tail=True),
                 dma_complete=hook('PostDmaMaskEnable', offset=load_bytes), irq=hook('IrqScrollSplit'))

    def run(data=raw, hs=hooks, ss=syms):
        ns = dict(raw=data, hooks=copy.deepcopy(hs), syms=ss, address=address, location=location,
                  hashlib=hashlib, hook_copy_owners={})
        exec(code, ns)
        return ns

    good = run()
    assert all(good['hooks'][k]['banks'] == [125, 127] for k in ['nmi', 'nmi_return', 'dma_complete'])
    assert 'banks' not in good['hooks']['irq'] and good['hooks']['irq']['bank'] == 126
    rejected = []
    changes = [('NMI interior', 'NonMaskableInterrupt', 17), ('OAM RTS', 'OAMandReadJoypad', 42),
               ('NMI RTI following hook bytes', 'NonMaskableInterrupt', 212)]
    for name, owner, offset in changes:
        bad = bytearray(raw)
        bad[16+125*8192+(address(owner) & 8191)+offset] ^= 1
        try:
            run(bad)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(name)
    for name, hs, ss in [('wrong primary bank', copy.deepcopy(hooks), syms),
                         ('wrong endpoint bytes', copy.deepcopy(hooks), syms),
                         ('zero owner size', hooks, copy.deepcopy(syms))]:
        if name == 'wrong primary bank':
            hs['nmi']['bank'] = 126
        elif name == 'wrong endpoint bytes':
            hs['dma_complete']['bytes'][0] ^= 1
        else:
            ss['NonMaskableInterrupt']['size'] = '0'
        try:
            run(raw, hs, ss)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(name)

    producer = source.read_bytes()
    begin = producer.index(b'    # CV3 DMC owns an explicit E-window clone')
    end = producer.index(b'    cfg = dict(name=a.identity', begin)
    old_producer = producer[:begin]+producer[end:]
    old_producer = old_producer.replace(b'                   hook_copy_owners=hook_copy_owners,\n', b'', 1)
    assert digest(old_producer) == 'a8d0d1ddcac3b788dcffb1b1c115cd7703a4870d8bbf43d51afab7fc23fbb4c2'
    lua = harness.read_bytes()
    begin = lua.index(b'local function hookBank(h,physical)\n')
    end = lua.index(b'local function hook(h,fn)\n', begin)
    old_lua = lua[:begin]+lua[end:]
    old_lua = old_lua.replace(b'  if done or not hookBank(h,bank(pc))then return end\n',
                              b'  if done or bank(pc)~=h.bank then return end\n', 1)
    old_lua = old_lua.replace(b' and hookBank(C.hooks.dma_complete,q.start.bank)and q.count', b' and q.count', 1)
    assert digest(old_lua) == '9d1fc97d64011a59407f6c86188e76917c65b4a02638ef3446573cd1788becce'
    for key in ['nmi', 'nmi_return', 'dma_complete', 'irq']:
        h = good['hooks'][key]
        accepted = h.get('banks', [h['bank']])
        assert [bank for bank in [124, 125, 126, 127] if bank in accepted] == ([126] if key == 'irq' else [125, 127])
    report = dict(passed=True, native_run=False, ROM_sha256=digest(raw), owner_copies=good['hook_copy_owners'],
                  actual_producer_body_negative_controls=rejected, unchanged_other_source_raw_bytes=True,
                  original_producer_sha256=digest(old_producer), original_harness_sha256=digest(old_lua),
                  producer_sha256=digest(producer), harness_sha256=digest(lua), tool_sha256=digest(Path(__file__).read_bytes()),
                  runtime_scope='Lua bank-membership model is source-only; Lua/Mesen was not executed. Existing literal three-byte, NMI-restoration and DMA-value guards are retained.',
                  held_negative='Sypha Hard v2 frame316 remains FALSE; bank125 completion/entry/return was omitted by the old observer.')
    assert not a.output.exists()
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, output=str(a.output), sha256=digest(a.output.read_bytes()))))


if __name__ == '__main__':
    main()
