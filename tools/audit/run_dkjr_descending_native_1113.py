"""Root's private native first-item/first-pipe checks for the pinned successor."""
import argparse
import base64
from hashlib import sha256
import json
from pathlib import Path
import zlib

import compose_dkjr_descending_platform_1113 as C
import replay_dkjr_descending_platform_1113 as Replay
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
OUT = Path(__file__).resolve().parents[2] / 'build/metal-flower-native-1112'
PARENT = '7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
PUBLIC_BUB = 'f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7'
PUBLIC_SMB2 = '3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'
PUBLIC_POSTBG = '12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52'
PINS = {
    'first-item': 'b784ed4ed57a051231424e1f603dda8b160a34b749d23138649ae7d463fe4a47',
    'first-pipe': '65af12f18021d30e47bd9f4022c01148bf295da76017f744acc38456345b90b8',
    'full': '122f4984fcf4310ce19fb26e4a7a121c83c0fff08b62dbc85af6d95adfffee66',
    'full-enemy-guard': 'acf454572d604b049deebbb82300a07c6852c9712065d6d32f44932c6e38442f',
    'full-waiting-guard': '36307f8ca293bf558377591a05939ed74d4b5a8cc42152a38cdce1c998cf0fbc',
}
DIRECT_PINS = {
    'first-item': '5ef1c7955010c1abebcbefdcdbe6594b76024f123a89117436b5782cde7f1d53',
    'full-enemy-guard': '84161feb7c7d4c6f6eb938e85a0fb2d82aef0600a9132d9946f148f85f1dcec6',
    'full-waiting-guard': '6c6aac8a3d0fdfe334beebcf62b4514014e45d9e044f43926b3ee38e261c8d73',
    'full-stair-active': '78215151aee3a4bb4309c26b31d18cf50dae9b95a9fd9a2772e7e45b4d8a729d',
    'full-stair-trace': '52792e0ce5141270c96ec7a40491f29ee9384787705d28dfbe00f34295538963',
    'full-stair-projection': '319a921e1ef75947b677ea212ff6ab5b5705754bc85a1eb98777999851ef2b82',
    'full-stair-turn': 'cd3004a7ffa3cdd4926dff58ab9d501c10339cdc0fae7daa81a17fa214b53487',
    'full-stair-universal': '80ef49e799e7d59775cc8a81ae7f5ef14207240e4d78b90c7b54f68105261386',
}
CURRENT_CHEAT_DK = 'a5942300cd677a9c62b1f3ff312552216766de8fcca8d93f8939143f3f650625'
CURRENT_CHEAT_PINS = {
    'first-item':'44563259a510e66937c919c8acd6e55b04d17cc5ab7ddc89f47e573be3ccfecf',
    'full-enemy-guard':'4248a1fc70ff5543942621211eec954373325b57ed9bc8cd718f106b7194f105',
    'full-waiting-guard':'e453ad753303d304f85015a6ce251b21444b5bf0e2e3382d3814509ec68191f5',
    'full-stair-active':'e36693a34ca895e639b9de892ac4d42d4c37f7e70c5ff89729875c95ca2e18bf',
    'full-stair-trace':'4b577fd1e4bd5afd72241506e88af3a6f8927b4371770d72f8308e8a9b066124',
    'full-stair-projection':'5efce8bb4e74fc372c82517a289b00e2d19edd9608e32da7f6a8891da00b5aab',
    'full-stair-turn':'66843bd42bf9794da119dbe7ab9cf9ca04dab00a9baaaf5da71fb5239230d8d2',
    'full-stair-universal':'71ae48c57aa14d691262642906a99e43964adc33191fc16b36bf228db089172c',
}
CURRENT_HIDDEN_DK = 'df130d5dba8d21e74f5bc2899aad4d77b681381c8f8dfa34b72b392131eedada'
CURRENT_HIDDEN_PINS = {
    'first-item':'99b9b4ca2f7f533deeb6be11e39c9d35f5b987ae36bac9646c843d8bdad763b2',
    'full-enemy-guard':'d20d7f9cfa13287de146aaa5c00d098afe75601ba6878a9636ea48aaf2ce616f',
    'full-waiting-guard':'e809e7fbad403daca146af5a17dfef2762d942e563030ead2a9cabc06cc3a988',
    'full-stair-active':'997bab00a8751373f0e0e6034c8deba6d2771f206eaaf6fd3fa461c9f6b264ca',
    'full-stair-trace':'313e30a252e000d3cdc529bd208f4029022bb8761f3b54f3d9755683d2e20936',
    'full-stair-projection':'c58bb3c5794a33ae8a37ddc2e6dc2047575fa7dfcaa5b3b61157c1e13c68da42',
    'full-stair-turn':'298fdf10e084343e5cc1058b69847f204ea334154e447bbc9b6190798efc90ee',
    'full-stair-universal':'c0b2401321db095c8392d4daca35d063018c18c9f81d9a4446365541c9bd43c2',
}


