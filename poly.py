import polyline
import geojson


coords = polyline.decode(
    "ujmdIpgff@RBvAe@_@aFQiA[}AKq@QgBcAiFvEeCd@VHNHVHfBP`CF`AGBFCGaAQaCIgBMwAbAc@fBu@rAg@hAa@Dw@?yAc@iFK{A@kAHaC?{AIqAg@}DSoAq@sCoByHC?EACCGQ@S@IU_Bg@{B[}Ac@aDm@}E]}Bk@cDUwAW_CYuBCQAOw@GgAI_@DIDKF?DAJAHIPIHI@KCKEGKCM?SuBuBwB}BAFEHCDGDI?QCKQCk@Dc@DKPsAAWGg@YeAa@kAsAqDkCqHiBcFeAkDwAgGo@mDWuA[oBp@e@TMXOj@WbAW`B?v@JfBPfDd@rCXhB@LYJa@AoB@{@R}ANg@PYRSLGbBo@nAa@LAPDj@ZLDL?NEJMVa@Gu@O}BHkA\\eDjA}IFa@RiAVoBDk@f@_E\\}DfAwMf@uI\\_FNaBBwAAs@I}@EAECIOAU@UFOJGL@HJBBZg@Te@`@eATkARwAPoAPgBLqA`@gDNqAEAECKOCWBWHSLEF@@?Ba@Bw@BiCB}CJy@Pq@Fs@@q@C]Qo@c@s@Y]w@eAO[Mg@_@qAUwAYoB[uFGiGGq@OkA_CoJ{@cDYmAiAsEaI_[eC{JuA}EcByG_C_JaCoJ{AkG_AoEWaAi@mCg@cCiAaGi@yDc@}Cg@mD}@{F{@oFyA}Ji@yC]yAc@yAmAsDw@cC{@aCw@_B_AuAkCcDiBaBs@e@}@g@cB{@uAy@w@e@qAaASOS_@e@a@[]o@q@{AyBkBoCsBcDiBsCaAcBuB_EgAoBgCyEc@u@QUQUu@m@L_AFu@J_BAq@i@wCWyAmA}I]kEn@YLKLQRc@NcAHkAF}CJiIV}XZgIp@kNh@kLTeFP_DP_@NMtCq@jAU`@I^GPOh@MLAXA?E@CBIHGH?Ng@P[Nm@DWz@_Gb@}ClBeMPy@fAkBxCwEz@yALWNMVc@\\_AL[lBiFPu@F{AAaGFm@VeBrBoNl@{ENsAh@kFHmA?w@}@mFi@gDUmBUaB{@aHUeBC_@Cu@H_HDqGWwCKyEWwMOcMEoFsAV{ATk@Pa@HM?g@LwBEiCGc@Es@L}Cp@sB`@eAVs@LoBj@]?}B[wAS}AS}Ce@wB]kCsCi@Sm@QmAMgCBa@D_A??g@GwDA{AQ@?BC_APm@Ac@NCCoCCgA@]GcDIsAM[DCGa@MHCACVHBAYPM", 5)

# coords are opposite order of what you'd expect so we need to reverse them
coords = [(x[1], x[0]) for x in coords]

# create a geojson LineString
line = geojson.LineString(coords)
# create a geojson Feature
feature = geojson.Feature(geometry=line)
# dump the geojson Feature to a string
print(geojson.dumps(feature))
