"""Import the two original Capcom audio drivers used by the pinned web build.

Upstream disassemblies are local inputs under .upstream/mm2 and .upstream/mm3.
MM4 charge effects share the MM3 bytecode/engine. Their instrument references
are remapped without changing the original envelopes. MM2 APU writes yield to
the SFX driver, allowing the same effects over either game's music.
"""
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parents[2]

def main():
    for game in (2,3):
        base=ROOT/f'.upstream/mm{game}'
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=base,text=True).strip()
        constants=(base/'constants/audio.asm').read_text()+'\n'+(base/'constants/nes.asm').read_text()
        if game==2:constants+='\n'+(base/'constants/track.asm').read_text()
        macros=(base/'macros/audio.asm').read_text()
        engine=(base/'audio/engine.asm').read_text()
        ram=(base/'ram/ram.asm').read_text()
        definitions=[]
        for name,value in re.findall(r'^\s*(\w+)\s*=\s*\$([0-9A-Fa-f]+)',ram,re.M):
            address=int(value,16)
            if game==2 and 0xe0<=address<=0xf5 or game==3 and 0xc0<=address<=0xe3:
                definitions.append(f'{name} = ${address:02x}')
            if game==3 and 0x700<=address<=0x77c:
                definitions.append(f'{name} = Mm3AudioRam + ${address-0x700:02x}')
        if game==2:
            definitions+=['zpause = $41','aaudio_ram = Mm2AudioRam','amodulation_pointers = Mm2AudioRam + $7c']
            engine=engine.replace('LDY #$05\n\tSTX z:zaudio_ram_pointers','LDY #>Mm2AudioRam\n\tSTX z:zaudio_ram_pointers')
            for register, helper in [('SQ1_VOL, X','MegaManAudioWrite0'),
                                     ('SQ1_SWEEP, X','MegaManAudioWrite1'),
                                     ('APU_STATUS','MegaManAudioStatus')]:
                engine=engine.replace('STA '+register, 'JSR ::'+helper)
            wanted={'flashman','bubbleman','boss_fighting','game_over','boss_defeated','get_weapon','boss_show','title'}
            sfx={'mega_buster','megaman_hit','enemy_hit','enemy_immune','landing','teleport_in','atomic_fire_charge_1','atomic_fire_charge_2','atomic_fire_charge_3','atomic_fire_release','death','1up','select','refill','door'}
            paths=[base/f'audio/music/{name}.asm' for name in sorted(wanted)]
            paths += [base/f'audio/sfx/{name}.asm' for name in sorted(sfx)]
            labels=set(re.findall(r'^([A-Za-z_][A-Za-z0-9_]*):','\n'.join(p.read_text() for p in paths),re.M))
            pointers=(base/'audio/track_pointers.asm').read_text()
            pointers=re.sub(r'(\.WORD )([A-Za-z_]\w*)',lambda m:m[1]+(m[2] if m[2] in labels else 'music_silence'),pointers)
            data=pointers+'\nmusic_silence: .byte $0f\n.word 0,0,0,0,0\n'+'\n'.join(p.read_text() for p in paths)
        else:
            start=engine.index('_read_audio_data:');end=engine.index('_audio_processing:',start)
            engine=engine[:start]+'_read_audio_data:\n STY z:zaudio_C1\n STA z:zaudio_C2\n LDY #0\n LDA (zaudio_C1),y\n RTS\n\n'+engine[end:]
            # In MM2 areas this instance owns effects only. Preserve X and
            # leave the music channels entirely to the other driver.
            engine=engine.replace('_handle_music:\n', '_handle_music:\n LDA ::MmAudioEngine\n CMP #2\n BNE :+\n RTS\n:\n')
            names=['landing','1up','mega_buster','megaman_hit','death','enemy_hit','enemy_immune','select','door','teleport_out','refill']
            paths=[base/'audio/music/title.asm']+[base/f'audio/sfx/{name}.asm' for name in names]
            labels=set(re.findall(r'^([A-Za-z_]\w*):','\n'.join(p.read_text() for p in paths),re.M))
            pointers=(base/'audio/track_pointers.asm').read_text()
            pointers=re.sub(r'(\.DBYT )([A-Za-z_]\w*)',lambda m:m[1]+(m[2] if m[2] in labels or m[2]=='instrument_table_pointers' else '$0000'),pointers)
            mm4=ROOT/'.upstream/mm4'
            mm4_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=mm4,text=True).strip()
            instruments=(base/'audio/instruments.asm').read_text()
            instrument_lines=re.findall(r'^\s*instrument_set [^;\n]+',instruments,re.M)
            instrument_keys=[''.join(line.split()) for line in instrument_lines]
            source_instruments=re.findall(r'^\s*instrument_set [^;\n]+',(mm4/'audio/instruments.asm').read_text(),re.M)
            effects=[]
            def remap_instrument(match):
                line=source_instruments[int(match[1])-1]
                key=''.join(line.split())
                if key not in instrument_keys:
                    instrument_keys.append(key)
                    instrument_lines.append(line)
                return 'sfx_instruments '+str(instrument_keys.index(key)+1)
            for name in ('charge_shot_charging','charge_shot_full_charging_1',
                         'charge_shot_full_charging_2','full_charge_shot',
                         'pharaoh_shot','pharaoh_full_charge_shot'):
                effect=(mm4/f'audio/sfx/{name}.asm').read_text()
                effects.append(re.sub(r'sfx_instruments (\d+)',remap_instrument,effect))
            # The hosted charge-start clip joins the rising sequence to the
            # first full-charge tone; the short second tone is its loop.
            start_effect=effects[0].replace('\tsfx_end','')
            start_effect+=re.sub(r'^sfx_charge_shot_full_charging_1:\s*sfx_priority 7','',effects[1])
            loop_effect=effects[2].replace('sfx_priority 7','sfx_priority $87')
            refill=(base/'audio/sfx/refill.asm').read_text().replace('sfx_refill','sfx_refill_continuous').replace('sfx_loop 2,','sfx_loop 0,')
            # MM2's metal effect has fixed three-frame pulses followed by a
            # sixteen-frame noise decay. Transcribe its register-level notes
            # into the common MM3 bytecode rather than aliasing the buster.
            metal=['sfx_metal_blade:', ' sfx_priority 7',
                   ' current_sfx_global_transpose .SET 0']
            def tone(frames,volume,duty,note,noise,noise_volume):
                metal.extend([' sfx_global_channel_flags sfx_ads_set',' sfx_ads $ff',
                              f' sfx_frames {frames}',' .byte sfx_pulse_2 | sfx_noise',
                              ' sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set',
                              ' sfx_instruments 41',f' sfx_duty_cycle {duty}',f' sfx_volume {volume}',f' sfx_note {note}',
                              ' sfx_channel_flags sfx_instruments_set | sfx_volume_set',
                              ' sfx_instruments 51',f' sfx_volume {noise_volume}',f' sfx_noise_note {noise}'])
            tone(3,15,0,'C_3',5,15)
            tone(3,15,0,'C_3',5,15)
            for v in (15,11,7,3): tone(4,8,3,'A_5',8,v)
            metal.append(' sfx_end')
            extra=[start_effect,loop_effect,*effects[3:],refill,'\n'.join(metal)]
            pointers=pointers.replace('track_pointers_end:',
                '\t.DBYT sfx_charge_shot_charging\n\t.DBYT sfx_charge_shot_full_charging_2\n\t.DBYT sfx_full_charge_shot\n'
                '\t.DBYT sfx_pharaoh_shot\n\t.DBYT sfx_pharaoh_full_charge_shot\n'
                '\t.DBYT sfx_refill_continuous\n\t.DBYT sfx_metal_blade\ntrack_pointers_end:')
            data=pointers+'\ninstrument_table_pointers:\n .FEATURE FORCE_RANGE\n'+'\n'.join(instrument_lines)+'\n'+'\n'.join(p.read_text() for p in paths)+'\n'+'\n'.join(extra)
            data=f'; Charge effects: https://github.com/lsmmega/mm4 at {mm4_commit}.\n'+data
        result='\n'.join([constants,*definitions,macros,engine,data])
        macro_names=re.findall(r'\.MACRO (\w+)',macros)
        for name in sorted(macro_names,key=len,reverse=True):
            result=re.sub(r'\b'+name+r'\b',f'mm{game}_'+name,result)
        result=f'; Imported from https://github.com/lsmmega/mm{game} at {commit}.\n; Original Capcom sound engine and music; adapted by tools/reference/import_megaman_audio.py.\n.pushseg\n.segment "MM{game}_AUDIO"\n.scope Mm{game}\n'+result+'\n.endscope\n.popseg\n'
        folder=ROOT/f'audio/megaman{game}';folder.mkdir(exist_ok=True)
        (folder/'imported.s').write_text(result)
        print(f'Imported MM{game} audio, upstream {commit}')

if __name__=='__main__':main()
