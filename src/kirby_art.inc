; Original native Kirby pixels/OAM; fixed native SMB upper halves unchanged.
.pushseg
.segment "KIRBY_GFX"
KbArtStart:
KbBodyChr:
 .byte 84,84,84,84,84,84,84,84,84,84,84,84
 .byte 84,84,84,84,84,84,84,84,84,84,86,86
 .byte 86,86,86,86,86,86,86,86,86,86,86,86
 .byte 86,86,86,86,86,86,86,86,86,86,84,84
 .byte 88,88,88,88,88,88,88,88,88,88,88,88
 .byte 88,88,88,88,88,88,90,90,90,90,90,90
 .byte 86,86,90,90,90,90,90,90,92,92,92,92
 .byte 92,92,90,90,92,92,92,92,92,92,92,92
 .byte 92,92,90,90,90,90,94,94,90,90,94,94
 .byte 94,94,94,94,94,94,94,94,94,94,94,94
 .byte 94,94
KbBodyLo:
 .byte <KbBody00,<KbBody01,<KbBody02,<KbBody03,<KbBody04,<KbBody05,<KbBody06,<KbBody07,<KbBody08,<KbBody09,<KbBody0a,<KbBody0b
 .byte <KbBody0c,<KbBody0d,<KbBody0e,<KbBody0f,<KbBody10,<KbBody11,<KbBody12,<KbBody13,<KbBody14,<KbBody15,<KbBody16,<KbBody17
 .byte <KbBody18,<KbBody19,<KbBody1a,<KbBody1b,<KbBody1c,<KbBody1d,<KbBody1e,<KbBody1f,<KbBody20,<KbBody21,<KbBody22,<KbBody23
 .byte <KbBody24,<KbBody25,<KbBody26,<KbBody27,<KbBody28,<KbBody29,<KbBody2a,<KbBody2b,<KbBody2c,<KbBody2d,<KbBody2e,<KbBody2f
 .byte <KbBody30,<KbBody31,<KbBody32,<KbBody33,<KbBody34,<KbBody35,<KbBody36,<KbBody37,<KbBody38,<KbBody39,<KbBody3a,<KbBody3b
 .byte <KbBody3c,<KbBody3d,<KbBody3e,<KbBody3f,<KbBody40,<KbBody41,<KbBody42,<KbBody43,<KbBody44,<KbBody45,<KbBody46,<KbBody47
 .byte <KbBody48,<KbBody49,<KbBody4a,<KbBody4b,<KbBody4c,<KbBody4d,<KbBody4e,<KbBody4f,<KbBody50,<KbBody51,<KbBody52,<KbBody53
 .byte <KbBody54,<KbBody55,<KbBody56,<KbBody57,<KbBody58,<KbBody59,<KbBody5a,<KbBody5b,<KbBody5c,<KbBody5d,<KbBody5e,<KbBody5f
 .byte <KbBody60,<KbBody61,<KbBody62,<KbBody63,<KbBody64,<KbBody65,<KbBody66,<KbBody67,<KbBody68,<KbBody69,<KbBody6a,<KbBody6b
 .byte <KbBody6c,<KbBody6d,<KbBody6e,<KbBody6f,<KbBody70,<KbBody71,<KbBody72,<KbBody73,<KbBody74,<KbBody75,<KbBody76,<KbBody77
 .byte <KbBody78,<KbBody79
KbBodyHi:
 .byte >KbBody00,>KbBody01,>KbBody02,>KbBody03,>KbBody04,>KbBody05,>KbBody06,>KbBody07,>KbBody08,>KbBody09,>KbBody0a,>KbBody0b
 .byte >KbBody0c,>KbBody0d,>KbBody0e,>KbBody0f,>KbBody10,>KbBody11,>KbBody12,>KbBody13,>KbBody14,>KbBody15,>KbBody16,>KbBody17
 .byte >KbBody18,>KbBody19,>KbBody1a,>KbBody1b,>KbBody1c,>KbBody1d,>KbBody1e,>KbBody1f,>KbBody20,>KbBody21,>KbBody22,>KbBody23
 .byte >KbBody24,>KbBody25,>KbBody26,>KbBody27,>KbBody28,>KbBody29,>KbBody2a,>KbBody2b,>KbBody2c,>KbBody2d,>KbBody2e,>KbBody2f
 .byte >KbBody30,>KbBody31,>KbBody32,>KbBody33,>KbBody34,>KbBody35,>KbBody36,>KbBody37,>KbBody38,>KbBody39,>KbBody3a,>KbBody3b
 .byte >KbBody3c,>KbBody3d,>KbBody3e,>KbBody3f,>KbBody40,>KbBody41,>KbBody42,>KbBody43,>KbBody44,>KbBody45,>KbBody46,>KbBody47
 .byte >KbBody48,>KbBody49,>KbBody4a,>KbBody4b,>KbBody4c,>KbBody4d,>KbBody4e,>KbBody4f,>KbBody50,>KbBody51,>KbBody52,>KbBody53
 .byte >KbBody54,>KbBody55,>KbBody56,>KbBody57,>KbBody58,>KbBody59,>KbBody5a,>KbBody5b,>KbBody5c,>KbBody5d,>KbBody5e,>KbBody5f
 .byte >KbBody60,>KbBody61,>KbBody62,>KbBody63,>KbBody64,>KbBody65,>KbBody66,>KbBody67,>KbBody68,>KbBody69,>KbBody6a,>KbBody6b
 .byte >KbBody6c,>KbBody6d,>KbBody6e,>KbBody6f,>KbBody70,>KbBody71,>KbBody72,>KbBody73,>KbBody74,>KbBody75,>KbBody76,>KbBody77
 .byte >KbBody78,>KbBody79
