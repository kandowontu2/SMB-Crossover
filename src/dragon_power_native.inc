; Generated from DragonPowerUSA SHAe52cc421c726181a35f0cc9e8969a8aad50abd17bdc7eea59dc065990a576147.
; Every label is a genuine original instruction/data boundary. No fake aliases.
.pushseg
.segment "DRAGON_POWER_CORE"
DpNativeStart:
DpNE82E:
 jsr DpNE834 ;3:E82E 2034e8
DpNE831:
 jmp DpNEE25 ;3:E831 4c25ee
DpNE834:
 jsr DpNEC02 ;3:E834 2002ec
DpNE837:
 lda DpAction ;3:E837 a52d
DpNE839:
 pha ;3:E839 48
DpNE83A:
 jeq DpNE857 ;3:E83A f01b
DpNE83C:
 lda #$00 ;3:E83C a900
DpNE83E:
 sta DpPlatform+4 ;3:E83E 8d4a04
DpNE841:
 jsr DpNEDC9 ;3:E841 20c9ed
DpNE844:
 jsr DpNE889 ;3:E844 2089e8
DpNE847:
 jsr DpNE8B0 ;3:E847 20b0e8
DpNE84A:
 jsr DpNE8C3 ;3:E84A 20c3e8
DpNE84D:
 lda DpY ;3:E84D a5f8
DpNE84F:
 cmp #$e0 ;3:E84F c9e0
DpNE851:
 jcc DpNE857 ;3:E851 9004
DpNE853:
 lda #$80 ;3:E853 a980
DpNE855:
 sta DpExit ;3:E855 8542
DpNE857:
 pla ;3:E857 68
DpNE858:
 asl a ;3:E858 0a
DpNE859:
 tay ;3:E859 a8
DpNE85A:
 lda DpNE867,y ;3:E85A b967e8
DpNE85D:
 sta R0 ;3:E85D 8500
DpNE85F:
 lda DpNE867+1,y ;3:E85F b968e8
DpNE862:
 sta R1 ;3:E862 8501
DpNE864:
 jmp (R0) ;3:E864 6c0000
DpNE867:
 .word DpNE8E4,DpNE906,DpNE99A,DpNE9B3,DpNEA20,DpNEA3D,DpNEA80,DpNEA86,DpNEAA6,DpNEAD1,DpNEAE1,DpNEB05,DpNEB32,DpNEB6D,DpNEBE1,DpNEC17,DpNEC45
DpNE889:
 lda DpAction ;3:E889 a52d
DpNE88B:
 jeq DpNE8AF ;3:E88B f022
DpNE88D:
 cmp #$0d ;3:E88D c90d
DpNE88F:
 jcs DpNE8AF ;3:E88F b01e
DpNE891:
 lda DpX ;3:E891 a5f7
DpNE893:
 clc ;3:E893 18
DpNE894:
 adc #$08 ;3:E894 6908
DpNE896:
 tay ;3:E896 a8
DpNE897:
 lda DpY ;3:E897 a5f8
DpNE899:
 clc ;3:E899 18
DpNE89A:
 adc #$10 ;3:E89A 6910
DpNE89C:
 jsr DpHostTileQuery ;3:E89C 202ced
DpNE89F:
 cmp #$10 ;3:E89F c910
DpNE8A1:
 jcc DpNE8AF ;3:E8A1 900c
DpNE8A3:
 cmp #$13 ;3:E8A3 c913
DpNE8A5:
 jcs DpNE8AF ;3:E8A5 b008
DpNE8A7:
 lda DpClock ;3:E8A7 a526
DpNE8A9:
 and #$0f ;3:E8A9 290f
DpNE8AB:
 jne DpNE8AF ;3:E8AB d002
DpNE8AD:
 dec DpHP ;3:E8AD c62e
DpNE8AF:
 rts ;3:E8AF 60
DpNE8B0:
 lda #$00 ;3:E8B0 a900
DpNE8B2:
 sta DpPlatform+3 ;3:E8B2 8d4904
DpNE8B5:
 lda DpPlatform+0 ;3:E8B5 ad4604
DpNE8B8:
 jpl DpNE8C2 ;3:E8B8 1008
DpNE8BA:
 lda DpX ;3:E8BA a5f7
DpNE8BC:
 clc ;3:E8BC 18
DpNE8BD:
 adc DpPlatform+1 ;3:E8BD 6d4704
DpNE8C0:
 sta DpX ;3:E8C0 85f7
DpNE8C2:
 rts ;3:E8C2 60
DpNE8C3:
 lda DpPlatform+2 ;3:E8C3 ad4804
DpNE8C6:
 and #$7f ;3:E8C6 297f
DpNE8C8:
 jeq DpNE8CD ;3:E8C8 f003
DpNE8CA:
 dec DpPlatform+2 ;3:E8CA ce4804
DpNE8CD:
 lda DpAction ;3:E8CD a52d
DpNE8CF:
 cmp #$03 ;3:E8CF c903
DpNE8D1:
 jeq DpNE8E3 ;3:E8D1 f010
DpNE8D3:
 cmp #$0a ;3:E8D3 c90a
DpNE8D5:
 jeq DpNE8E3 ;3:E8D5 f00c
DpNE8D7:
 cmp #$0b ;3:E8D7 c90b
DpNE8D9:
 jeq DpNE8E3 ;3:E8D9 f008
DpNE8DB:
 lda DpPlatform+2 ;3:E8DB ad4804
DpNE8DE:
 and #$7f ;3:E8DE 297f
DpNE8E0:
 sta DpPlatform+2 ;3:E8E0 8d4804
DpNE8E3:
 rts ;3:E8E3 60
DpNE8E4:
 lda #$00 ;3:E8E4 a900
DpNE8E6:
 sta DpJumping ;3:E8E6 8538
DpNE8E8:
 sta DpSourcePrevious ;3:E8E8 85e4
DpNE8EA:
 sta DpAttribute ;3:E8EA 8531
DpNE8EC:
 sta DpVertical ;3:E8EC 8534
DpNE8EE:
 sta DpHorizontal ;3:E8EE 8535
DpNE8F0:
 sta DpSeconds ;3:E8F0 8536
DpNE8F2:
 sta DpShotState ;3:E8F2 853a
DpNE8F4:
 sta DpSpecial ;3:E8F4 8537
DpNE8F6:
 jsr DpSpawnHook ;3:E8F6 20baec
DpNE8F9:
 lda DpActionFlags ;3:E8F9 a532
DpNE8FB:
 and #$01 ;3:E8FB 2901
DpNE8FD:
 sta DpActionFlags ;3:E8FD 8532
DpNE8FF:
 lda #$02 ;3:E8FF a902
DpNE901:
 sta DpPose ;3:E901 8530
DpNE903:
 inc DpAction ;3:E903 e62d
DpNE905:
 rts ;3:E905 60
DpNE906:
 lda DpContacts+0 ;3:E906 ad0004
DpNE909:
 jne DpNE915 ;3:E909 d00a
DpNE90B:
 lda DpContacts+1 ;3:E90B ad0104
DpNE90E:
 jne DpNE915 ;3:E90E d005
DpNE910:
 lda DpPlatform+0 ;3:E910 ad4604
DpNE913:
 jpl DpNE933 ;3:E913 101e
DpNE915:
 lda DpPlatform+0 ;3:E915 ad4604
DpNE918:
 jmi DpNE920 ;3:E918 3006
DpNE91A:
 lda DpY ;3:E91A a5f8
DpNE91C:
 and #$f8 ;3:E91C 29f8
DpNE91E:
 sta DpY ;3:E91E 85f8
