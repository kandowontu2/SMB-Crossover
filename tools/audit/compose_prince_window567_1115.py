"""Exact graphics-only Prince carrier composition over delivered ae66."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json,struct,zlib
import current_prince_body_research_ae66_1114 as Current
import check_prince_window567_render_1114 as Render

R,Packet=Render.Packet.R,Render.Packet
PIN='ae669c7ec7536f1c912b3000597be7b3416c20f312638b2589f52fab55f0bc01'
CANDIDATE='590e0ae60414d98d4b0a4d74874af58b93c6e720e8156220e0648966128b5f1f'
GRANT=R/'docs/qa/allocations/prince-window567-candidate-1115.json'
GRANT_SHA='47eb427e276c2d43d39886d831b68ddfba21ee7fb761f043696107bebdff38ab'
POSE_SHA='585fedc5269ececbd0e4279d86003873f833ad41cd7aca7804ffdd4c149700fb'
POSE_ZLIB_HEX='''78da55560f5013571adfec6e96253cc2b2ac610931ae2149438831e6621a639a6e12a0fe3b1b81506b3d6b53ea81a736a5d6b19ec709acd6fe99bb5e2789edcd74a6e74ca3d7e9cd747a1cb6377353af73f90b737373b5401b40104501edb505e41061ef05b59dcb6f32b3bfefedfbdefbbeeff7bdb7a248c44be25c7c4d7c637c73bc31dedfd9143f1c6f8fff26fe5efce33811ff0ca2372e8afdf1abf1e9f8379d98c00a164192284aa812468887133589ba4430218a354228d196d825bc28bc2e54bd7156f86d429556a57f9ff820f1c932e289bec45f846b8969888c8025b1e4c06bc5c955c93549517427ddc9cdc90688204428d9967c3df94e3296fc73f2221c15c57f26b310a238919c8390a6a4291aa202623dc42688dc5bcfa65e48b5a7de4cbd9bfa20d595fa0c2293ea4f8da7665292b4242d4f574188a2235d9dde91de03f18bf4518853e970fa6cfae374cec31f3eff5b3a93fe327d257d2bbd90cecfb01943c691792c13c80433a1ccb067de7359a0bc666fddd63a6f0b443b84280e7b44f143ef3fe053ee3fb46cbdb7979ccf39e158e6742692792ff361a63b238a7fcf88fff7ebcddc82b803ad644f19c4433deb7b6a7a0ef6fcb24714dfe879a727d673a1e7c7b717bc3dcb6ca067bc67ba07e905bda5bd6f7faee9dd99627c953eafef29df0bbe377ce77c9ffbaa7b1b7b0719bc03191c00f303e0bbd4ea55fccaf218ab3030344fc9df61f23bb0d1eb60e13a98fec8b436683484f55a4453c5ac382d991eb901bef7d5310d563fbd4db3dd52cb55535ec9167ed341664527363536092626c1e824f8aabed9bb4f13a4f75a9b2cbbb89d54a3640fbffbbfcc0a05d17177f81658bc05a4d3c289ee8eb6f0f1637f64a0151b1e07e838b8f391bf3eb87d5b78cb26a416dab10e317bcfdeb5fb19e2e95d953b1bf906152eb9aa57b03c43ff0a897345859c8c9c6014791dc8e509807c05903b87f6db0f34b3fb9af8e024a3203bb09129b098058bdf1eff75f7b1a395470ef3ada19b4c29d9b9383201c409303701fe33b36d87ecf12d0737d50a5e9eaa9e64ca898ea5e16be0ce35f0fdccb6c79d5b3635d77a3d7cf5794685b72f0e7e011684975e8c850e0907f623cd9f32aa9578c7e2e015b0f0efdc407bacedb870ec2872e4c1c018b8fb05b89b9bf1da6941e8a04e9d67a01d1dbc0c24fd60beabe1097b9d9fd9beed0368ed9c1d1c01f323e0bb1130213cf76c6cef1e61d74e6af7fda151303b0a6e8d826bb9a1430784e67dd47e388475ce66c7c0c218981e0353c22f5f8e1d392cb486a8fd7019ac7d363b0aa67f34d696493a97b2d52a9bb242c1b05686a657531490c859ec557cd4a7f90957a1a655eb94ab598a912876629df858bdd56bd19869d33a2367a0f488b605c35f21aed7577b79da8579d739356ece41d9111b8b9f42c7bd0c0aacb486a2e59c8c221182959e448630a7cf6d7554b868fb6a1b6591587711c2e260bdd967a2b598d1a3b11a347a0bc7a929550b91775a72c3c7d7b93d76ab8b76a20e8b8db352962761712777c8bcb4153a46014f5a080ea7d0d2bcf6f9518d85367b4c96dce61408c3e60bd2412d83511a79095d4c7ac03a1947b0f9a716876dee1207eeb2da2b9cab6dbcd562a964569c9c19f2b9181e775b9db45d737fad40e9ab92f91d4a0f6b61285aa20820189a0d11f93a1c45104896b221aa442707880c92bbd99072a58e85eb46116c3e7b41af452b357e4e1d45706cf082d582ae37fb4dc6082245872eb85d3aa703b14725b92192400b703f8af44ba0f739835e56a5d56938441d91e0e8e0058355673123a6882437cfe5d43960766f48500ccfa67eba55b6b9bab5d6ebe7dd390b929d313c29ab6a0c36d4f1feed11548a0c5dd0703ab50a5106d0dcc68d6b740658b3300a577dd966f55bcc5fc2c7ab1fda5c426e37e3d0297af54e6df58097e7ddf62886e58d75d3d45b40cecbc83e9c446f1c5429cfab595e4144700c990a1af461ad06e1a2b854bc76d66669b69a7918208e2d8e75bb5d954e076f6f94c210f882fc2081f32812c8316205ada5e408e8974a2543739c5a56a1d229594411951292e10b6653a5d1e0d76b1b0954fcfa87890304890c5c2e67bb15f4068662e4a0210f86406cb07336eb19124706f992e2a01c8465506451125f18ec52ad6a51b21e4611c88d86f495badc4607480ccbf21b1e5eb059831673d8648c91f9b864d057e36de1dd8ccbd9972fbd3b748c53ad57b3034a457f3e717738b9d6205fa3ffd4a8bda8e99361c8d85919d14ca2db10bc4f46a22376bd7625a711d4aa3e19b134ecb4985fb29a5246c37559411e7259e671b5ba9dbb1df613b68602b8309a8fef25d07b8fc5723f90450b603af2562a8d0ad6cfd00f984ecbbda951470b087138645ea73319de34ea0305e4d248c8b15167b721d6f70b00363bd65ded0df32eca1d0070cfb545409b8b3d0090c57f3d51c6a0a5344245c0f1b95ea1627550ade2955180cdf444d7acadad3268f5da00806a8589d0d9ac88e5395098633e8fdee5469cd1c2b66f12c1a2c22d056433813716b6dd4e70e5a5b5658c96a602856d4b094e57a1e3d488eae7a0b04d4cd43dff42de4146b7bf19d977be50de8624def73cfaca230e74a3dd6fb37e9533fca9a4f8646151882cd01138829e2b941f4112277ff67468e753ba4603d2a0c2245341bd96d7707d72521c59301a5af45a0fa7e997e7a1971fdf60efb659c31613658ec98b60bbbd52e33dcfbb3c4e77a408aa0786bd5cf27ba44c116660d8f545043ebe2cfa86221cbd79cf77b808ea356232726643a40813a7a23687d60e638f155190c5aabd06decdbb9c518a146fc428b901c87892885052c9b56e251b5630081da130c958b75613cec50ea7c1826c7dfe40cb7e13dfbc2f6f595735bee0b29300050b19b26f584e6e13558c49b221b787733923c530cfc27d4d078aa58b43fc8a922025e70124d80f24524ca0c39dab5431257b42d1570cbb62465b297b48d3cce5d8e28f2c5a0cc3fec8bafe9e96cf1443a50b8f3e426c7454da4dbcb181c6c4ac2f0f6f827d471f9124d032a64901f3d34087ee5eac5dade655ca08fdccdca7af551984dc8d1ea677cdfcf5bc05b6b0e61a4efbbffbe4e6d123c2e15684804c3e77fb019bc5e912303773f3449b70fc1842f49790b3df4eca41b38ce071f422d95f427cffcda44a79805508b96ac4f012ecf6546c5f9321b897df43f495e4cf4ec4ac969419eed010292166c7634e8700656d78bf84c16e8fc15208bc1b714122cda205b97e2e954927637aad41c3f16a55a054ba34b4dc1746c4d0500a3bb2d591935a53294b2c8eb7f26ebfcb59cfe28b37eb7002412fb1f8ec4c0ac83ca4fc129b3f3b3fa0a03d141361f1a59b314e2da894082b3bbd30c228352cadf030168a93c3eb8f8eb0d06fcc782f2f5116eaaecbf6708bd5c29b4de7d83248851a5f8c770b2e27e2682cc3a45ff8a545ad40e62789c6329cb8c4979705150c4f53679659e543c1fbb2893ee0cb0583df489df363d3607a1a2c2c1c2d5b3872b83274a8a9f500b2ff87f71cf6b0cd7aae4c899397fc8fd5747bf94ab78b770694b0d2b5c5722d902164402915876acb596d4ea46f2be199dfa5af222aefa7eb6b25b934f0bb471fe9726cb4db6def5aac308440393cf31ea8215a0ef5e5d44239a93c4a75a05c865d21d69ab44603a20f94e763a3f08cd52eebb85c953bef968f49f8cd255e7d9620191c6d50a1e89565d5caea55d8d25453aeeff25e454671bd464373a8daaaf5a82c4a8ecd5dc7e757aaa5b787ba6ab7129babdfe2bdbcdb7566d9c01410f974387727fc0ffb955566'''


def digest(raw):return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA;q=json.loads(data)
    assert q['eligible_input_SHA256']==PIN and q['private_in_memory_ROM_composition_authorized']
    assert tuple(q['owned_carrier_CHR_pages'])==Packet.PAGES
    for path,pin in q['frozen_sources'].items():assert digest((R/path).read_bytes())==pin,path
    return q


@lru_cache(maxsize=1)
def original_pose():
    data=zlib.decompress(bytes.fromhex(POSE_ZLIB_HEX));assert len(data)==3174 and digest(data)==POSE_SHA
    return data


@lru_cache(maxsize=1)
def proposal(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Expected exact owning ae66'
    q=allocation();current=Current.normalize(raw,kind='bt-service-ae66')
    before=Packet.extract(raw);assert before==Packet.extract(current.referenceF11)
    assert before[1][1][:3174]==original_pose()
    parts,_=Render.arrays(current.referenceF11)
    def change(*old):
        for row in q['decoded_envelopes']:
            stream=row['stream'];lo=row['offset'];size=row['bytes']
            old[stream][lo:lo+size]=parts[stream][lo:lo+size]
        return old
    result,codec=Packet.rebuild(raw,change);after=Packet.extract(result)
    for stream,(a,b)in enumerate(zip(before[1],after[1],strict=True)):
        allowed={at for row in q['decoded_envelopes']if row['stream']==stream for at in range(row['offset'],row['offset']+row['bytes'])}
        assert len(a)==len(b)and all(x==y for at,(x,y)in enumerate(zip(a,b,strict=True))if at not in allowed)
    config=len(before[0])-54
    words=struct.unpack_from('<12H',before[0],config);newwords=struct.unpack_from('<12H',after[0],config)
    allowed_head={config+2*word+byte for word in(2,4,6,10)for byte in(0,1)}
    assert len(before[0])==len(after[0])and all(a==b for at,(a,b)in enumerate(zip(before[0],after[0],strict=True))if at not in allowed_head)
    allowed={*range(Packet.COOKIE,Packet.COOKIE+16),*(at for page in Packet.PAGES for at in range(Packet.CHR+page*1024,Packet.CHR+(page+1)*1024))}
    changed={at for at,(a,b)in enumerate(zip(raw,result,strict=True))if a!=b};assert changed<=allowed
    if CANDIDATE is not None:assert digest(result)==CANDIDATE
    return result,dict(parent_SHA256=PIN,candidate_SHA256=digest(result),grant_SHA256=GRANT_SHA,
        cookie=result[Packet.COOKIE:Packet.COOKIE+16].hex(),codec=codec,old_config_words=words,new_config_words=newwords,
        exact_graphics_decoded_envelopes=q['decoded_envelopes'],all_other_decoded_and_physical_bytes_exact=True,
        immutable31072_head_art_decoder_loader_page_tables_exact=True,
        current_world_collision_importer_and_BT160_score10_Gm192_exact=True,
        compact_original_pose_bytes=3174,compact_original_pose_SHA256=POSE_SHA,
        portable_inverse_no_mutable_Downloads=True,outputs=0,Mesen=False,installed=False)


@lru_cache(maxsize=1)
def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Expected exact graphics567 candidate'
    q=allocation();parts=Packet.extract(raw)[1]
    def restore(*chunks):
        for row in q['decoded_envelopes']:
            stream=row['stream'];lo=row['offset'];size=row['bytes']
            assert digest(chunks[stream][lo:lo+size])==(row.get('new_SHA256')or digest(bytes.fromhex(row['new_hex'])))
            chunks[stream][lo:lo+size]=original_pose()if stream==1 and lo==0 else bytes.fromhex(row['old_hex'])
        return chunks
    parent,_=Packet.rebuild(raw,restore);assert digest(parent)==PIN
    assert proposal(parent)[0]==raw
    return parent


if __name__=='__main__':
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    print(json.dumps(proposal(raw)[1],separators=(',',':')),flush=True)