KbBody00:
 .byte 8
 .byte 28,0,15,0
 .byte 30,0,15,8
KbBody01:
 .byte 8
 .byte 28,64,15,8
 .byte 30,64,15,0
KbBody02:
 .byte 8
 .byte 28,0,15,0
 .byte 32,0,15,8
KbBody03:
 .byte 8
 .byte 28,64,15,8
 .byte 32,64,15,0
KbBody04:
 .byte 8
 .byte 34,0,17,8
 .byte 36,0,17,0
KbBody05:
 .byte 8
 .byte 38,0,17,8
 .byte 40,0,17,0
KbBody06:
 .byte 8
 .byte 40,64,17,8
 .byte 38,64,17,0
KbBody07:
 .byte 8
 .byte 36,64,17,8
 .byte 34,64,17,0
KbBody08:
 .byte 12
 .byte 42,0,31,0
 .byte 44,0,15,0
 .byte 12,0,15,8
KbBody09:
 .byte 12
 .byte 42,0,31,0
 .byte 46,0,15,8
 .byte 18,0,15,0
KbBody0a:
 .byte 12
 .byte 42,64,31,8
 .byte 46,64,15,0
 .byte 18,64,15,8
KbBody0b:
 .byte 12
 .byte 42,64,31,8
 .byte 44,64,15,8
 .byte 12,64,15,0
KbBody0c:
 .byte 8
 .byte 48,0,7,0
 .byte 50,0,7,8
KbBody0d:
 .byte 8
 .byte 48,64,7,8
 .byte 50,64,7,0
KbBody0e:
 .byte 4
 .byte 52,0,15,8
KbBody0f:
 .byte 4
 .byte 52,64,15,8
KbBody10:
 .byte 4
 .byte 52,0,15,0
KbBody11:
 .byte 4
 .byte 52,64,15,0
KbBody12:
 .byte 8
 .byte 54,0,15,0
 .byte 56,0,15,8
KbBody13:
 .byte 8
 .byte 54,64,15,8
 .byte 56,64,15,0
KbBody14:
 .byte 8
 .byte 58,0,15,0
 .byte 60,0,15,8
KbBody15:
 .byte 8
 .byte 58,64,15,8
 .byte 60,64,15,0
KbBody16:
 .byte 8
 .byte 28,0,15,0
 .byte 30,0,15,8
KbBody17:
 .byte 8
 .byte 28,64,15,8
 .byte 30,64,15,0
KbBody18:
 .byte 12
 .byte 32,0,31,0
 .byte 34,0,15,8
 .byte 36,0,15,0
KbBody19:
 .byte 12
 .byte 32,64,31,8
 .byte 36,64,15,8
 .byte 34,64,15,0
KbBody1a:
 .byte 8
 .byte 38,0,13,8
 .byte 40,0,13,0
KbBody1b:
 .byte 8
 .byte 38,64,13,0
 .byte 40,64,13,8
KbBody1c:
 .byte 12
 .byte 32,0,31,2
 .byte 42,0,15,8
 .byte 44,0,15,0
KbBody1d:
 .byte 12
 .byte 32,64,31,6
 .byte 42,64,15,0
 .byte 44,64,15,8
KbBody1e:
 .byte 8
 .byte 46,0,15,0
 .byte 48,0,15,8
KbBody1f:
 .byte 8
 .byte 46,64,15,8
 .byte 48,64,15,0
KbBody20:
 .byte 8
 .byte 46,0,15,0
 .byte 48,0,15,8
KbBody21:
 .byte 8
 .byte 46,64,15,8
 .byte 48,64,15,0
KbBody22:
 .byte 8
 .byte 50,0,15,0
 .byte 52,0,15,8
KbBody23:
 .byte 8
 .byte 50,64,15,8
 .byte 52,64,15,0
KbBody24:
 .byte 8
 .byte 54,0,15,0
 .byte 56,0,15,8
KbBody25:
 .byte 8
 .byte 54,64,15,8
 .byte 56,64,15,0
KbBody26:
 .byte 8
 .byte 16,192,15,8
 .byte 58,192,15,0