DpNE920:
 lda DpFresh ;3:E920 a5e0
DpNE922:
 and #$03 ;3:E922 2903
DpNE924:
 jeq DpNE93F ;3:E924 f019
DpNE926:
 lsr a ;3:E926 4a
DpNE927:
 jcs DpNE931 ;3:E927 b008
DpNE929:
 lda #$06 ;3:E929 a906
DpNE92B:
 sta DpPose ;3:E92B 8530
DpNE92D:
 lda #$04 ;3:E92D a904
DpNE92F:
 jne DpNE93A ;3:E92F d009
DpNE931:
 lda #$e7 ;3:E931 a9e7
DpNE933:
 sta DpVertical ;3:E933 8534
DpNE935:
 lda #$04 ;3:E935 a904
DpNE937:
 sta DpPose ;3:E937 8530
DpNE939:
 lsr a ;3:E939 4a
DpNE93A:
 sta DpAction ;3:E93A 852d
DpNE93C:
 jmp DpNE96A ;3:E93C 4c6ae9
DpNE93F:
 lda DpHeld ;3:E93F a5df
DpNE941:
 and #$20 ;3:E941 2920
DpNE943:
 jeq DpNE957 ;3:E943 f012
DpNE945:
 ldy #$09 ;3:E945 a009
DpNE947:
 sty DpPose ;3:E947 8430
DpNE949:
 lda #$00 ;3:E949 a900
DpNE94B:
 sta DpTimer ;3:E94B 8533
DpNE94D:
 lda DpActionFlags ;3:E94D a532
DpNE94F:
 and #$01 ;3:E94F 2901
DpNE951:
 sta DpActionFlags ;3:E951 8532
DpNE953:
 lda #$0c ;3:E953 a90c
DpNE955:
 jne DpNE93A ;3:E955 d0e3
DpNE957:
 lda DpHeld ;3:E957 a5df
DpNE959:
 and #$c0 ;3:E959 29c0
DpNE95B:
 jeq DpNE968 ;3:E95B f00b
DpNE95D:
 lda DpClock ;3:E95D a526
DpNE95F:
 lsr a ;3:E95F 4a
DpNE960:
 lsr a ;3:E960 4a
DpNE961:
 lsr a ;3:E961 4a
DpNE962:
 and #$03 ;3:E962 2903
DpNE964:
 jne DpNE968 ;3:E964 d002
DpNE966:
 lda #$02 ;3:E966 a902
DpNE968:
 sta DpPose ;3:E968 8530
DpNE96A:
 lda DpHeld ;3:E96A a5df
DpNE96C:
 jmi DpNE988 ;3:E96C 301a
DpNE96E:
 asl a ;3:E96E 0a
DpNE96F:
 jmi DpNE992 ;3:E96F 3021
DpNE971:
 ldy #$00 ;3:E971 a000
DpNE973:
 lda DpHorizontal ;3:E973 a535
DpNE975:
 jmi DpNE979 ;3:E975 3002
DpNE977:
 ldy #$40 ;3:E977 a040
DpNE979:
 sty DpAttribute ;3:E979 8431
DpNE97B:
 lda DpActionFlags ;3:E97B a532
DpNE97D:
 and #$01 ;3:E97D 2901
DpNE97F:
 asl a ;3:E97F 0a
DpNE980:
 asl a ;3:E980 0a
DpNE981:
 asl a ;3:E981 0a
DpNE982:
 asl a ;3:E982 0a
DpNE983:
 ora DpPose ;3:E983 0530
DpNE985:
 sta DpPose ;3:E985 8530
DpNE987:
 rts ;3:E987 60
DpNE988:
 lda DpHorizontal ;3:E988 a535
DpNE98A:
 jpl DpNE971 ;3:E98A 10e5
DpNE98C:
 lda #$00 ;3:E98C a900
DpNE98E:
 sta DpHorizontal ;3:E98E 8535
DpNE990:
 jeq DpNE971 ;3:E990 f0df
DpNE992:
 lda DpHorizontal ;3:E992 a535
DpNE994:
 jmi DpNE971 ;3:E994 30db
DpNE996:
 lda #$80 ;3:E996 a980
DpNE998:
 jne DpNE98E ;3:E998 d0f4
DpNE99A:
 lda DpActionFlags ;3:E99A a532
DpNE99C:
 and #$01 ;3:E99C 2901
DpNE99E:
 sta DpActionFlags ;3:E99E 8532
DpNE9A0:
 lda DpHeld ;3:E9A0 a5df
DpNE9A2:
 and #$c0 ;3:E9A2 29c0
DpNE9A4:
 ora DpActionFlags ;3:E9A4 0532
DpNE9A6:
 sta DpActionFlags ;3:E9A6 8532
DpNE9A8:
 lda #$01 ;3:E9A8 a901
DpNE9AA:
 sta DpJumping ;3:E9AA 8538
DpNE9AC:
 inc DpAction ;3:E9AC e62d
DpNE9AE:
 lda #$30 ;3:E9AE a930
DpNE9B0:
 jsr DpAudioRequest ;3:E9B0 20a898
DpNE9B3:
 lda DpHeld ;3:E9B3 a5df
DpNE9B5:
 and #$cf ;3:E9B5 29cf
DpNE9B7:
 sta DpHeld ;3:E9B7 85df
DpNE9B9:
 inc DpVertical ;3:E9B9 e634
DpNE9BB:
 lda DpVertical ;3:E9BB a534
DpNE9BD:
 jpl DpNE9E0 ;3:E9BD 1021
DpNE9BF:
 lda DpY ;3:E9BF a5f8
DpNE9C1:
 cmp #$04 ;3:E9C1 c904
DpNE9C3:
 jcc DpNE9CD ;3:E9C3 9008
DpNE9C5:
 lda DpContacts+6 ;3:E9C5 ad0604
DpNE9C8:
 jeq DpNE9D1 ;3:E9C8 f007
DpNE9CA:
 jsr DpNEEF9 ;3:E9CA 20f9ee
DpNE9CD:
 lda #$00 ;3:E9CD a900
DpNE9CF:
 sta DpVertical ;3:E9CF 8534
DpNE9D1:
 lda DpPlatform+2 ;3:E9D1 ad4804
DpNE9D4:
 jmi DpNE9DC ;3:E9D4 3006
DpNE9D6:
 lda DpFresh ;3:E9D6 a5e0
DpNE9D8:
 and #$02 ;3:E9D8 2902
DpNE9DA:
 jne DpNEA0C ;3:E9DA d030
DpNE9DC:
 lda #$04 ;3:E9DC a904
DpNE9DE:
 jne DpNE9FC ;3:E9DE d01c
DpNE9E0:
 lda DpContacts+0 ;3:E9E0 ad0004
DpNE9E3:
 jne DpNE9EF ;3:E9E3 d00a
DpNE9E5:
 lda DpContacts+1 ;3:E9E5 ad0104
DpNE9E8:
 jne DpNE9EF ;3:E9E8 d005
DpNE9EA:
 lda DpPlatform+0 ;3:E9EA ad4604
DpNE9ED:
 jpl DpNEA01 ;3:E9ED 1012
DpNE9EF:
 lda #$67 ;3:E9EF a967
DpNE9F1:
 jsr DpAudioRequest ;3:E9F1 20a898
DpNE9F4:
 jsr DpNEF0D ;3:E9F4 200def
DpNE9F7:
 lda #$01 ;3:E9F7 a901
DpNE9F9:
 sta DpAction ;3:E9F9 852d
DpNE9FB:
 lsr a ;3:E9FB 4a
DpNE9FC:
 sta DpPose ;3:E9FC 8530
