# R version of JavaScript (from Java & C++) calculations of adjustment reagents
# Modified VII-2017 for iQuaCalc in Shiny module version


calcAdjustment <- function(initDic,  initAlk,
                           finalDic, finalAlk,
                           vol,
                           reagent1, reagent2) {

  # cat('\n(', initDic, ', ', initAlk, ') \n')
  # cat('(', finalDic, ', ', finalAlk, ') \n')

  # get vector of reagent data for each checked checkbox
  myP1 <- reagent_data %>% filter(name == reagent1)
  myP2 <- reagent_data %>% filter(name == reagent2)

  # myP1 <- reagent.df[reagent.df$name==reagent1,]
  # myP2 <- reagent.df[reagent.df$name==reagent2,]


  # initialize first as lower- & second as higherReagent
  lowerReagent <- myP1
  higherReagent <- myP2

  deltaDic <- finalDic - initDic;
  deltaAlk <- finalAlk - initAlk;

  wpSlope    <- deltaAlk / deltaDic # slope between waypoints
  wpSlopeRad <- atan(wpSlope)

  # ** 0. initialize chemAdjustment1 & chemAdjustment2...
  chemAdjustment1 <- 0
  chemAdjustment2 <- 0


  # ** 1. Are there exactly TWO cbs checked?

  # ** 1a Recover adjustment data for the two selected reagents

  # ** 2. ID the reagent with the lower slope (AND WHEN THE SLOPES ARE EQUAL?)
  # ** (Ans: When slopes are equal, disable all but first of those selected)
  #            var lowerReagent = ((myP1.m < myP2.m) ? myP1 : myP2);

  if(myP1$mRad < myP2$mRad) {
    lowerReagent  <- myP1
    higherReagent <- myP2
  } else {
    lowerReagent  <- myP2
    higherReagent <- myP1
  }


  # ** 2a Re-assign elements of cbChecked so that lowerReagent is first
  # cbChecked.length = 0;
  # cbChecked.push(lowerReagent.name);
  # cbChecked.push(higherReagent.name);


  # ** 3. Is wpTerminal within the adjustment region? (test slopes & Q-is)
  # ** 3a adjLowerSlope < wpSlope < adjUpperSlope ?

  quadrant <- 0

  if(deltaDic >= 0 && deltaAlk >= 0)
    quadrant <- 1
  else if (deltaDic < 0 && deltaAlk >= 0)
    quadrant <- 2
  else if (deltaDic < 0 && deltaAlk < 0)
    quadrant <- 3
  else if (deltaDic >= 0 && deltaAlk < 0)
    quadrant <- 4

  if(2 == quadrant)
    wpSlopeRad <- wpSlopeRad + pi # ** 2nd-Quadrant correction
  else if(3 == quadrant)
    wpSlopeRad <- wpSlopeRad + pi
  else if(4 == quadrant)
    wpSlopeRad <- wpSlopeRad + 2 * pi


  bContinueCalc <- TRUE


  if(higherReagent$mRad - lowerReagent$mRad < pi) {

    if(wpSlopeRad <= higherReagent$mRad &&
         wpSlopeRad >= lowerReagent$mRad)
      bContinueCalc <- TRUE
    else {
      bContinueCalc <- FALSE
    }
  } else {
#    if(wpSlopeRad >= higherReagent$mRad)
    if((wpSlopeRad >= higherReagent$mRad) || (wpSlopeRad <= lowerReagent$mRad))
      bContinueCalc <- TRUE
    else {
      bContinueCalc <- FALSE
    }
  }

  # ** 3b First, just deal with "Q-I" reagents; extend it later

  if(bContinueCalc) {

    if(myP1$m < myP2$m) {
      lowerReagent  <- myP1
      higherReagent <- myP2
    } else {
      lowerReagent  <- myP2
      higherReagent <- myP1
    }


    # ** 4b Calc DIC coordinate of "adjustment intersection"
    dicStar <- 0
    alkStar <- 0

    # ** if the higher reagent is NaOH, CaO, or Ca(OH)2, slope > 2 (undefined, in fact)
    if(higherReagent$m > 2) {
#    if(higherReagent$m > 2 || higherReagent$m == 0) {
      dicStar <- finalDic
      alkStar <- lowerReagent$m * (finalDic - initDic) + initAlk
    } else {
      dicStar <-  initAlk - lowerReagent$m * initDic
      dicStar <- dicStar + (-finalAlk) + higherReagent$m * finalDic
      dicStar <- dicStar / (higherReagent$m - lowerReagent$m)

      # ** 4. Calc [Alk] coordinate of "adjustment intersection"
      alkStar <-  lowerReagent$m * (dicStar - initDic)
      alkStar <-  alkStar + initAlk
    }

    # ** 5. Calc amt of REAGENT 1 (with lower slope) to reach this DIC
    # cat('dicStar - initDic = ', dicStar - initDic, '\n')
    # # print(lowerReagent)
    # cat('  lowerReagent$mw = ', lowerReagent$mw, '\n')
    # cat('              vol = ', vol, '\n')
    # cat('(dicStar - initDic) * lowerReagent$mw * vol = ', (dicStar - initDic) * lowerReagent$mw * vol, '\n\n')

    # NB: UNITS .... [mol/kg - mol/kg] * [g/mol] * [L} (or [kg for DIC deficit??]) --> g
    chemAdjustment1 <- abs((dicStar - initDic) * lowerReagent$mw * vol)
    #            }

    # ** 6. Use value in 4. to calc "[Alk] deficit"
    alkDeficit <- abs(finalAlk - alkStar)

    # *****************************************************************************
    # ** 7. Use REAGENT 2 to calc amount needed to raise/lower [Alk] to wpTerminal

    chemAdjustment2 <- alkDeficit * (higherReagent$mw / higherReagent$meq_mmol) * vol

    # *****************************************************************************

  } else {
    chemAdjustment1 <- chemAdjustment2 <- 0.0
  }

  # if HCl and/or CO2, then convert mass to volume
  # You are asked for a volume. You obviously need composition per volume.

# What volume of concentrated hydrochloric acid of specific gravity 1.19
# containing 37.23 percent HCL by weight contains 100g of HCL?

# Specific gravity = (density of a substance) :: (density of water)
# 1 L of pure water at 4 C has a weight of 1000 g
# Therefore, 1 L of the HCl at 4 C has a mass of 1190 g (= 1.19 x 1000).
# 37.23 % of 1190 g = 443.0 g of HCl
# (100 g / 443.0 g) x 1000 mL = 225.7 mL
# ANSWER: 226 mL
#
# Instead of trying to find a FORMULA to use, think of what you are given
# (percent by weight) and what you need (grams per volume).
# Your task is to convert mass per weight to mass per volume
#
# why 4 deg C...because that is the temperature when water has a density of 1.00000 g / mL.
# But the HCl was, e.g., at 20 deg C (68 deg F).
# The density of water at 20 deg c = 0.998203 g/mL,
# so the weight of the HCl solution at 20 deg C would be
# 0.998203 g/mL x 1000 mL/L x 1.19 = 1187.9 g and 37.23% of 1187.9 g = 442.2 g.
# The answer would be 226.1 mL (226 mL).
# Note that your answer should have 3 sig. fig. (sp. g. = 1.19; grams of HCl = 100)

muriaticPoSto<-0.3145
muriaticSpGr<-1.16                              # 1.16 kg HCl soln/L at 4C
muriaticMassPerL<-muriaticPoSto*muriaticSpGr    # kg HCL/L at 4C

# cat('BEFORE:',lowerReagent$name,': ',chemAdjustment1,'\n')
# cat('BEFORE:',higherReagent$name,': ',chemAdjustment2,'\n\n')

if(lowerReagent$name=='hcl') chemAdjustment1<-chemAdjustment1/muriaticMassPerL
if(higherReagent$name=='hcl') chemAdjustment2<-chemAdjustment2/muriaticMassPerL

# cat('AFTER:',lowerReagent$name,': ',chemAdjustment1,'\n')
# cat('AFTER:',higherReagent$name,': ',chemAdjustment2,'\n\n')


# NB: as calculated above, chemAdjustment* in grams
#     FOR iQuaCalc Shiny Web App, return KILOGRAMS
#     (This is a change from the earlier WQ Map 'test' Shiny App)

chemAdjustment1 <- chemAdjustment1 / 1000.0   # convert from grams to kg
chemAdjustment2 <- chemAdjustment2 / 1000.0   # convert from grams to kg

  adjResults<-c(chemAdjustment1, chemAdjustment2)

  adjNames<-c(as.character(lowerReagent$name), as.character(higherReagent$name))
  adjCmpds<-c(as.character(lowerReagent$cmpd), as.character(higherReagent$cmpd))

  # result.df<-data.frame(name=adjNames,
  result.df <- tibble(name = adjNames,
                          cmpd = adjCmpds,
                          amt  = adjResults)

                          # stringsAsFactors = F)   # NB: stringsAsFactors is FALSE

  return(result.df)
}