KbBody27:
 .byte 8
 .byte 16,128,15,0
 .byte 58,128,15,8
KbBody28:
 .byte 8
 .byte 46,0,15,0
 .byte 48,0,15,8
KbBody29:
 .byte 8
 .byte 46,64,15,8
 .byte 48,64,15,0
KbBody2a:
 .byte 8
 .byte 60,0,15,0
 .byte 62,0,15,8
KbBody2b:
 .byte 8
 .byte 60,64,15,8
 .byte 62,64,15,0
KbBody2c:
 .byte 8
 .byte 54,0,15,0
 .byte 56,0,15,8
KbBody2d:
 .byte 8
 .byte 54,64,15,8
 .byte 56,64,15,0
KbBody2e:
 .byte 8
 .byte 48,0,15,0
 .byte 50,0,15,8
KbBody2f:
 .byte 8
 .byte 48,64,15,8
 .byte 50,64,15,0
KbBody30:
 .byte 8
 .byte 28,0,17,8
 .byte 30,0,17,0
KbBody31:
 .byte 8
 .byte 32,0,17,8
 .byte 34,0,17,0
KbBody32:
 .byte 8
 .byte 32,64,17,0
 .byte 34,64,17,8
KbBody33:
 .byte 8
 .byte 28,64,17,0
 .byte 30,64,17,8
KbBody34:
 .byte 8
 .byte 36,0,18,8
 .byte 38,0,18,0
KbBody35:
 .byte 8
 .byte 36,0,18,8
 .byte 38,0,18,0
KbBody36:
 .byte 8
 .byte 36,64,18,0
 .byte 38,64,18,8
KbBody37:
 .byte 8
 .byte 36,64,18,0
 .byte 38,64,18,8
KbBody38:
 .byte 12
 .byte 40,0,15,-2
 .byte 42,0,15,6
 .byte 44,0,15,14
KbBody39:
 .byte 12
 .byte 40,64,15,10
 .byte 42,64,15,2
 .byte 44,64,15,-6
KbBody3a:
 .byte 8
 .byte 46,0,16,8
 .byte 48,0,16,0
KbBody3b:
 .byte 8
 .byte 46,64,16,0
 .byte 48,64,16,8
KbBody3c:
 .byte 8
 .byte 50,0,15,8
 .byte 52,0,15,0
KbBody3d:
 .byte 8
 .byte 50,64,15,0
 .byte 52,64,15,8
KbBody3e:
 .byte 8
 .byte 54,0,17,8
 .byte 56,0,17,0
KbBody3f:
 .byte 8
 .byte 54,64,17,0
 .byte 56,64,17,8
KbBody40:
 .byte 8
 .byte 58,0,16,8
 .byte 60,0,16,0
KbBody41:
 .byte 8
 .byte 58,64,16,0
 .byte 60,64,16,8
KbBody42:
 .byte 8
 .byte 28,0,15,8
 .byte 30,0,15,0
KbBody43:
 .byte 8
 .byte 28,0,15,8
 .byte 30,0,15,0
KbBody44:
 .byte 12
 .byte 32,0,15,-4
 .byte 32,64,15,11
 .byte 34,0,15,4
KbBody45:
 .byte 12
 .byte 32,0,15,-4
 .byte 32,64,15,11
 .byte 34,0,15,4
KbBody46:
 .byte 8
 .byte 36,0,15,8
 .byte 38,0,15,0
KbBody47:
 .byte 8
 .byte 36,0,15,8
 .byte 38,0,15,0
KbBody48:
 .byte 8
 .byte 54,0,15,0
 .byte 56,0,15,8
KbBody49:
 .byte 8
 .byte 54,64,15,8
 .byte 56,64,15,0
KbBody4a:
 .byte 8
 .byte 40,0,15,0
 .byte 42,0,15,8
KbBody4b:
 .byte 8
 .byte 40,64,15,8
 .byte 42,64,15,0
KbBody4c:
 .byte 8
 .byte 40,0,15,0
 .byte 44,0,15,8
KbBody4d:
 .byte 8
 .byte 40,64,15,8
 .byte 44,64,15,0
KbBody4e:
 .byte 16
 .byte 46,0,23,8
 .byte 48,0,23,0
 .byte 50,0,7,0
 .byte 52,0,7,8
KbBody4f:
 .byte 16
 .byte 46,64,23,0
 .byte 48,64,23,8
 .byte 50,64,7,8
 .byte 52,64,7,0
KbBody50:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 32,0,23,-4
 .byte 34,0,7,12
 .byte 36,0,7,4
 .byte 38,0,7,-4
KbBody51:
 .byte 24
 .byte 28,0,23,4
 .byte 32,64,23,12
 .byte 30,64,23,-4
 .byte 38,64,7,12
 .byte 36,64,7,4
 .byte 34,64,7,-4