DpNE9FE:
 jmp DpNE96A ;3:E9FE 4c6ae9
DpNEA01:
 lda DpPlatform+2 ;3:EA01 ad4804
DpNEA04:
 jmi DpNE9DC ;3:EA04 30d6
DpNEA06:
 lda DpFresh ;3:EA06 a5e0
DpNEA08:
 and #$02 ;3:EA08 2902
DpNEA0A:
 jeq DpNE9DC ;3:EA0A f0d0
DpNEA0C:
 lda DpPlatform+2 ;3:EA0C ad4804
DpNEA0F:
 ora #$80 ;3:EA0F 0980
DpNEA11:
 sta DpPlatform+2 ;3:EA11 8d4804
DpNEA14:
 lda #$00 ;3:EA14 a900
DpNEA16:
 sta DpVertical ;3:EA16 8534
DpNEA18:
 lda #$0a ;3:EA18 a90a
DpNEA1A:
 sta DpAction ;3:EA1A 852d
DpNEA1C:
 lda #$05 ;3:EA1C a905
DpNEA1E:
 jne DpNE9FC ;3:EA1E d0dc
DpNEA20:
 lda DpActionFlags ;3:EA20 a532
DpNEA22:
 and #$01 ;3:EA22 2901
DpNEA24:
 tay ;3:EA24 a8
DpNEA25:
 sta DpActionFlags ;3:EA25 8532
DpNEA27:
 lda DpHeld ;3:EA27 a5df
DpNEA29:
 and #$c0 ;3:EA29 29c0
DpNEA2B:
 ora DpActionFlags ;3:EA2B 0532
DpNEA2D:
 and #$cf ;3:EA2D 29cf
DpNEA2F:
 sta DpActionFlags ;3:EA2F 8532
DpNEA31:
 lda DpNEA7E,y ;3:EA31 b97eea
DpNEA34:
 sta DpTimer ;3:EA34 8533
DpNEA36:
 inc DpAction ;3:EA36 e62d
DpNEA38:
 lda #$31 ;3:EA38 a931
DpNEA3A:
 jsr DpAudioRequest ;3:EA3A 20a898
DpNEA3D:
 lda DpHeld ;3:EA3D a5df
DpNEA3F:
 and #$0f ;3:EA3F 290f
DpNEA41:
 sta DpHeld ;3:EA41 85df
DpNEA43:
 dec DpTimer ;3:EA43 c633
DpNEA45:
 jne DpNEA6F ;3:EA45 d028
DpNEA47:
 jsr DpNEF3A ;3:EA47 203aef
DpNEA4A:
 jsr DpNEF9A ;3:EA4A 209aef
DpNEA4D:
 lda DpActionFlags ;3:EA4D a532
DpNEA4F:
 and #$08 ;3:EA4F 2908
DpNEA51:
 jne DpNEA67 ;3:EA51 d014
DpNEA53:
 lda DpWaves ;3:EA53 a53b
DpNEA55:
 and #$3f ;3:EA55 293f
DpNEA57:
 jeq DpNEA67 ;3:EA57 f00e
DpNEA59:
 lda DpShotState ;3:EA59 a53a
DpNEA5B:
 and #$0f ;3:EA5B 290f
DpNEA5D:
 jne DpNEA67 ;3:EA5D d008
DpNEA5F:
 lda #$06 ;3:EA5F a906
DpNEA61:
 sta DpAction ;3:EA61 852d
DpNEA63:
 lda #$07 ;3:EA63 a907
DpNEA65:
 jne DpNEA6C ;3:EA65 d005
DpNEA67:
 lda #$01 ;3:EA67 a901
DpNEA69:
 sta DpAction ;3:EA69 852d
DpNEA6B:
 asl a ;3:EA6B 0a
DpNEA6C:
 sta DpPose ;3:EA6C 8530
DpNEA6E:
 rts ;3:EA6E 60
DpNEA6F:
 lda DpHeld ;3:EA6F a5df
DpNEA71:
 and #$02 ;3:EA71 2902
DpNEA73:
 jne DpNEA7B ;3:EA73 d006
DpNEA75:
 lda DpActionFlags ;3:EA75 a532
DpNEA77:
 ora #$06 ;3:EA77 0906
DpNEA79:
 sta DpActionFlags ;3:EA79 8532
DpNEA7B:
 jmp DpNE971 ;3:EA7B 4c71e9
DpNEA7E:
 .byte 12,20
DpNEA80:
 lda #$20 ;3:EA80 a920
DpNEA82:
 sta DpTimer ;3:EA82 8533
DpNEA84:
 inc DpAction ;3:EA84 e62d
DpNEA86:
 lda DpHeld ;3:EA86 a5df
DpNEA88:
 and #$0f ;3:EA88 290f
DpNEA8A:
 sta DpHeld ;3:EA8A 85df
DpNEA8C:
 and #$02 ;3:EA8C 2902
DpNEA8E:
 jne DpNEA9A ;3:EA8E d00a
DpNEA90:
 lda #$01 ;3:EA90 a901
DpNEA92:
 sta DpAction ;3:EA92 852d
DpNEA94:
 lsr a ;3:EA94 4a
DpNEA95:
 sta DpPose ;3:EA95 8530
DpNEA97:
 jmp DpNE971 ;3:EA97 4c71e9
DpNEA9A:
 lda DpTimer ;3:EA9A a533
DpNEA9C:
 jeq DpNEAA4 ;3:EA9C f006
DpNEA9E:
 dec DpTimer ;3:EA9E c633
DpNEAA0:
 lda #$07 ;3:EAA0 a907
DpNEAA2:
 jne DpNEA95 ;3:EAA2 d0f1
DpNEAA4:
 inc DpAction ;3:EAA4 e62d
DpNEAA6:
 lda DpHeld ;3:EAA6 a5df
DpNEAA8:
 and #$0f ;3:EAA8 290f
DpNEAAA:
 sta DpHeld ;3:EAAA 85df
DpNEAAC:
 and #$02 ;3:EAAC 2902
DpNEAAE:
 jne DpNEAB9 ;3:EAAE d009
DpNEAB0:
 sta DpPose ;3:EAB0 8530
DpNEAB2:
 lda #$01 ;3:EAB2 a901
DpNEAB4:
 sta DpAction ;3:EAB4 852d
DpNEAB6:
 jmp DpNE971 ;3:EAB6 4c71e9
DpNEAB9:
 lda DpFresh ;3:EAB9 a5e0
DpNEABB:
 lsr a ;3:EABB 4a
DpNEABC:
 jcs DpNEAC2 ;3:EABC b004
DpNEABE:
 lda #$07 ;3:EABE a907
DpNEAC0:
 jne DpNEA95 ;3:EAC0 d0d3
DpNEAC2:
 lda #$10 ;3:EAC2 a910
DpNEAC4:
 sta DpTimer ;3:EAC4 8533
DpNEAC6:
 dec DpWaves ;3:EAC6 c63b
DpNEAC8:
 inc DpShotState ;3:EAC8 e63a
DpNEACA:
 inc DpAction ;3:EACA e62d
DpNEACC:
 lda #$34 ;3:EACC a934
DpNEACE:
 jsr DpAudioRequest ;3:EACE 20a898
DpNEAD1:
 lda DpHeld ;3:EAD1 a5df
DpNEAD3:
 and #$0f ;3:EAD3 290f
DpNEAD5:
 sta DpHeld ;3:EAD5 85df
DpNEAD7:
 lda DpTimer ;3:EAD7 a533
DpNEAD9:
 jmi DpNEA90 ;3:EAD9 30b5
DpNEADB:
 dec DpTimer ;3:EADB c633