def direct_controller(image, route):
    """Original strict769 factories and route hashes, unchanged."""
    import compose_dkjr_direct_platform_1113 as Direct
    assert route in DIRECT_PINS
    if route == 'full-stair-universal':
        import replay_dkjr_stair_geometry_turn_1113 as Universal
        text=Universal.controller(image)
    elif route == 'full-stair-turn':
        import replay_dkjr_odd_stair_turn_1113 as Turn
        text=Turn.donor_ground_controller(image)
    elif route == 'full-stair-projection':
        import replay_dkjr_stair_projection_trace_1113 as Projection
        text=Projection.controller(image)
    elif route in ('full-stair-active','full-stair-trace'):
        import replay_dkjr_final_stair_takeoff_1113 as Stair
        text=Stair.active_trace_controller(image)if route=='full-stair-trace'else Stair.active_controller(image)
    else:
        full=route in ('full-enemy-guard','full-waiting-guard')
        text=Direct.controller(image,full=full,departure_enemy_guard=full,
                               approach_enemy_guard=route=='full-waiting-guard')
    assert sha256(text.encode()).hexdigest()==DIRECT_PINS[route]
    return text


def prepare_current_cheat(raw, *, route, reuse_image=None):
    """Explicit fa66 input, retained DK ownership, and ROM-pin-only controls."""
    import current_smb2_cheat_input_1114 as Current
    import compose_dkjr_direct_postbg_current_1113 as Merge
    assert route in DIRECT_PINS
    assert sha256(Path(Current.__file__).read_bytes()).hexdigest()=='f973573e52a2c752da3531ee6bc3706dc8e1096b79cc0fab2740ad4f0fb20f34'
    assert sha256(Path(Merge.__file__).read_bytes()).hexdigest()=='c5885ac48e48ae21f50fefd7be595fa456b6644ff145b012ef121b2562290f6b'
    typed=Current.normalize(raw,kind='cheat-fa66')
    own={i for at,size in Merge.Old.dk_envelopes()for i in range(at,at+size)}
    if reuse_image is None:
        legacy,_=Merge.proposal(typed.postbg)
        private=Merge.private_image(legacy)
    else:
        pin=sha256(reuse_image).hexdigest()
        if pin==CURRENT_CHEAT_DK:
            legacy=bytearray(reuse_image)
            for i,(old,new)in enumerate(zip(typed.postbg,raw,strict=True)):
                if old!=new:
                    assert legacy[i]==new
                    legacy[i]=old
            legacy=bytes(legacy)
            assert sha256(legacy).hexdigest()==Merge.PIN
            private=Merge.private_image(legacy)
        else:
            if pin==C.PIN:
                private=Merge.DK.transform(reuse_image)[0]
            else:
                assert pin==Merge.DK.PIN,'Reuse requires exact14ae/769/a594, never an unknown candidate'
                private=reuse_image
            assert sha256(private).hexdigest()==Merge.DK.PIN
            legacy=bytearray(typed.postbg)
            for at,size in Merge.Old.dk_envelopes():legacy[at:at+size]=private[at:at+size]
            legacy=bytes(legacy)
            assert sha256(legacy).hexdigest()==Merge.PIN
        assert Merge.private_image(legacy)==private
    image,info=typed.preserve(legacy,legacy_result_SHA256=Merge.PIN,allowed_component_offsets=own)
    assert sha256(image).hexdigest()==CURRENT_CHEAT_DK
    assert info['component_changed_bytes']==846 and info['current_fix_changed_bytes_preserved']==66
    original=direct_controller(private,route)
    assert original.count(Merge.DK.PIN)==1
    text=original.replace(Merge.DK.PIN,CURRENT_CHEAT_DK,1)
    assert text.replace(CURRENT_CHEAT_DK,Merge.DK.PIN,1)==original
    assert sha256(text.encode()).hexdigest()==CURRENT_CHEAT_PINS[route]
    LuaRuntime().compile(text)
    return image,text,dict(info,canonical_private_DK_SHA256=Merge.DK.PIN,
        legacy_controller_SHA256=DIRECT_PINS[route],controller_SHA256=sha256(text.encode()).hexdigest(),
        original_controls_authentication_and_assertions_exact=True,only_controller_ROM_pin_rebound=True,
        all_current_fixes_preserved=True,merged_native_qualified=False,private_only=True)