KbBody52:
 .byte 24
 .byte 28,0,22,4
 .byte 30,0,22,12
 .byte 32,0,22,-4
 .byte 40,0,6,12
 .byte 42,0,6,4
 .byte 44,0,6,-4
KbBody53:
 .byte 24
 .byte 28,0,22,4
 .byte 32,64,22,12
 .byte 30,64,22,-4
 .byte 44,64,6,12
 .byte 42,64,6,4
 .byte 40,64,6,-4
KbBody54:
 .byte 24
 .byte 28,0,24,4
 .byte 30,0,24,12
 .byte 32,0,24,-4
 .byte 46,0,8,12
 .byte 42,0,8,4
 .byte 48,0,8,-4
KbBody55:
 .byte 24
 .byte 28,0,24,4
 .byte 32,64,24,12
 .byte 30,64,24,-4
 .byte 48,64,8,12
 .byte 42,64,8,4
 .byte 46,64,8,-4
KbBody56:
 .byte 8
 .byte 44,0,15,8
 .byte 40,0,15,0
KbBody57:
 .byte 8
 .byte 40,64,15,8
 .byte 44,64,15,0
KbBody58:
 .byte 8
 .byte 50,0,15,8
 .byte 52,0,15,0
KbBody59:
 .byte 8
 .byte 52,64,15,8
 .byte 50,64,15,0
KbBody5a:
 .byte 16
 .byte 54,0,14,21
 .byte 56,0,14,16
 .byte 52,0,15,0
 .byte 50,0,15,8
KbBody5b:
 .byte 16
 .byte 54,64,14,-13
 .byte 56,64,14,-8
 .byte 52,64,15,8
 .byte 50,64,15,0
KbBody5c:
 .byte 16
 .byte 58,0,14,26
 .byte 60,0,14,18
 .byte 50,0,15,8
 .byte 52,0,15,0
KbBody5d:
 .byte 16
 .byte 58,64,14,-18
 .byte 60,64,14,-10
 .byte 50,64,15,0
 .byte 52,64,15,8
KbBody5e:
 .byte 16
 .byte 54,0,14,26
 .byte 56,0,14,18
 .byte 52,0,15,0
 .byte 50,0,15,8
KbBody5f:
 .byte 16
 .byte 54,64,14,-18
 .byte 56,64,14,-10
 .byte 52,64,15,8
 .byte 50,64,15,0
KbBody60:
 .byte 12
 .byte 62,0,13,26
 .byte 50,0,15,8
 .byte 52,0,15,0
KbBody61:
 .byte 12
 .byte 62,64,13,-18
 .byte 50,64,15,0
 .byte 52,64,15,8
KbBody62:
 .byte 8
 .byte 54,0,15,3
 .byte 56,0,15,11
KbBody63:
 .byte 8
 .byte 54,64,15,5
 .byte 56,64,15,-3
KbBody64:
 .byte 16
 .byte 58,0,14,24
 .byte 60,0,14,19
 .byte 54,0,15,3
 .byte 56,0,15,11
KbBody65:
 .byte 16
 .byte 58,64,14,-16
 .byte 60,64,14,-11
 .byte 54,64,15,5
 .byte 56,64,15,-3
KbBody66:
 .byte 16
 .byte 28,0,14,29
 .byte 30,0,14,21
 .byte 32,0,15,11
 .byte 34,0,15,3
KbBody67:
 .byte 16
 .byte 28,64,14,-21
 .byte 30,64,14,-13
 .byte 32,64,15,-3
 .byte 34,64,15,5
KbBody68:
 .byte 16
 .byte 58,0,14,29
 .byte 60,0,14,21
 .byte 54,0,15,3
 .byte 56,0,15,11
KbBody69:
 .byte 16
 .byte 58,64,14,-21
 .byte 60,64,14,-13
 .byte 54,64,15,5
 .byte 56,64,15,-3
KbBody6a:
 .byte 12
 .byte 36,0,13,29
 .byte 32,0,15,11
 .byte 34,0,15,3
KbBody6b:
 .byte 12
 .byte 36,64,13,-21
 .byte 32,64,15,-3
 .byte 34,64,15,5
KbBody6c:
 .byte 8
 .byte 38,64,15,8
 .byte 40,0,15,0
KbBody6d:
 .byte 8
 .byte 38,0,15,0
 .byte 40,64,15,8
KbBody6e:
 .byte 8
 .byte 42,64,15,8
 .byte 42,0,15,0
KbBody6f:
 .byte 12
 .byte 44,64,15,12
 .byte 44,0,15,-4
 .byte 46,64,15,4
KbBody70:
 .byte 8
 .byte 48,64,15,8
 .byte 48,0,15,0
KbBody71:
 .byte 16
 .byte 50,64,3,8
 .byte 50,0,3,0
 .byte 48,64,15,8
 .byte 48,0,15,0