DpNEADD:
 lda #$08 ;3:EADD a908
DpNEADF:
 jne DpNEA95 ;3:EADF d0b4
DpNEAE1:
 lda DpActionFlags ;3:EAE1 a532
DpNEAE3:
 and #$01 ;3:EAE3 2901
DpNEAE5:
 sta DpActionFlags ;3:EAE5 8532
DpNEAE7:
 lda #$04 ;3:EAE7 a904
DpNEAE9:
 sta DpKickAge ;3:EAE9 8587
DpNEAEB:
 lda DpHeld ;3:EAEB a5df
DpNEAED:
 and #$c0 ;3:EAED 29c0
DpNEAEF:
 ora DpActionFlags ;3:EAEF 0532
DpNEAF1:
 sta DpActionFlags ;3:EAF1 8532
DpNEAF3:
 lda DpVertical ;3:EAF3 a534
DpNEAF5:
 jpl DpNEAFB ;3:EAF5 1004
DpNEAF7:
 lda #$00 ;3:EAF7 a900
DpNEAF9:
 sta DpVertical ;3:EAF9 8534
DpNEAFB:
 inc DpAction ;3:EAFB e62d
DpNEAFD:
 lda #$56 ;3:EAFD a956
DpNEAFF:
 jsr DpAudioRequest ;3:EAFF 20a898
DpNEB02:
 jmp DpNE96A ;3:EB02 4c6ae9
DpNEB05:
 lda DpContacts+0 ;3:EB05 ad0004
DpNEB08:
 jne DpNEB14 ;3:EB08 d00a
DpNEB0A:
 lda DpContacts+1 ;3:EB0A ad0104
DpNEB0D:
 jne DpNEB14 ;3:EB0D d005
DpNEB0F:
 lda DpPlatform+0 ;3:EB0F ad4604
DpNEB12:
 jpl DpNEB17 ;3:EB12 1003
DpNEB14:
 jmp DpNE9F7 ;3:EB14 4cf7e9
DpNEB17:
 lda DpKickAge ;3:EB17 a587
DpNEB19:
 cmp #$04 ;3:EB19 c904
DpNEB1B:
 jne DpNEB23 ;3:EB1B d006
DpNEB1D:
 jsr DpNEF3A ;3:EB1D 203aef
DpNEB20:
 jsr DpNEF9A ;3:EB20 209aef
DpNEB23:
 lda #$05 ;3:EB23 a905
DpNEB25:
 sta DpPose ;3:EB25 8530
DpNEB27:
 dec DpKickAge ;3:EB27 c687
DpNEB29:
 jne DpNEB2F ;3:EB29 d004
DpNEB2B:
 lda #$03 ;3:EB2B a903
DpNEB2D:
 sta DpAction ;3:EB2D 852d
DpNEB2F:
 jmp DpNE96A ;3:EB2F 4c6ae9
DpNEB32:
 lda DpHeld ;3:EB32 a5df
DpNEB34:
 and #$2f ;3:EB34 292f
DpNEB36:
 sta DpHeld ;3:EB36 85df
DpNEB38:
 lda DpFresh ;3:EB38 a5e0
DpNEB3A:
 and #$01 ;3:EB3A 2901
DpNEB3C:
 jeq DpNEB41 ;3:EB3C f003
DpNEB3E:
 jmp DpNE926 ;3:EB3E 4c26e9
DpNEB41:
 lda DpHeld ;3:EB41 a5df
DpNEB43:
 and #$20 ;3:EB43 2920
DpNEB45:
 jeq DpNEB14 ;3:EB45 f0cd
DpNEB47:
 lda DpActionFlags ;3:EB47 a532
DpNEB49:
 and #$01 ;3:EB49 2901
DpNEB4B:
 jeq DpNEB57 ;3:EB4B f00a
DpNEB4D:
 lda DpTimer ;3:EB4D a533
DpNEB4F:
 jne DpNEB5F ;3:EB4F d00e
DpNEB51:
 lda DpFresh ;3:EB51 a5e0
DpNEB53:
 and #$02 ;3:EB53 2902
DpNEB55:
 jne DpNEB5B ;3:EB55 d004
DpNEB57:
 lda #$09 ;3:EB57 a909
DpNEB59:
 jne DpNEB68 ;3:EB59 d00d
DpNEB5B:
 lda #$10 ;3:EB5B a910
DpNEB5D:
 sta DpTimer ;3:EB5D 8533
DpNEB5F:
 dec DpTimer ;3:EB5F c633
DpNEB61:
 jne DpNEB66 ;3:EB61 d003
DpNEB63:
 jsr DpNEF7B ;3:EB63 207bef
DpNEB66:
 lda #$0a ;3:EB66 a90a
DpNEB68:
 sta DpPose ;3:EB68 8530
DpNEB6A:
 jmp DpNE96A ;3:EB6A 4c6ae9
DpNEB6D:
 lda #$00 ;3:EB6D a900
DpNEB6F:
 sta DpProtection ;3:EB6F 852f
DpNEB71:
 lda DpHeld ;3:EB71 a5df
DpNEB73:
 and #$0c ;3:EB73 290c
DpNEB75:
 sta DpHeld ;3:EB75 85df
DpNEB77:
 lda #$0e ;3:EB77 a90e
DpNEB79:
 sta DpPose ;3:EB79 8530
DpNEB7B:
 lda #$00 ;3:EB7B a900
DpNEB7D:
 sta DpAttribute ;3:EB7D 8531
DpNEB7F:
 lda DpActionFlags ;3:EB7F a532
DpNEB81:
 jpl DpNEBC9 ;3:EB81 1046
DpNEB83:
 inc DpVertical ;3:EB83 e634
DpNEB85:
 lda DpVertical ;3:EB85 a534
DpNEB87:
 jpl DpNEB99 ;3:EB87 1010
DpNEB89:
 lda DpY ;3:EB89 a5f8
DpNEB8B:
 cmp #$10 ;3:EB8B c910
DpNEB8D:
 jcc DpNEB94 ;3:EB8D 9005
DpNEB8F:
 lda DpContacts+6 ;3:EB8F ad0604
DpNEB92:
 jeq DpNEB98 ;3:EB92 f004
DpNEB94:
 lda #$00 ;3:EB94 a900
DpNEB96:
 sta DpVertical ;3:EB96 8534
DpNEB98:
 rts ;3:EB98 60
DpNEB99:
 lda DpY ;3:EB99 a5f8
DpNEB9B:
 cmp #$10 ;3:EB9B c910
DpNEB9D:
 jcc DpNEB98 ;3:EB9D 90f9
DpNEB9F:
 lda DpContacts+0 ;3:EB9F ad0004
DpNEBA2:
 jne DpNEBAE ;3:EBA2 d00a
DpNEBA4:
 lda DpContacts+1 ;3:EBA4 ad0104
DpNEBA7:
 jne DpNEBAE ;3:EBA7 d005
DpNEBA9:
 lda DpPlatform+0 ;3:EBA9 ad4604
DpNEBAC:
 jpl DpNEB98 ;3:EBAC 10ea
DpNEBAE:
 lda #$67 ;3:EBAE a967
DpNEBB0:
 jsr DpAudioRequest ;3:EBB0 20a898
DpNEBB3:
 lda #$00 ;3:EBB3 a900
DpNEBB5:
 sta DpVertical ;3:EBB5 8534
DpNEBB7:
 sta DpTimer ;3:EBB7 8533
DpNEBB9:
 lda DpActionFlags ;3:EBB9 a532
DpNEBBB:
 clc ;3:EBBB 18
DpNEBBC:
 adc #$10 ;3:EBBC 6910