def prepare_current_hidden(raw, *, route, reuse_image=None):
    """Separate exact421 boundary; delegate frozen fa66 component preparation."""
    import current_smb2_hidden_input_1114 as Current
    import compose_dkjr_direct_postbg_current_1113 as Merge
    assert route in DIRECT_PINS
    assert sha256(Path(Current.__file__).read_bytes()).hexdigest()=='d9014c60e6294bc8eb92a8e24ab0dfdb84af428e5b3654dbb48cbd75ca67956b'
    typed=Current.normalize(raw,kind='hidden-421')
    cheat_reuse=reuse_image
    if reuse_image is not None:
        pin=sha256(reuse_image).hexdigest()
        assert pin in(C.PIN,Merge.DK.PIN,CURRENT_HIDDEN_DK),'Reuse requires exact14ae/769/df130'
        if pin==CURRENT_HIDDEN_DK:
            prior=bytearray(reuse_image)
            for at,size in Current.hidden_envelopes():prior[at:at+size]=typed.fa66[at:at+size]
            cheat_reuse=bytes(prior)
            assert sha256(cheat_reuse).hexdigest()==CURRENT_CHEAT_DK
    cheated,cheat_text,cheat_info=prepare_current_cheat(typed.fa66,route=route,reuse_image=cheat_reuse)
    assert sha256(cheated).hexdigest()==CURRENT_CHEAT_DK
    legacy=bytearray(typed.postbg)
    envelopes=Merge.Old.dk_envelopes()
    for at,size in envelopes:legacy[at:at+size]=cheated[at:at+size]
    legacy=bytes(legacy);assert sha256(legacy).hexdigest()==Merge.PIN
    own={i for at,size in envelopes for i in range(at,at+size)}
    image,info=typed.preserve(legacy,legacy_result_SHA256=Merge.PIN,allowed_component_offsets=own)
    assert sha256(image).hexdigest()==CURRENT_HIDDEN_DK
    assert info['component_changed_bytes']==846 and info['current_fix_changed_bytes_preserved']==176
    assert info['hidden_response_changed_bytes_preserved']==110 and info['fa66_changed_bytes_preserved']==66
    assert cheat_text.count(CURRENT_CHEAT_DK)==1
    text=cheat_text.replace(CURRENT_CHEAT_DK,CURRENT_HIDDEN_DK,1)
    assert text.replace(CURRENT_HIDDEN_DK,CURRENT_CHEAT_DK,1)==cheat_text
    assert sha256(text.encode()).hexdigest()==CURRENT_HIDDEN_PINS[route]
    LuaRuntime().compile(text)
    return image,text,dict(info,canonical_private_DK_SHA256=Merge.DK.PIN,
        legacy_controller_SHA256=DIRECT_PINS[route],controller_SHA256=sha256(text.encode()).hexdigest(),
        delegated_fa66_controller_SHA256=cheat_info['controller_SHA256'],
        original_controls_authentication_and_assertions_exact=True,only_controller_ROM_pin_rebound=True,
        all_current_fixes_preserved=True,merged_native_qualified=False,private_only=True)