KbBody72:
 .byte 16
 .byte 52,64,-1,8
 .byte 52,0,-1,0
 .byte 48,64,15,8
 .byte 48,0,15,0
KbBody73:
 .byte 16
 .byte 50,64,-1,8
 .byte 50,0,-1,0
 .byte 48,64,15,8
 .byte 48,0,15,0
KbBody74:
 .byte 16
 .byte 54,64,-5,8
 .byte 54,0,-5,0
 .byte 48,64,15,8
 .byte 48,0,15,0
KbBody75:
 .byte 8
 .byte 56,64,15,8
 .byte 56,0,15,0
KbBody76:
 .byte 16
 .byte 50,192,27,8
 .byte 50,128,27,0
 .byte 56,64,15,8
 .byte 56,0,15,0
KbBody77:
 .byte 16
 .byte 52,192,31,8
 .byte 52,128,31,0
 .byte 56,64,15,8
 .byte 56,0,15,0
KbBody78:
 .byte 16
 .byte 50,192,31,8
 .byte 50,128,31,0
 .byte 56,64,15,8
 .byte 56,0,15,0
KbBody79:
 .byte 16
 .byte 54,192,35,8
 .byte 54,128,35,0
 .byte 56,64,15,8
 .byte 56,0,15,0
KbFullChr:
 .byte 90,90,90,90,96,96,96,96,96,96,96,96
 .byte 96,96,96,96,96,96,96,96,96,96,96,96
 .byte 96,96,96,96,96,96,96,96,98,98,98,98
 .byte 98,98,98,98,98,98,98,98,96,96,96,96
 .byte 98,98,98,98,98,98,98,98,96,96,90,90
 .byte 90,90,98,98,98,98,98,98,98,98
KbFullLo:
 .byte <KbFull00,<KbFull01,<KbFull02,<KbFull03,<KbFull04,<KbFull05,<KbFull06,<KbFull07,<KbFull08,<KbFull09,<KbFull0a,<KbFull0b
 .byte <KbFull0c,<KbFull0d,<KbFull0e,<KbFull0f,<KbFull10,<KbFull11,<KbFull12,<KbFull13,<KbFull14,<KbFull15,<KbFull16,<KbFull17
 .byte <KbFull18,<KbFull19,<KbFull1a,<KbFull1b,<KbFull1c,<KbFull1d,<KbFull1e,<KbFull1f,<KbFull20,<KbFull21,<KbFull22,<KbFull23
 .byte <KbFull24,<KbFull25,<KbFull26,<KbFull27,<KbFull28,<KbFull29,<KbFull2a,<KbFull2b,<KbFull2c,<KbFull2d,<KbFull2e,<KbFull2f
 .byte <KbFull30,<KbFull31,<KbFull32,<KbFull33,<KbFull34,<KbFull35,<KbFull36,<KbFull37,<KbFull38,<KbFull39,<KbFull3a,<KbFull3b
 .byte <KbFull3c,<KbFull3d,<KbFull3e,<KbFull3f,<KbFull40,<KbFull41,<KbFull42,<KbFull43,<KbFull44,<KbFull45
KbFullHi:
 .byte >KbFull00,>KbFull01,>KbFull02,>KbFull03,>KbFull04,>KbFull05,>KbFull06,>KbFull07,>KbFull08,>KbFull09,>KbFull0a,>KbFull0b
 .byte >KbFull0c,>KbFull0d,>KbFull0e,>KbFull0f,>KbFull10,>KbFull11,>KbFull12,>KbFull13,>KbFull14,>KbFull15,>KbFull16,>KbFull17
 .byte >KbFull18,>KbFull19,>KbFull1a,>KbFull1b,>KbFull1c,>KbFull1d,>KbFull1e,>KbFull1f,>KbFull20,>KbFull21,>KbFull22,>KbFull23
 .byte >KbFull24,>KbFull25,>KbFull26,>KbFull27,>KbFull28,>KbFull29,>KbFull2a,>KbFull2b,>KbFull2c,>KbFull2d,>KbFull2e,>KbFull2f
 .byte >KbFull30,>KbFull31,>KbFull32,>KbFull33,>KbFull34,>KbFull35,>KbFull36,>KbFull37,>KbFull38,>KbFull39,>KbFull3a,>KbFull3b
 .byte >KbFull3c,>KbFull3d,>KbFull3e,>KbFull3f,>KbFull40,>KbFull41,>KbFull42,>KbFull43,>KbFull44,>KbFull45
KbFull00:
 .byte 8
 .byte 40,0,15,0
 .byte 44,0,15,8
KbFull01:
 .byte 8
 .byte 40,64,15,8
 .byte 44,64,15,0
KbFull02:
 .byte 16
 .byte 46,0,23,8
 .byte 48,0,23,0
 .byte 50,0,7,0
 .byte 52,0,7,8
KbFull03:
 .byte 16
 .byte 46,64,23,0
 .byte 48,64,23,8
 .byte 50,64,7,8
 .byte 52,64,7,0