DpNEBBE:
 and #$7f ;3:EBBE 297f
DpNEBC0:
 sta DpActionFlags ;3:EBC0 8532
DpNEBC2:
 cmp #$60 ;3:EBC2 c960
DpNEBC4:
 jcc DpNEBC9 ;3:EBC4 9003
DpNEBC6:
 jmp DpSceneExitRequest ;3:EBC6 4c4d98
DpNEBC9:
 inc DpTimer ;3:EBC9 e633
DpNEBCB:
 lda DpTimer ;3:EBCB a533
DpNEBCD:
 cmp #$08 ;3:EBCD c908
DpNEBCF:
 jcc DpNEBE0 ;3:EBCF 900f
DpNEBD1:
 lda DpActionFlags ;3:EBD1 a532
DpNEBD3:
 ora #$80 ;3:EBD3 0980
DpNEBD5:
 sta DpActionFlags ;3:EBD5 8532
DpNEBD7:
 lda #$e8 ;3:EBD7 a9e8
DpNEBD9:
 sta DpVertical ;3:EBD9 8534
DpNEBDB:
 lda #$30 ;3:EBDB a930
DpNEBDD:
 jsr DpAudioRequest ;3:EBDD 20a898
DpNEBE0:
 rts ;3:EBE0 60
DpNEBE1:
 lda #$0b ;3:EBE1 a90b
DpNEBE3:
 sta DpPose ;3:EBE3 8530
DpNEBE5:
 lda DpTimer ;3:EBE5 a533
DpNEBE7:
 jpl DpNEBF9 ;3:EBE7 1010
DpNEBE9:
 dec DpTimer ;3:EBE9 c633
DpNEBEB:
 lda DpTimer ;3:EBEB a533
DpNEBED:
 and #$7f ;3:EBED 297f
DpNEBEF:
 jeq DpNEBF8 ;3:EBEF f007
DpNEBF1:
 lda #$01 ;3:EBF1 a901
DpNEBF3:
 sta DpAction ;3:EBF3 852d
DpNEBF5:
 lsr a ;3:EBF5 4a
DpNEBF6:
 sta DpTimer ;3:EBF6 8533
DpNEBF8:
 rts ;3:EBF8 60
DpNEBF9:
 lda DpHP ;3:EBF9 a52e
DpNEBFB:
 jeq DpNEC01 ;3:EBFB f004
DpNEBFD:
 lda #$8f ;3:EBFD a98f
DpNEBFF:
 sta DpTimer ;3:EBFF 8533
DpNEC01:
 rts ;3:EC01 60
DpNEC02:
 lda DpAction ;3:EC02 a52d
DpNEC04:
 cmp #$0f ;3:EC04 c90f
DpNEC06:
 jeq DpNEC16 ;3:EC06 f00e
DpNEC08:
 lda DpHP ;3:EC08 a52e
DpNEC0A:
 jne DpNEC16 ;3:EC0A d00a
DpNEC0C:
 sta DpVertical ;3:EC0C 8534
DpNEC0E:
 lda #$ff ;3:EC0E a9ff
DpNEC10:
 sta DpTimer ;3:EC10 8533
DpNEC12:
 lda #$0f ;3:EC12 a90f
DpNEC14:
 sta DpAction ;3:EC14 852d
DpNEC16:
 rts ;3:EC16 60
DpNEC17:
 lda #$0b ;3:EC17 a90b
DpNEC19:
 sta DpPose ;3:EC19 8530
DpNEC1B:
 dec DpTimer ;3:EC1B c633
DpNEC1D:
 lda DpTimer ;3:EC1D a533
DpNEC1F:
 and #$7f ;3:EC1F 297f
DpNEC21:
 jeq DpNEC40 ;3:EC21 f01d
DpNEC23:
 lda DpContacts+0 ;3:EC23 ad0004
DpNEC26:
 jne DpNEC32 ;3:EC26 d00a
DpNEC28:
 lda DpContacts+1 ;3:EC28 ad0104
DpNEC2B:
 jne DpNEC32 ;3:EC2B d005
DpNEC2D:
 lda DpPlatform+0 ;3:EC2D ad4604
DpNEC30:
 jpl DpNEC3D ;3:EC30 100b
DpNEC32:
 lda #$00 ;3:EC32 a900
DpNEC34:
 sta DpVertical ;3:EC34 8534
DpNEC36:
 lda DpY ;3:EC36 a5f8
DpNEC38:
 and #$f8 ;3:EC38 29f8
DpNEC3A:
 sta DpY ;3:EC3A 85f8
DpNEC3C:
 rts ;3:EC3C 60
DpNEC3D:
 inc DpY ;3:EC3D e6f8
DpNEC3F:
 rts ;3:EC3F 60
DpNEC40:
 lda #$80 ;3:EC40 a980
DpNEC42:
 sta DpExit ;3:EC42 8542
DpNEC44:
 rts ;3:EC44 60
DpNEC45:
 lda #$80 ;3:EC45 a980
DpNEC47:
 sta DpPlatform+3 ;3:EC47 8d4904
DpNEC4A:
 pla ;3:EC4A 68
DpNEC4B:
 pla ;3:EC4B 68
DpNEC4C:
 rts ;3:EC4C 60
DpNEC4D:
 lda DpShotState ;3:EC4D a53a
DpNEC4F:
 and #$0f ;3:EC4F 290f
DpNEC51:
 asl a ;3:EC51 0a
DpNEC52:
 tay ;3:EC52 a8
DpNEC53:
 lda DpNEC60,y ;3:EC53 b960ec
DpNEC56:
 sta R0 ;3:EC56 8500
DpNEC58:
 lda DpNEC60+1,y ;3:EC58 b961ec
DpNEC5B:
 sta R1 ;3:EC5B 8501
DpNEC5D:
 jmp (R0) ;3:EC5D 6c0000
DpNEC60:
 .word DpNEC68,DpNEC8A,DpNEC97,DpNECA2
DpNEC68:
 lda DpActionFlags ;3:EC68 a532
DpNEC6A:
 and #$c0 ;3:EC6A 29c0
DpNEC6C:
 sta DpShotState ;3:EC6C 853a
DpNEC6E:
 jmi DpNEC78 ;3:EC6E 3008
DpNEC70:
 lda DpX ;3:EC70 a5f7
DpNEC72:
 clc ;3:EC72 18
DpNEC73:
 adc #$08 ;3:EC73 6908
DpNEC75:
 jmp DpNEC7D ;3:EC75 4c7dec
DpNEC78:
 lda DpX ;3:EC78 a5f7
DpNEC7A:
 sec ;3:EC7A 38
DpNEC7B:
 sbc #$08 ;3:EC7B e908
DpNEC7D:
 sta DpShotX ;3:EC7D 853e
DpNEC7F:
 lda DpY ;3:EC7F a5f8
DpNEC81:
 sta DpShotY ;3:EC81 853c
DpNEC83:
 lda #$00 ;3:EC83 a900
DpNEC85:
 sta DpShotXPage ;3:EC85 853f
DpNEC87:
 sta DpShotYPage ;3:EC87 853d
DpNEC89:
 rts ;3:EC89 60
DpNEC8A:
 ldy #$82 ;3:EC8A a082
DpNEC8C:
 lda DpHorizontal ;3:EC8C a535
DpNEC8E:
 jpl DpNEC92 ;3:EC8E 1002
DpNEC90:
 ldy #$43 ;3:EC90 a043
DpNEC92:
 sty DpShotState ;3:EC92 843a
DpNEC94:
 jmp DpNEC4D ;3:EC94 4c4dec
DpNEC97:
 lda DpShotX ;3:EC97 a53e