def complete(args,image,text,candidate,expected,summary,public_now):
    assert sha256(image).hexdigest()==candidate and sha256(text.encode()).hexdigest()==expected
    if not args.metadata:
        assert OUT.is_dir()
        assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
        rom, script = OUT / 'candidate.nes', OUT / 'controller.lua'
        rom.write_bytes(image)
        script.write_text(text, encoding='utf-8', newline='\n')
        q = run(script, rom, OUT / 'capture', candidate, 240)
        receipt = {k: v for k, v in q['receipt'].items() if k != 'events'}
        receipt['last_events'] = q['receipt'].get('events', [])[-12:]
        summary.update(passed=q['passed'], receipt_SHA256=q['receipt_SHA256'],
                       receipt=receipt, outputs_written=q['outputs_written'])
        if args.route == 'full-stair-projection':
            rows=receipt.pop('final_stair_trace')
            assert len(rows)<=60
            encoded=json.dumps(rows,separators=(',',':')).encode()
            summary.update(trace_rows=len(rows),trace_bytes=len(encoded),
                trace_SHA256=sha256(encoded).hexdigest(),
                trace_codec='base64(zlib(UTF-8 JSON)); bounded instruction contexts only',
                trace_zlib_base64=base64.b64encode(zlib.compress(encoded,9)).decode())
    print(json.dumps(summary, separators=(',', ':')), flush=True)
    assert check(NIGHTLY)['ROM_sha256'] == public_now
    if not args.metadata:
        assert q['passed'], 'Private native DK component check did not pass'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--route', choices=tuple(PINS|DIRECT_PINS), required=True)
    p.add_argument('--metadata', action='store_true')
    p.add_argument('--reuse', action='store_true', help='Reuse the already composed exact14ae private file; no repeated parent build.')
    p.add_argument('--direct', action='store_true', help='Use the granted769afe direct-foreign successor and a route from DIRECT_PINS.')
    current=p.add_mutually_exclusive_group()
    current.add_argument('--current-cheat-fa66',action='store_true',help='Explicit exactfa66 current merge preserving all fixes; requires --direct. Defaults stay frozen.')
    current.add_argument('--current-hidden-421',action='store_true',help='Explicit exact421 current merge preserving hidden and cheat fixes; requires --direct. Defaults stay frozen.')
    args = p.parse_args(argv)
    if args.current_cheat_fa66:assert args.direct,'Explicit current fa66 merge requires --direct'
    if args.current_hidden_421:assert args.direct,'Explicit current421 merge requires --direct'
    if args.direct:
        import compose_dkjr_direct_platform_1113 as Direct
        assert args.route in DIRECT_PINS
    else:assert args.route in PINS,'This route requires the explicit direct successor'
    public_now = check(NIGHTLY)['ROM_sha256']
    if args.current_hidden_421:
        assert public_now=='421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f','Explicit hidden merge requires exact421 Downloads'
        image,text,info=prepare_current_hidden(NIGHTLY.read_bytes(),route=args.route,
            reuse_image=(OUT/'candidate.nes').read_bytes()if args.reuse else None)
        assert public_now==info['current_input_SHA256']
        expected=CURRENT_HIDDEN_PINS[args.route]
        summary=dict(ROM_SHA256=CURRENT_HIDDEN_DK,parent_SHA256=public_now,current_Downloads_SHA256=public_now,
            route=args.route,Lua_SHA256=expected,direct_foreign=True,current_hidden_421=True,
            private_only=True,installed=False,native_run=not args.metadata,reused_exact_private_candidate=args.reuse,
            current_preservation=info)
        complete(args,image,text,CURRENT_HIDDEN_DK,expected,summary,public_now)
        return
    if args.current_cheat_fa66:
        assert public_now=='fa66fa915d91ed125cf947b5c15d517c2919c62941378e10d62b0fdf184cdaae','Explicit current merge requires exactfa66 Downloads'
        image,text,info=prepare_current_cheat(NIGHTLY.read_bytes(),route=args.route,
            reuse_image=(OUT/'candidate.nes').read_bytes()if args.reuse else None)
        assert public_now==info['current_input_SHA256']
        expected=CURRENT_CHEAT_PINS[args.route]
        summary=dict(ROM_SHA256=CURRENT_CHEAT_DK,parent_SHA256=public_now,current_Downloads_SHA256=public_now,
            route=args.route,Lua_SHA256=expected,direct_foreign=True,current_cheat_fa66=True,
            private_only=True,installed=False,native_run=not args.metadata,reused_exact_private_candidate=args.reuse,
            current_preservation=info)
        complete(args,image,text,CURRENT_CHEAT_DK,expected,summary,public_now)
        return
    assert public_now in (PARENT, PUBLIC_BUB, PUBLIC_SMB2, PUBLIC_POSTBG)
    raw = NIGHTLY.read_bytes()
    if public_now == PUBLIC_POSTBG:
        import compose_smb2_postbg_mirror_1113 as PostBG
        raw = PostBG.inverse(raw)
        assert sha256(raw).hexdigest() == PUBLIC_SMB2
    if sha256(raw).hexdigest() == PUBLIC_SMB2:
        import compose_smb2_foreground_current_1113 as Current
        raw = Current.inverse(raw)
        assert sha256(raw).hexdigest() == PUBLIC_BUB
    if sha256(raw).hexdigest() == PUBLIC_BUB:
        import bub_native_noops_1113 as Bub
        raw = Bub.combined_reverse(raw)
        assert sha256(raw).hexdigest() == PARENT
    if args.reuse:
        image = (OUT / 'candidate.nes').read_bytes()
        if args.direct and sha256(image).hexdigest()==Direct.PIN:
            image=Direct.reverse(image)
        assert sha256(image).hexdigest() == C.PIN
        assert sha256(C.reverse(image)).hexdigest() == C.PARENT
    else:
        image, info = C.compose_current(raw)
        assert sha256(image).hexdigest() == C.PIN
        assert C.P.inverse_current(C.reverse(image)) == raw
        assert info['new_RAM_bytes'] == info['new_CHR_bytes'] == 0
    candidate=C.PIN
    expected=DIRECT_PINS[args.route]if args.direct else PINS[args.route]
    if args.direct:
        direct_parent=image
        image,direct_info=Direct.transform(image)
        assert Direct.reverse(image)==direct_parent and direct_info['changed_bytes']==141
        candidate=Direct.PIN
        text=direct_controller(image,args.route)
        expected=DIRECT_PINS[args.route]
    elif args.route == 'first-item':
        text = C.controller(image)
    elif args.route in ('full', 'full-enemy-guard', 'full-waiting-guard'):
        text = Replay.controller(image, descending_roof=(2,3), observe_prior=True,
                                 early_ledge=True, native_gap_observer=True,
                                 departure_enemy_guard=args.route!='full',
                                 approach_enemy_guard=args.route=='full-waiting-guard')
    else:
        text = Replay.controller(image, pipes=(1,), stop_after_pipe=1)
    assert sha256(text.encode()).hexdigest() == expected
    LuaRuntime().compile(text)
    summary = dict(ROM_SHA256=candidate, parent_SHA256=PARENT, current_Downloads_SHA256=public_now, route=args.route,
                   Lua_SHA256=expected, direct_foreign=args.direct, private_only=True, installed=False,
                   native_run=not args.metadata, reused_exact_private_candidate=args.reuse)
    complete(args,image,text,candidate,expected,summary,public_now)


if __name__ == '__main__':
    main()