KbFull04:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 32,0,7,12
 .byte 34,0,7,4
 .byte 36,0,7,-4
KbFull05:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 36,64,7,12
 .byte 34,64,7,4
 .byte 32,64,7,-4
KbFull06:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 38,0,7,12
 .byte 40,0,7,4
 .byte 42,0,7,-4
KbFull07:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 42,64,7,12
 .byte 40,64,7,4
 .byte 38,64,7,-4
KbFull08:
 .byte 24
 .byte 28,0,23,1
 .byte 30,0,23,9
 .byte 30,64,23,-7
 .byte 38,0,7,9
 .byte 40,0,7,1
 .byte 42,0,7,-7
KbFull09:
 .byte 24
 .byte 28,0,23,1
 .byte 30,0,23,9
 .byte 30,64,23,-7
 .byte 42,64,7,9
 .byte 40,64,7,1
 .byte 38,64,7,-7
KbFull0a:
 .byte 24
 .byte 28,0,23,7
 .byte 30,0,23,15
 .byte 30,64,23,-1
 .byte 38,0,7,15
 .byte 40,0,7,7
 .byte 42,0,7,-1
KbFull0b:
 .byte 24
 .byte 28,0,23,7
 .byte 30,0,23,15
 .byte 30,64,23,-1
 .byte 42,64,7,15
 .byte 40,64,7,7
 .byte 38,64,7,-1
KbFull0c:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 32,0,7,12
 .byte 34,0,7,4
 .byte 36,0,7,-4
KbFull0d:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 36,64,7,12
 .byte 34,64,7,4
 .byte 32,64,7,-4
KbFull0e:
 .byte 24
 .byte 28,0,25,4
 .byte 30,0,25,12
 .byte 30,64,25,-4
 .byte 32,0,9,12
 .byte 34,0,9,4
 .byte 36,0,9,-4
KbFull0f:
 .byte 24
 .byte 28,64,25,4
 .byte 30,64,25,-4
 .byte 30,0,25,12
 .byte 32,64,9,-4
 .byte 34,64,9,4
 .byte 36,64,9,12
KbFull10:
 .byte 24
 .byte 28,0,27,4
 .byte 30,0,27,12
 .byte 30,64,27,-4
 .byte 32,0,11,12
 .byte 34,0,11,4
 .byte 36,0,11,-4
KbFull11:
 .byte 24
 .byte 28,64,27,4
 .byte 30,64,27,-4
 .byte 30,0,27,12
 .byte 32,64,11,-4
 .byte 34,64,11,4
 .byte 36,64,11,12
KbFull12:
 .byte 8
 .byte 44,0,15,8
 .byte 46,0,15,0
KbFull13:
 .byte 8
 .byte 44,64,15,0
 .byte 46,64,15,8
KbFull14:
 .byte 8
 .byte 44,0,15,8
 .byte 46,0,15,0
KbFull15:
 .byte 8
 .byte 44,64,15,0
 .byte 46,64,15,8
KbFull16:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 48,0,7,12
 .byte 40,0,7,4
 .byte 50,0,7,-4
KbFull17:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 50,64,7,12
 .byte 40,64,7,4
 .byte 48,64,7,-4
KbFull18:
 .byte 24
 .byte 52,0,23,4
 .byte 54,0,23,12
 .byte 56,0,23,-4
 .byte 38,0,7,12
 .byte 40,0,7,4
 .byte 42,0,7,-4
KbFull19:
 .byte 24
 .byte 52,0,23,4
 .byte 54,0,23,12
 .byte 56,0,23,-4
 .byte 42,64,7,12
 .byte 40,64,7,4
 .byte 38,64,7,-4
KbFull1a:
 .byte 24
 .byte 52,64,23,4
 .byte 56,64,23,12
 .byte 54,64,23,-4
 .byte 38,0,7,12
 .byte 40,0,7,4
 .byte 42,0,7,-4
KbFull1b:
 .byte 24
 .byte 52,64,23,4
 .byte 56,64,23,12
 .byte 54,64,23,-4
 .byte 42,64,7,12
 .byte 40,64,7,4
 .byte 38,64,7,-4
KbFull1c:
 .byte 24
 .byte 58,0,23,4
 .byte 54,0,23,12
 .byte 60,0,23,-4
 .byte 38,0,7,12
 .byte 40,0,7,4
 .byte 42,0,7,-4
KbFull1d:
 .byte 24
 .byte 58,0,23,4
 .byte 54,0,23,12
 .byte 60,0,23,-4
 .byte 42,64,7,12
 .byte 40,64,7,4
 .byte 38,64,7,-4
KbFull1e:
 .byte 24
 .byte 58,64,23,4
 .byte 60,64,23,12
 .byte 54,64,23,-4
 .byte 38,0,7,12
 .byte 40,0,7,4
 .byte 42,0,7,-4