DpNEC99:
 clc ;3:EC99 18
DpNEC9A:
 adc #$07 ;3:EC9A 6907
DpNEC9C:
 sta DpShotX ;3:EC9C 853e
DpNEC9E:
 jcs DpNECB5 ;3:EC9E b015
DpNECA0:
 jcc DpNECAB ;3:ECA0 9009
DpNECA2:
 lda DpShotX ;3:ECA2 a53e
DpNECA4:
 sec ;3:ECA4 38
DpNECA5:
 sbc #$07 ;3:ECA5 e907
DpNECA7:
 sta DpShotX ;3:ECA7 853e
DpNECA9:
 jcc DpNECB5 ;3:ECA9 900a
DpNECAB:
 lda DpShotX ;3:ECAB a53e
DpNECAD:
 cmp #$f8 ;3:ECAD c9f8
DpNECAF:
 jcs DpNECB5 ;3:ECAF b004
DpNECB1:
 cmp #$08 ;3:ECB1 c908
DpNECB3:
 jcs DpNECB9 ;3:ECB3 b004
DpNECB5:
 lda #$00 ;3:ECB5 a900
DpNECB7:
 sta DpShotState ;3:ECB7 853a
DpNECB9:
 rts ;3:ECB9 60
DpNED1C:
 sta R0 ;3:ED1C 8500
DpNED1E:
 tya ;3:ED1E 98
DpNED1F:
 clc ;3:ED1F 18
DpNED20:
 adc DpX ;3:ED20 65f7
DpNED22:
 sta DpMath+14 ;3:ED22 850e
DpNED24:
 tay ;3:ED24 a8
DpNED25:
 lda DpY ;3:ED25 a5f8
DpNED27:
 clc ;3:ED27 18
DpNED28:
 adc R0 ;3:ED28 6500
DpNED2A:
 sta DpMath+15 ;3:ED2A 850f
 jmp DpHostTileQuery ; genuine original fall-through crosses projected boundary
DpNED45:
 sta R0 ;3:ED45 8500
DpNED47:
 tya ;3:ED47 98
DpNED48:
 clc ;3:ED48 18
DpNED49:
 adc DpX ;3:ED49 65f7
DpNED4B:
 tay ;3:ED4B a8
DpNED4C:
 lda DpY ;3:ED4C a5f8
DpNED4E:
 clc ;3:ED4E 18
DpNED4F:
 adc R0 ;3:ED4F 6500
DpNED51:
 jsr DpHostTileQuery ;3:ED51 202ced
DpNED54:
 cmp #$10 ;3:ED54 c910
DpNED56:
 jcc DpNED72 ;3:ED56 901a
DpNED58:
 cmp #$13 ;3:ED58 c913
DpNED5A:
 jcc DpNED75 ;3:ED5A 9019
DpNED5C:
 cmp #$85 ;3:ED5C c985
DpNED5E:
 jeq DpNED72 ;3:ED5E f012
DpNED60:
 cmp #$75 ;3:ED60 c975
DpNED62:
 jcc DpNED72 ;3:ED62 900e
DpNED64:
 cmp #$95 ;3:ED64 c995
DpNED66:
 jcc DpNED7A ;3:ED66 9012
DpNED68:
 cmp #$a0 ;3:ED68 c9a0
DpNED6A:
 jcc DpNED7D ;3:ED6A 9011
DpNED6C:
 cmp #$c0 ;3:ED6C c9c0
DpNED6E:
 jcs DpNED7A ;3:ED6E b00a
DpNED70:
 jcc DpNED7F ;3:ED70 900d
DpNED72:
 lda #$00 ;3:ED72 a900
DpNED74:
 rts ;3:ED74 60
DpNED75:
 lda #$80 ;3:ED75 a980
DpNED77:
 sta DpPlatform+4 ;3:ED77 8d4a04
DpNED7A:
 lda #$01 ;3:ED7A a901
DpNED7C:
 rts ;3:ED7C 60
DpNED7D:
 lda #$02 ;3:ED7D a902
DpNED7F:
 rts ;3:ED7F 60
DpNED80:
 tay ;3:ED80 a8
DpNED81:
 jpl DpNED7F ;3:ED81 10fc
DpNED83:
 and #$0f ;3:ED83 290f
DpNED85:
 cmp #$04 ;3:ED85 c904
DpNED87:
 jcc DpNED72 ;3:ED87 90e9
DpNED89:
 cmp #$06 ;3:ED89 c906
DpNED8B:
 jeq DpNED72 ;3:ED8B f0e5
DpNED8D:
 cmp #$08 ;3:ED8D c908
DpNED8F:
 jeq DpNED7A ;3:ED8F f0e9
DpNED91:
 lda DpMath+3 ;3:ED91 a503
DpNED93:
 and #$0f ;3:ED93 290f
DpNED95:
 cmp #$08 ;3:ED95 c908
DpNED97:
 jcc DpNED72 ;3:ED97 90d9
DpNED99:
 jcs DpNED7A ;3:ED99 b0df
DpNED9B:
 tay ;3:ED9B a8
DpNED9C:
 jpl DpNED7F ;3:ED9C 10e1
DpNED9E:
 and #$0f ;3:ED9E 290f
DpNEDA0:
 cmp #$06 ;3:EDA0 c906
DpNEDA2:
 jeq DpNED72 ;3:EDA2 f0ce
DpNEDA4:
 cmp #$04 ;3:EDA4 c904
DpNEDA6:
 jcc DpNED72 ;3:EDA6 90ca
DpNEDA8:
 cmp #$08 ;3:EDA8 c908
DpNEDAA:
 jne DpNED91 ;3:EDAA d0e5
DpNEDAC:
 jeq DpNEDBF ;3:EDAC f011
DpNEDAE:
 tay ;3:EDAE a8
DpNEDAF:
 jpl DpNED7F ;3:EDAF 10ce
DpNEDB1:
 and #$0f ;3:EDB1 290f
DpNEDB3:
 cmp #$04 ;3:EDB3 c904
DpNEDB5:
 jcc DpNED72 ;3:EDB5 90bb
DpNEDB7:
 cmp #$06 ;3:EDB7 c906
DpNEDB9:
 jeq DpNED72 ;3:EDB9 f0b7
DpNEDBB:
 cmp #$08 ;3:EDBB c908
DpNEDBD:
 jne DpNED7A ;3:EDBD d0bb
DpNEDBF:
 lda DpMath+3 ;3:EDBF a503
DpNEDC1:
 and #$0f ;3:EDC1 290f
DpNEDC3:
 cmp #$08 ;3:EDC3 c908
DpNEDC5:
 jcs DpNED72 ;3:EDC5 b0ab
DpNEDC7:
 jcc DpNED7A ;3:EDC7 90b1
DpNEDC9:
 ldy #$02 ;3:EDC9 a002
DpNEDCB:
 lda #$10 ;3:EDCB a910
DpNEDCD:
 jsr DpNED45 ;3:EDCD 2045ed
DpNEDD0:
 jsr DpNED80 ;3:EDD0 2080ed
DpNEDD3:
 sta DpContacts+0 ;3:EDD3 8d0004
DpNEDD6:
 ldy #$0e ;3:EDD6 a00e
DpNEDD8:
 lda #$10 ;3:EDD8 a910
DpNEDDA:
 jsr DpNED45 ;3:EDDA 2045ed
DpNEDDD:
 jsr DpNED80 ;3:EDDD 2080ed
DpNEDE0:
 sta DpContacts+1 ;3:EDE0 8d0104
DpNEDE3:
 ldy #$00 ;3:EDE3 a000
DpNEDE5:
 lda #$0e ;3:EDE5 a90e
