"""Ordinary reach suffixes from the genuinely played Prince cap, exact3ce.

The parent diagnostics remain immutable. This additive source-only facade
authenticates the Shinobi inverse, complete Prince streams and reached hooks.
Forks copy only an actually played game in RAM; no actor/terrain/state seeds.
All receipts are diagnostics, never natural-pickup or physical Mesen passes.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import compose_shinobi_pickups_1123 as Shinobi
import probe_prince_hidden_life_current_1123 as P
import search_prince_cap_offsets_current_1123 as Prior

H, W, N, Engine = P.H, P.W, P.N, P.Engine
PIN = Shinobi.CANDIDATE
PREFIX_SHA = '0a9900ba84aeb3be5ed255e0d3623210635cd70dcc8394ce7c3ea085b7d1ebd3'
SEARCH_SHA = 'f35317c03b5c8bda3554a4c7bf54e1c49182da1f20564863790415f7cbd2be79'
CASES = (
    dict(name='idle-cap-Up-release-A', pre=0, pre_controls=0, press=129,
         right_delay=0, reach=True, donor_edge=True),
    dict(name='careful-edge-Up-release-A', pre=65, pre_controls=1, press=129,
         right_delay=0, settle=True, reach=True, donor_edge=True),
    dict(name='careful-edge-A-Up-on-descent', pre=65, pre_controls=1,
         press=129, right_delay=0, settle=True, up_descent=True,
         donor_edge=True),
)
EXPECTED_PREFIX = 'e65acbd83c108ba71f81d0335cbcf1f831f0b2c44edcbd7d60699c24aeb93949'
EXPECTED_SUFFIXES = (
    '9603c1196ee4723a88a8df4033b14a618328c39bf181fc5d552a4227ca7fdd86',
    '427c2a4bd2b31fa313c5f8c026c09da44caaf35205c47740299974c01280612f',
    '7ab7b1d35a144bbda063ee8c0115f14ac4aec0bedc6001db0995d81e89c92eb5',
)
NEGATIVE_RECEIPTS = (
    'a6768c8ba534166cb31f86b7e7f56d07cef8f0cd29aba751f0a0cae2a01c5c03',
    '0b978a86dfc9ef859b2f8dfd79222f9f58dd8c6a9102f1731250c1e7c2c3c3ea',
    '53388b65b38a7aa2ce916393f99e1d1d6bca9aeb6432c087b42b38aee6193c9d',
)


@lru_cache(maxsize=1)
def authenticate(raw):
    assert H(raw) == PIN
    parent = Shinobi.recover_parent(raw)
    assert H(parent) == P.CURRENT
    proof = P.authenticate(parent)
    assert P.Packet.extract(raw) == P.Packet.extract(parent)
    assert raw[P.Packet.COOKIE:P.Packet.COOKIE + 16] == bytes.fromhex(P.COOKIE)
    b = dict(W.Symbols.bundle(), raw=raw)
    for name, delta in (('GameLoop', 0), ('IdleLoop', 12), ('IdleLoop', 30),
                        ('BlockBufferColli_Head', 0),
                        ('NativeRarePlayerHeadCollisionCore', 0)):
        at = W.location(b, name) + delta
        assert raw[at:at + 8] == parent[at:at + 8]
    return dict(proof, actual=PIN, parent=H(parent), inverse='Shinobi.recover_parent')


def prefix(raw):
    authenticate(raw)
    parent = Shinobi.recover_parent(raw)
    text = P.controller(parent, 'cap')
    assert text.count(P.CURRENT) == 2
    old = text
    text = text.replace(P.CURRENT, PIN)
    assert text.replace(PIN, P.CURRENT) == old
    return P.G.First.once(text, "stockPhase('cap-fresh-A',128)",
                          "final=s;finish(false,'Reached genuine idle cap for ordinary reach suffixes');return true")


Facade = SimpleNamespace(**dict(P.__dict__, authenticate=authenticate))
cold = P.clone(P.cold, dict(authenticate=authenticate))
config = P.clone(Prior.config, dict(P=Facade))


def body():
    text = Prior.BODY
    once = P.G.First.once
    text = once(text, "if C.case.settle then S.phase='settle';setpad(0)else S.phase='press';S.request=s;setpad(C.case.press)end",
                "if C.case.settle then S.phase='settle';setpad(0)elseif C.case.reach then S.phase='reach';S.reach_start=s;setpad(8)else S.phase='press';S.request=s;setpad(C.case.press)end")
    text = once(text, "else S.phase='press';S.request=s;setpad(C.case.press)end\n  end\n elseif S.phase=='press'then",
                """elseif C.case.reach then S.phase='reach';S.reach_start=s;setpad(8)
   else S.phase='press';S.request=s;setpad(C.case.press)end
  end
 elseif S.phase=='reach'then
  setpad(8)
  if s.action==28 or s.pose==78 then S.reach_admission=S.reach_admission or s end
  if s.pose==78 then S.reach_apex=s;S.phase='release';setpad(0)end
  if updates-S.reach_start.updates>90 then finish('Bounded ordinary Up reach');return end
 elseif S.phase=='release'then
  setpad(0)
  if idle(s)then
   S.reach_released=s
   if s.y~=112 or s.foot~=144 then finish('Reach released away from the cap plane');return end
   S.phase='press';S.request=s;setpad(C.case.press)
  end
 elseif S.phase=='press'then""")
    text = once(text, "setpad(controls-S.launch_control<C.case.right_delay and 128 or 1)",
                """setpad(controls-S.launch_control<C.case.right_delay and 128 or 1)
  if C.case.up_descent and s.y>=113 and (s.speed<128 or s.action==7 or s.action==18)then
   S.descent_Up=S.descent_Up or s;setpad(9)
  end""")
    text = once(text, 'updates>=185', 'updates>=330')
    text = once(text, "s.x<976 or s.x>1056", "s.x<912 or s.x>1060")
    text = once(text, '#S.heads>=64', '#S.heads>=96')
    text = once(text, "local q={state=s,headX=s.x+8,headY=(s.y+1)&255};S.heads[#S.heads+1]=q",
                """local key=s.x..':'..s.y..':'..s.pose..':'..s.speed
 if S.head_key==key then return end;S.head_key=key
 local q={state=s,headX=s.x+8,headY=(s.y+1)&255};S.heads[#S.heads+1]=q""")
    assert not any(s in text for s in ('emu.write', 'emu.setState', 'io.open', 'dofile', 'saveState', 'loadState', 'takeScreenshot'))
    return text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compile-only', action='store_true')
    args = p.parse_args()
    assert H(Path(P.__file__).read_bytes()) == PREFIX_SHA
    assert H(Path(Prior.__file__).read_bytes()) == SEARCH_SHA
    raw = P.G.ROM.read_bytes()
    installed = H(raw)
    if installed != PIN:
        import compose_dkjr_shinobi_1123 as DK
        if H(raw) != DK.STAR_UNDER:
            import install_mega_giant_item_semantics_1123 as Mega
            assert H(raw) == Mega.CANDIDATE
            raw = Mega.recover_parent(raw)
        assert H(raw) == DK.STAR_UNDER
        raw = DK.recover_parent(raw)
        assert H(raw) == PIN  # Reproduce the named3ce fixture in RAM only.
    binding = authenticate(raw)
    text, suffix = prefix(raw), body()
    P.Base.LuaRuntime().compile(text)
    programs = [('local C=' + P.G.Stock.value(config(raw, case)) + '\n' + suffix) for case in CASES]
    for program in programs:
        P.Base.LuaRuntime().compile(program)
    assert H(text.encode()) == EXPECTED_PREFIX
    assert tuple(H(program.encode()) for program in programs) == EXPECTED_SUFFIXES
    print('PRINCE_REACH_COMPILE ' + json.dumps(dict(installed_input=installed, ROM=PIN, prefix=H(text.encode()),
          suffixes=[dict(name=c['name'], SHA256=H(p.encode())) for c, p in zip(CASES, programs)],
          binding=binding, outputs=0), separators=(',', ':')), flush=True)
    if args.compile_only:
        return
    captured = []

    def reached(image):
        model = cold(image)
        captured.append(model)
        return model

    def deny(*a, **k):
        raise AssertionError('Prince source-only reach probe attempted output/native')

    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), patch('subprocess.Popen', deny):
        with patch.object(Engine.J, 'cold', reached), patch.object(Engine.J, 'PIN', PIN):
            q = Engine.run(raw, 2400, text=text)
        receipt = q['receipt']
        assert receipt['reason'] == 'Reached genuine idle cap for ordinary reach suffixes'
        cap = receipt['natural_stock']['cap_ready']
        assert (cap['x'], cap['y'], cap['action'], cap['hp'], cap['lives']) == (937, 112, 0, 4, 2)
        assert len(captured) == 1
        model = captured.pop()
        print('PRINCE_REACH_PREFIX ' + json.dumps(dict(controller=H(text.encode()), receipt=q['receipt_SHA256'],
              passes=q['source_passes'], cap=cap), separators=(',', ':')), flush=True)
        for case, program, expected in zip(CASES, programs, NEGATIVE_RECEIPTS):
            fork = N.fork(model)
            with patch.object(Engine.J, 'cold', lambda image: fork), patch.object(Engine.J, 'PIN', PIN):
                q = Engine.run(raw, 365, text=program)
            s = q['receipt'].get('diagnostic', {})
            assert q['receipt_SHA256'] == expected
            small = {k: v for k, v in s.items() if k not in ('states', 'heads', 'feet', 'lastKey', 'head_key')}
            small['state_samples'] = len(s.get('states', []))
            small['heads'] = [dict(head=[h['headX'],h['headY'],h.get('row'),h.get('tile')],
                state={k:h['state'][k] for k in ('Main','x','y','action','pose','speed','hp')})
                for h in s.get('heads', []) if h.get('tile') == 96 or h.get('row') == 128 or h['state']['pose'] == 78]
            print('PRINCE_REACH_CASE ' + json.dumps(dict(name=case['name'], controller=q['controller_SHA256'],
                  receipt=q['receipt_SHA256'], passes=q['source_passes'], result=small), separators=(',', ':')), flush=True)
    print('PRINCE_REACH_SUMMARY ' + json.dumps(dict(ROM=PIN, cases=len(CASES), outputs=0,
          normal_input_only=True, genuine_linked_checkpoint=True, no_natural_pickup_pass_claim=True), separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