KbFull1f:
 .byte 24
 .byte 58,64,23,4
 .byte 60,64,23,12
 .byte 54,64,23,-4
 .byte 42,64,7,12
 .byte 40,64,7,4
 .byte 38,64,7,-4
KbFull20:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 32,64,23,-4
 .byte 34,0,7,12
 .byte 36,0,7,4
 .byte 38,0,7,-4
KbFull21:
 .byte 24
 .byte 28,0,23,4
 .byte 32,0,23,12
 .byte 30,64,23,-4
 .byte 38,64,7,12
 .byte 36,64,7,4
 .byte 34,64,7,-4
KbFull22:
 .byte 24
 .byte 40,0,25,4
 .byte 42,0,25,12
 .byte 42,64,25,-4
 .byte 44,0,9,12
 .byte 46,0,9,4
 .byte 48,0,9,-4
KbFull23:
 .byte 24
 .byte 40,0,25,4
 .byte 42,0,25,12
 .byte 42,64,25,-4
 .byte 48,64,9,12
 .byte 46,64,9,4
 .byte 44,64,9,-4
KbFull24:
 .byte 24
 .byte 28,0,23,4
 .byte 50,0,23,12
 .byte 30,64,23,-4
 .byte 52,0,7,12
 .byte 54,0,7,4
 .byte 56,0,7,-4
KbFull25:
 .byte 24
 .byte 28,64,23,4
 .byte 30,0,23,12
 .byte 50,64,23,-4
 .byte 56,64,7,12
 .byte 54,64,7,4
 .byte 52,64,7,-4
KbFull26:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 32,64,23,-4
 .byte 34,0,7,12
 .byte 36,0,7,4
 .byte 38,0,7,-4
KbFull27:
 .byte 24
 .byte 28,0,23,4
 .byte 32,0,23,12
 .byte 30,64,23,-4
 .byte 38,64,7,12
 .byte 36,64,7,4
 .byte 34,64,7,-4
KbFull28:
 .byte 24
 .byte 40,0,25,4
 .byte 42,0,25,12
 .byte 42,64,25,-4
 .byte 44,0,9,12
 .byte 46,0,9,4
 .byte 48,0,9,-4
KbFull29:
 .byte 24
 .byte 40,0,25,4
 .byte 42,0,25,12
 .byte 42,64,25,-4
 .byte 48,64,9,12
 .byte 46,64,9,4
 .byte 44,64,9,-4
KbFull2a:
 .byte 24
 .byte 28,0,23,4
 .byte 50,0,23,12
 .byte 30,64,23,-4
 .byte 52,0,7,12
 .byte 54,0,7,4
 .byte 56,0,7,-4
KbFull2b:
 .byte 24
 .byte 28,64,23,4
 .byte 30,0,23,12
 .byte 50,64,23,-4
 .byte 56,64,7,12
 .byte 54,64,7,4
 .byte 52,64,7,-4
KbFull2c:
 .byte 24
 .byte 58,64,23,4
 .byte 60,64,23,12
 .byte 54,64,23,-4
 .byte 38,0,7,12
 .byte 40,0,7,4
 .byte 42,0,7,-4
KbFull2d:
 .byte 24
 .byte 58,0,23,4
 .byte 54,0,23,12
 .byte 60,0,23,-4
 .byte 42,64,7,12
 .byte 40,64,7,4
 .byte 38,64,7,-4
KbFull2e:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 48,0,7,12
 .byte 40,0,7,4
 .byte 50,0,7,-4
KbFull2f:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 50,64,7,12
 .byte 40,64,7,4
 .byte 48,64,7,-4
KbFull30:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 32,64,23,-4
 .byte 34,0,7,12
 .byte 36,0,7,4
 .byte 38,0,7,-4
KbFull31:
 .byte 24
 .byte 28,0,23,4
 .byte 32,0,23,12
 .byte 30,64,23,-4
 .byte 38,64,7,12
 .byte 36,64,7,4
 .byte 34,64,7,-4
KbFull32:
 .byte 24
 .byte 40,0,25,4
 .byte 42,0,25,12
 .byte 42,64,25,-4
 .byte 44,0,9,12
 .byte 46,0,9,4
 .byte 48,0,9,-4
KbFull33:
 .byte 24
 .byte 40,0,25,4
 .byte 42,0,25,12
 .byte 42,64,25,-4
 .byte 48,64,9,12
 .byte 46,64,9,4
 .byte 44,64,9,-4
KbFull34:
 .byte 24
 .byte 28,0,23,4
 .byte 50,0,23,12
 .byte 30,64,23,-4
 .byte 52,0,7,12
 .byte 54,0,7,4
 .byte 56,0,7,-4
KbFull35:
 .byte 24
 .byte 28,64,23,4
 .byte 30,0,23,12
 .byte 50,64,23,-4
 .byte 56,64,7,12
 .byte 54,64,7,4
 .byte 52,64,7,-4