DpNEDE7:
 jsr DpNED45 ;3:EDE7 2045ed
DpNEDEA:
 jsr DpNED9B ;3:EDEA 209bed
DpNEDED:
 sta DpContacts+2 ;3:EDED 8d0204
DpNEDF0:
 ldy #$10 ;3:EDF0 a010
DpNEDF2:
 lda #$0e ;3:EDF2 a90e
DpNEDF4:
 jsr DpNED45 ;3:EDF4 2045ed
DpNEDF7:
 jsr DpNED9B ;3:EDF7 209bed
DpNEDFA:
 sta DpContacts+3 ;3:EDFA 8d0304
DpNEDFD:
 ldy #$00 ;3:EDFD a000
DpNEDFF:
 lda #$fe ;3:EDFF a9fe
DpNEE01:
 jsr DpNED45 ;3:EE01 2045ed
DpNEE04:
 jsr DpNED9B ;3:EE04 209bed
DpNEE07:
 sta DpContacts+4 ;3:EE07 8d0404
DpNEE0A:
 ldy #$10 ;3:EE0A a010
DpNEE0C:
 lda #$fe ;3:EE0C a9fe
DpNEE0E:
 jsr DpNED45 ;3:EE0E 2045ed
DpNEE11:
 jsr DpNED9B ;3:EE11 209bed
DpNEE14:
 sta DpContacts+5 ;3:EE14 8d0504
DpNEE17:
 ldy #$08 ;3:EE17 a008
DpNEE19:
 lda #$f0 ;3:EE19 a9f0
DpNEE1B:
 jsr DpNED45 ;3:EE1B 2045ed
DpNEE1E:
 jsr DpNEDAE ;3:EE1E 20aeed
DpNEE21:
 sta DpContacts+6 ;3:EE21 8d0604
DpNEE24:
 rts ;3:EE24 60
DpNEE25:
 lda DpAction ;3:EE25 a52d
DpNEE27:
 asl a ;3:EE27 0a
DpNEE28:
 tay ;3:EE28 a8
DpNEE29:
 lda DpNEE36,y ;3:EE29 b936ee
DpNEE2C:
 sta R0 ;3:EE2C 8500
DpNEE2E:
 lda DpNEE36+1,y ;3:EE2E b937ee
DpNEE31:
 sta R1 ;3:EE31 8501
DpNEE33:
 jmp (R0) ;3:EE33 6c0000
DpNEE36:
 .word DpNEE66,DpNEE56,DpNEE66,DpNEE59,DpNEE66,DpNEE66,DpNEE66,DpNEE66,DpNEE66,DpNEE66,DpNEE59,DpNEE59,DpNEE66,DpNEE5F,DpNEE66,DpNEE5F
DpNEE56:
 jmp DpNEE70 ;3:EE56 4c70ee
DpNEE59:
 jsr DpNEE70 ;3:EE59 2070ee
DpNEE5C:
 jmp DpNEECB ;3:EE5C 4ccbee
DpNEE5F:
 lda DpActionFlags ;3:EE5F a532
DpNEE61:
 jpl DpNEE66 ;3:EE61 1003
DpNEE63:
 jsr DpNEECB ;3:EE63 20cbee
DpNEE66:
 rts ;3:EE66 60
DpNEE67:
 lda DpHorizontal ;3:EE67 a535
DpNEE69:
 clc ;3:EE69 18
DpNEE6A:
 adc #$04 ;3:EE6A 6904
DpNEE6C:
 sta DpHorizontal ;3:EE6C 8535
DpNEE6E:
 jne DpNEE82 ;3:EE6E d012
DpNEE70:
 lda DpHeld ;3:EE70 a5df
DpNEE72:
 and #$c0 ;3:EE72 29c0
DpNEE74:
 jeq DpNEE82 ;3:EE74 f00c
DpNEE76:
 lda DpPlatform+4 ;3:EE76 ad4a04
DpNEE79:
 jmi DpNEE67 ;3:EE79 30ec
DpNEE7B:
 lda DpHorizontal ;3:EE7B a535
DpNEE7D:
 clc ;3:EE7D 18
DpNEE7E:
 adc #$14 ;3:EE7E 6914
DpNEE80:
 sta DpHorizontal ;3:EE80 8535
DpNEE82:
 lda DpHorizontal ;3:EE82 a535
DpNEE84:
 pha ;3:EE84 48
DpNEE85:
 and #$8f ;3:EE85 298f
DpNEE87:
 sta DpHorizontal ;3:EE87 8535
DpNEE89:
 pla ;3:EE89 68
DpNEE8A:
 and #$70 ;3:EE8A 2970
DpNEE8C:
 lsr a ;3:EE8C 4a
DpNEE8D:
 lsr a ;3:EE8D 4a
DpNEE8E:
 lsr a ;3:EE8E 4a
DpNEE8F:
 lsr a ;3:EE8F 4a
DpNEE90:
 sta R0 ;3:EE90 8500
DpNEE92:
 lda DpHorizontal ;3:EE92 a535
DpNEE94:
 jmi DpNEEB1 ;3:EE94 301b
DpNEE96:
 lda DpContacts+3 ;3:EE96 ad0304
DpNEE99:
 jne DpNEEAE ;3:EE99 d013
DpNEE9B:
 lda DpContacts+5 ;3:EE9B ad0504
DpNEE9E:
 jne DpNEEAE ;3:EE9E d00e
DpNEEA0:
 lda DpX ;3:EEA0 a5f7
DpNEEA2:
 cmp #$f7 ;3:EEA2 c9f7
DpNEEA4:
 jcs DpNEEAD ;3:EEA4 b007
DpNEEA6:
 lda DpX ;3:EEA6 a5f7
DpNEEA8:
 clc ;3:EEA8 18
DpNEEA9:
 adc R0 ;3:EEA9 6500
DpNEEAB:
 sta DpX ;3:EEAB 85f7
DpNEEAD:
 rts ;3:EEAD 60
DpNEEAE:
 dec DpX ;3:EEAE c6f7
DpNEEB0:
 rts ;3:EEB0 60
DpNEEB1:
 lda DpContacts+2 ;3:EEB1 ad0204
DpNEEB4:
 jne DpNEEC8 ;3:EEB4 d012
DpNEEB6:
 lda DpContacts+4 ;3:EEB6 ad0404
DpNEEB9:
 jne DpNEEC8 ;3:EEB9 d00d
DpNEEBB:
 lda DpX ;3:EEBB a5f7
DpNEEBD:
 cmp #$09 ;3:EEBD c909
DpNEEBF:
 jcc DpNEEAD ;3:EEBF 90ec
DpNEEC1:
 lda DpX ;3:EEC1 a5f7
DpNEEC3:
 sbc R0 ;3:EEC3 e500
DpNEEC5:
 sta DpX ;3:EEC5 85f7
DpNEEC7:
 rts ;3:EEC7 60
DpNEEC8:
 inc DpX ;3:EEC8 e6f7
DpNEECA:
 rts ;3:EECA 60
DpNEECB:
 lda DpVertical ;3:EECB a534
DpNEECD:
 jpl DpNEEE4 ;3:EECD 1015
DpNEECF:
 cmp #$f8 ;3:EECF c9f8
DpNEED1:
 jcs DpNEEE1 ;3:EED1 b00e
DpNEED3:
 cmp #$f4 ;3:EED3 c9f4
DpNEED5:
 jcs DpNEEDF ;3:EED5 b008
DpNEED7:
 cmp #$f0 ;3:EED7 c9f0
DpNEED9:
 jcs DpNEEDD ;3:EED9 b002
DpNEEDB:
 dec DpY ;3:EEDB c6f8