KbFull36:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 32,64,23,-4
 .byte 34,0,7,12
 .byte 36,0,7,4
 .byte 38,0,7,-4
KbFull37:
 .byte 24
 .byte 28,0,23,4
 .byte 32,0,23,12
 .byte 30,64,23,-4
 .byte 38,64,7,12
 .byte 36,64,7,4
 .byte 34,64,7,-4
KbFull38:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 62,0,7,12
 .byte 34,0,7,4
 .byte 36,0,7,-4
KbFull39:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 30,64,23,-4
 .byte 36,64,7,12
 .byte 34,64,7,4
 .byte 62,64,7,-4
KbFull3a:
 .byte 16
 .byte 46,0,23,8
 .byte 48,0,23,0
 .byte 50,0,7,0
 .byte 52,0,7,8
KbFull3b:
 .byte 16
 .byte 46,64,23,0
 .byte 48,64,23,8
 .byte 50,64,7,8
 .byte 52,64,7,0
KbFull3c:
 .byte 8
 .byte 40,0,15,0
 .byte 44,0,15,8
KbFull3d:
 .byte 8
 .byte 40,64,15,8
 .byte 44,64,15,0
KbFull3e:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 32,64,23,-4
 .byte 34,0,7,12
 .byte 36,0,7,4
 .byte 38,0,7,-4
KbFull3f:
 .byte 24
 .byte 28,0,23,4
 .byte 32,0,23,12
 .byte 30,64,23,-4
 .byte 38,64,7,12
 .byte 36,64,7,4
 .byte 34,64,7,-4
KbFull40:
 .byte 24
 .byte 40,0,25,4
 .byte 42,0,25,12
 .byte 42,64,25,-4
 .byte 44,0,9,12
 .byte 46,0,9,4
 .byte 48,0,9,-4
KbFull41:
 .byte 24
 .byte 40,0,25,4
 .byte 42,0,25,12
 .byte 42,64,25,-4
 .byte 48,64,9,12
 .byte 46,64,9,4
 .byte 44,64,9,-4
KbFull42:
 .byte 24
 .byte 28,0,23,4
 .byte 50,0,23,12
 .byte 30,64,23,-4
 .byte 52,0,7,12
 .byte 54,0,7,4
 .byte 56,0,7,-4
KbFull43:
 .byte 24
 .byte 28,64,23,4
 .byte 30,0,23,12
 .byte 50,64,23,-4
 .byte 56,64,7,12
 .byte 54,64,7,4
 .byte 52,64,7,-4
KbFull44:
 .byte 24
 .byte 28,0,23,4
 .byte 30,0,23,12
 .byte 32,64,23,-4
 .byte 34,0,7,12
 .byte 36,0,7,4
 .byte 38,0,7,-4
KbFull45:
 .byte 24
 .byte 28,0,23,4
 .byte 32,0,23,12
 .byte 30,64,23,-4
 .byte 38,64,7,12
 .byte 36,64,7,4
 .byte 34,64,7,-4
KbEffectLo:
 .byte <KbEffect0,<KbEffect1,<KbEffect2,<KbEffect3,<KbEffect4,<KbEffect5,<KbEffect6,<KbEffect7,<KbEffect8,<KbEffect9
KbEffectHi:
 .byte >KbEffect0,>KbEffect1,>KbEffect2,>KbEffect3,>KbEffect4,>KbEffect5,>KbEffect6,>KbEffect7,>KbEffect8,>KbEffect9
KbHealthTiles:
 .byte 22,24,26
KbEffect0:
 .byte 12
 .byte 0,130,-9,-12
 .byte 0,194,-9,-4
 .byte 2,66,-7,4
KbEffect1:
 .byte 12
 .byte 4,194,-12,-2
 .byte 6,194,-12,-10
 .byte 2,66,-1,3
KbEffect2:
 .byte 12
 .byte 0,2,-15,-8
 .byte 0,66,-15,0
 .byte 2,194,-7,-3
KbEffect3:
 .byte 12
 .byte 4,2,-12,-3
 .byte 6,2,-12,5
 .byte 2,130,-9,-8
KbEffect4:
 .byte 12
 .byte 0,2,-7,-8
 .byte 0,66,-7,0
 .byte 2,66,-14,-3
KbEffect5:
 .byte 12
 .byte 6,2,-7,-2
 .byte 4,2,-7,-10
 .byte 2,66,-11,3
KbEffect6:
 .byte 8
 .byte 8,130,-9,-8
 .byte 10,130,-9,0
KbEffect7:
 .byte 8
 .byte 12,2,-9,0
 .byte 14,2,-9,-8
KbEffect8:
 .byte 8
 .byte 16,66,-9,0
 .byte 16,2,-9,-8
KbEffect9:
 .byte 8
 .byte 18,2,-9,0
 .byte 20,2,-9,-8
.popseg