DpNEEDD:
 dec DpY ;3:EEDD c6f8
DpNEEDF:
 dec DpY ;3:EEDF c6f8
DpNEEE1:
 dec DpY ;3:EEE1 c6f8
DpNEEE3:
 rts ;3:EEE3 60
DpNEEE4:
 cmp #$08 ;3:EEE4 c908
DpNEEE6:
 jcc DpNEEF6 ;3:EEE6 900e
DpNEEE8:
 cmp #$0c ;3:EEE8 c90c
DpNEEEA:
 jcc DpNEEF4 ;3:EEEA 9008
DpNEEEC:
 cmp #$10 ;3:EEEC c910
DpNEEEE:
 jcc DpNEEF2 ;3:EEEE 9002
DpNEEF0:
 inc DpY ;3:EEF0 e6f8
DpNEEF2:
 inc DpY ;3:EEF2 e6f8
DpNEEF4:
 inc DpY ;3:EEF4 e6f8
DpNEEF6:
 inc DpY ;3:EEF6 e6f8
DpNEEF8:
 rts ;3:EEF8 60
DpNEEF9:
 ldx #$00 ;3:EEF9 a200
DpNEEFB:
 lda DpContacts+7,x ;3:EEFB bd0704
DpNEEFE:
 jpl DpNEF03 ;3:EEFE 1003
DpNEF00:
 jmp DpNEF7A ;3:EF00 4c7aef
DpNEF03:
 ldy #$08 ;3:EF03 a008
DpNEF05:
 lda #$e8 ;3:EF05 a9e8
DpNEF07:
 jsr DpNED1C ;3:EF07 201ced
DpNEF0A:
 jmp DpNEF59 ;3:EF0A 4c59ef
DpNEF0D:
 lda DpPlatform+2 ;3:EF0D ad4804
DpNEF10:
 and #$7f ;3:EF10 297f
DpNEF12:
 jne DpNEF1B ;3:EF12 d007
DpNEF14:
 ldx #$00 ;3:EF14 a200
DpNEF16:
 lda DpContacts+7,x ;3:EF16 bd0704
DpNEF19:
 jpl DpNEF1E ;3:EF19 1003
DpNEF1B:
 jmp DpNEF7A ;3:EF1B 4c7aef
DpNEF1E:
 ldy #$08 ;3:EF1E a008
DpNEF20:
 lda #$14 ;3:EF20 a914
DpNEF22:
 jsr DpNED1C ;3:EF22 201ced
DpNEF25:
 tay ;3:EF25 a8
DpNEF26:
 cmp #$95 ;3:EF26 c995
DpNEF28:
 jcc DpNEF36 ;3:EF28 900c
DpNEF2A:
 cmp #$9b ;3:EF2A c99b
DpNEF2C:
 jcs DpNEF36 ;3:EF2C b008
DpNEF2E:
 lda DpPlatform+2 ;3:EF2E ad4804
DpNEF31:
 ora #$1f ;3:EF31 091f
DpNEF33:
 sta DpPlatform+2 ;3:EF33 8d4804
DpNEF36:
 tya ;3:EF36 98
DpNEF37:
 jmp DpNEF59 ;3:EF37 4c59ef
DpNEF3A:
 ldx #$00 ;3:EF3A a200
DpNEF3C:
 lda DpContacts+7,x ;3:EF3C bd0704
DpNEF3F:
 jpl DpNEF44 ;3:EF3F 1003
DpNEF41:
 jmp DpNEF7A ;3:EF41 4c7aef
DpNEF44:
 lda DpHorizontal ;3:EF44 a535
DpNEF46:
 jmi DpNEF52 ;3:EF46 300a
DpNEF48:
 ldy #$18 ;3:EF48 a018
DpNEF4A:
 lda #$08 ;3:EF4A a908
DpNEF4C:
 jsr DpNED1C ;3:EF4C 201ced
DpNEF4F:
 jmp DpNEF59 ;3:EF4F 4c59ef
DpNEF52:
 ldy #$f8 ;3:EF52 a0f8
DpNEF54:
 lda #$08 ;3:EF54 a908
DpNEF56:
 jsr DpNED1C ;3:EF56 201ced
DpNEF59:
 cmp #$95 ;3:EF59 c995
DpNEF5B:
 jcc DpNEF7A ;3:EF5B 901d
DpNEF5D:
 cmp #$9b ;3:EF5D c99b
DpNEF5F:
 jcs DpNEF7A ;3:EF5F b019
DpNEF61:
 sta DpContacts+11,x ;3:EF61 9d0b04
DpNEF64:
 lda DpMath+15 ;3:EF64 a50f
DpNEF66:
 and #$f0 ;3:EF66 29f0
DpNEF68:
 sta R0 ;3:EF68 8500
DpNEF6A:
 lda DpMath+14 ;3:EF6A a50e
DpNEF6C:
 lsr a ;3:EF6C 4a
DpNEF6D:
 lsr a ;3:EF6D 4a
DpNEF6E:
 lsr a ;3:EF6E 4a
DpNEF6F:
 lsr a ;3:EF6F 4a
DpNEF70:
 ora R0 ;3:EF70 0500
DpNEF72:
 sta DpContacts+9,x ;3:EF72 9d0904
DpNEF75:
 lda #$80 ;3:EF75 a980
DpNEF77:
 sta DpContacts+7,x ;3:EF77 9d0704
DpNEF7A:
 rts ;3:EF7A 60
DpNEF7B:
 ldx #$00 ;3:EF7B a200
DpNEF7D:
 lda DpContacts+7,x ;3:EF7D bd0704
DpNEF80:
 jmi DpNEF7A ;3:EF80 30f8
DpNEF82:
 lda DpHorizontal ;3:EF82 a535
DpNEF84:
 jmi DpNEF90 ;3:EF84 300a
DpNEF86:
 ldy #$10 ;3:EF86 a010
DpNEF88:
 lda #$18 ;3:EF88 a918
DpNEF8A:
 jsr DpNED1C ;3:EF8A 201ced
DpNEF8D:
 jmp DpNEF59 ;3:EF8D 4c59ef
DpNEF90:
 ldy #$00 ;3:EF90 a000
DpNEF92:
 lda #$18 ;3:EF92 a918
DpNEF94:
 jsr DpNED1C ;3:EF94 201ced
DpNEF97:
 jmp DpNEF59 ;3:EF97 4c59ef
DpNEF9A:
 ldx #$01 ;3:EF9A a201
DpNEF9C:
 lda DpContacts+7,x ;3:EF9C bd0704
DpNEF9F:
 jmi DpNEF7A ;3:EF9F 30d9
DpNEFA1:
 lda DpHorizontal ;3:EFA1 a535
DpNEFA3:
 jmi DpNEFAF ;3:EFA3 300a
DpNEFA5:
 ldy #$18 ;3:EFA5 a018
DpNEFA7:
 lda #$f8 ;3:EFA7 a9f8
DpNEFA9:
 jsr DpNED1C ;3:EFA9 201ced
DpNEFAC:
 jmp DpNEF59 ;3:EFAC 4c59ef
DpNEFAF:
 ldy #$f8 ;3:EFAF a0f8
DpNEFB1:
 lda #$f8 ;3:EFB1 a9f8
DpNEFB3:
 jsr DpNED1C ;3:EFB3 201ced
DpNEFB6:
 jmp DpNEF59 ;3:EFB6 4c59ef
DpNativeEnd:
.export DpNE82E,DpNE906,DpNE99A,DpNE9B3,DpNEA20,DpNEA3D,DpNEC4D,DpNEE70,DpNEECB
.popseg
