# CarbCalc methods in R

# updated Pi Day, 14_III-2017


# cpragma mark - numerical methods

# ** For now, use f() as general QUARTIC (or cubic or quadratic)
# ** to be solved by calcPhForAlkDic()...
fOfx < - function(x, a, b, c, d, e)
{
return (a * x * x * x * x + b * x * x * x + c * x * x + d * x + e)
}

# ** code the secant method to solve 2nd-, 3rd-, & 4th-degree polynomials
calcSecantMethod < - function(q4, q3, q2, q1, q0)
{
# print('IN SECANT METHOD...')
ans = polyroot(c(q0, q1, q2, q3, q4))
# print(ans)
# ***************************************
# Method to carry out the secant search
# ***************************************

# ** define the number of iterations
n < - 500
del < - 10 ^ (-10)
a < - 0
b < - 40

# ** define the interval, dz, and ...
dx < - (b - a) / 10
x < - (a + b) / 2
# ***************************************

k < - 0

# ** increment the interval
x1 = x + dx

# ** while the increment is greater than the tolerance
# ** and the iterations are less than the max number thereof
# ** NB ** for iOS, MUST USE ---> fabs() <----, not abs() !!
while ((abs(dx) > del) & & (k < n)) {

d < - fOfx(x1, q4, q3, q2, q1, q0) - fOfx(x, q4, q3, q2, q1, q0)
x2 < - x1 - (fOfx(x1, q4, q3, q2, q1, q0) * (x1 - x)) / d

x < - x1
x1 < - x2

dx < - x1 - x

k < - k + 1
}

#  if(k == n) NSLog(@"Convergence not found after %d iterations",n)

return (x1)
}

# ---- density calcs ----

# ** NB: TEMP IS IN CELCIUS, ** NOT ** KELVIN

# NB: SMOW --Standard Mean Ocean Water
calcRhoFW < - function(t)
{
# **  input temp, dT, in KELVIN
# ** define a local temp in CELCIUS

tempInCelcius < - t - 273.15

rhoFw < - 999.842594 + 0.06793952 * tempInCelcius
rhoFw < - rhoFw + (-0.009095290) * tempInCelcius * tempInCelcius

rhoFw < - rhoFw + 0.0001001685 * tempInCelcius ^ 3
rhoFw < - rhoFw + (-0.000001120083) * tempInCelcius ^ 4
rhoFw < - rhoFw + 0.000000006536332 * tempInCelcius ^ 5

return (rhoFw)
}


# ** NB: TEMP IS IN CELCIUS, ** NOT ** KELVIN
# ***** SW rho(T, S)
# return: kg/m3 (g/l)
calcRho < - function(t, sal)
{
# ** input temp, dT, in KELVIN
# ** define a local temp in CELCIUS

tempInCelcius = t - 273.15

A < -      0.824493 - 0.0040899 * tempInCelcius
A < - A + 0.000076438 * tempInCelcius * tempInCelcius
A < - A + (-0.00000082467) * tempInCelcius ^ 3
A < - A + 0.0000000053875 * tempInCelcius ^ 4

B < -     -0.00572466 + 0.00010227 * tempInCelcius
B < - B + -0.0000016546 * tempInCelcius * tempInCelcius

C < - 0.00048314

# ** NB: SEND calcRhoFW temp in **KELVIN**, it will change to C
# **     Why? In case need to call calcRhoFW from another
# **     method that send temp in KELVIN
myRhoSW < -  calcRhoFW(t) + A * sal
myRhoSW < - myRhoSW + B * sal ^ 1.5
myRhoSW < - myRhoSW + C * sal * sal

return (myRhoSW)
}


# ---- pH 'slope' & 'intercept' calcs ----

phLineSlope < - function(temp, sal, ph)
{

return (alphaOne(temp, sal, ph) + 2 * alphaTwo(temp, sal, ph))
}

phLineIntercept < - function(temp, sal, ph)
{

return (calcHydroxide(ph, temp, sal) - calcHydronium(ph) + calcBorate(ph, temp, sal))
}


# [Alk] & DIC ----

calcAlkOfDic < - function(dic, ph, temp, sal)
{

alk < - dic * phLineSlope(temp, sal, ph)

alk < - alk + calcHydroxide(ph, temp, sal)

alk < - alk - calcHydronium(ph)

alk < - alk + calcBorate(ph, temp, sal)

#   print('----------')
#   print(alk)
#   print(phLineIntercept(temp,sal,ph) + dic*phLineSlope(temp,sal,ph))
#   print(1000*phLineIntercept(temp,sal,ph))
#   print(phLineSlope(temp,sal,ph))
#   print('----------')

return (alk)
}


# pragma mark - DIC from [Alk]

# calc DIC for a given [Alk] & pH
# (COULD USE WHEN pH is pHCrit for CO2Crit, no ???)
# ** What are the units of DIC? ... mmol/kg
# Do [Alk] units need converted from "/liter" to "/kg" ?
calcDicOfAlk < - function(alk, ph, temp, sal)
{

m < - phLineSlope(temp, sal, ph)

dic < - (alk - calcHydroxide(ph, temp, sal) -
         calcBorate(ph, temp, sal) +
         calcHydronium(ph)) / m;

return (dic)
}


# Borate ----

# ** FREE scale?
calcBorate < - function(ph, t, sal)
{

concB < - calcBorateConcOfSalinity(sal)

myKB < - calcBorateFactor(t, sal)

borate < - myKB * concB / (myKB + 10 ^ (-ph))

return (borate)
}


calcBorateConcOfSalinity < - function(sal)
{

concB < - 0.000232 * sal / (10.811 * 1.80655)

return (concB)
}

calcBorateFactor < - function(t, sal)
{

if (is.null(sal))
return ()

A < - 148.0248 + 137.1942 * sqrt(sal) + 1.62142 * sal
B < - -8966.90 - 2890.53 * sqrt(sal) - 77.942 * sal + 1.728 * sal ^ (1.5) - 0.0996 * sal * sal
C < - -24.4344 - 25.085 * sqrt(sal) - 0.2474 * sal
D < - 0.053105 * sqrt(sal)

K_BOH3 < - exp(A + B / t + C * log(t) + D * t);

ans < - 10 ^ -(-log10(K_BOH3) + log10(ahFreeToTotFactor(sal, t, 0)))

return (ans)
}


# H3O+, OH-, & pKW ----

calcHydronium < - function(ph)
{

return (10.0 ^ (-ph))
}

calcHydroxide < - function(ph, t, sal)
{

if (is.null(sal))
return ()

kWToTheTen < - log10(calcKWMehrbach(t, sal))

return (10.0 ^ (kWToTheTen + ph))
}


# KW(T, S) from Miller-o (1995),
# in Dickson & Goyet (1994), Ch. 5, p. 18
# pH scale: TOTAL  units: (mol/kg-soln)^2
calcKWMehrbach < - function(temp, sal)
{

if (is.null(sal))
return ()

expSum < - 148.9652;  # NB: "148.965 02" in Zeebe & Wolf-Gladrow code
expSum < - expSum - 13847.26 / temp
expSum < - expSum - 23.6521 * log(temp)
expSum < - expSum + (-5.977 + (118.67 / temp) + 1.0495 * log(temp)) * sqrt(sal)
expSum < - expSum - 0.01615 * sal;

KW < - exp(expSum);  # still on TOTAL scale
pKW < - -log10(KW);  # still on TOTAL scale

# ** NB: convert to FREE pH scale, as per AquaEnv
pKW < - pKW + log10(ahFreeToTotFactor(sal, temp, 0.0))

return (10 ^ (-pKW))
}

# ---- alpha-sub-i ----

alphaZero < - function(temp, sal, ph)
{

# NB: declare p LOCALLY until incorporate in calcs
p < - 0.0

h < - calcHydronium(ph)

k1 < - getK1(temp, sal, p)

k2 < - getK2(temp, sal, p)

numerator < - h * h

return (numerator / calcAlphaDenom(h, k1, k2))
}


alphaOne < - function(temp, sal, ph)
{

# NB: define p LOCALLY until incorporate in calcs
p < - 0.0

h < - calcHydronium(ph)

k1 < - getK1(temp, sal, p)

k2 < - getK2(temp, sal, p)

numerator < - h * k1;

return (numerator / calcAlphaDenom(h, k1, k2))
}

alphaTwo < - function(temp, sal, ph)
{

# NB: define p LOCALLY until incorporate in calcs
p < - 0.0

h < - calcHydronium(ph)

k1 < - getK1(temp, sal, p)

k2 < - getK2(temp, sal, p)

numerator < - k1 * k2;

return (numerator / calcAlphaDenom(h, k1, k2))
}

calcAlphaDenom < - function(h, k1, k2)
{

return (h * h + k1 * h + k1 * k2)
}

# T- and S-dependent K1 from Millero et al. (2006)
# ** pH scale: SWS for calculation, FREE returned
getK1 < - function(temp, sal, p)
{

# cat('\n==========================\n')
# cat('CARB_CALC, sal = ', sal, '\n')
# cat('CARB_CALC, NULL = ', is.null(sal), '\n')
# cat('CARB_CALC, {} = ', identical(sal, character(0)), '\n')
# cat('CARB_CALC, \'\' = ', identical(sal, ''), '\n')
# cat('==========================\n\n')

if (is.null(sal))
return ()

sqrtS < - sqrt(sal)
lnT < - log(temp)

pK1z < - -126.34048 + (6320.813 / temp) + 19.568224 * lnT  # was "19.56822.."
A < - 13.4191 * sqrtS + 0.0331 * sal - 0.0000533 * sal * sal
B < - -530.123 * sqrtS - 6.103 * sal
C < - -2.06950 * sqrtS
pK1 < - pK1z + A + (B / temp) + C * lnT

# ** NB: THIS conversion puts it on the FREE pH scale *from* the SWS scale, as per AquaEnv
# **     factor for sws2free = 1.0 / ahFreeToSwsFactorForSalinity:temp:pressure:
# **     when dealing with -log10, -log10(1 / ah) = -(-log10(ah)) = +log10(ahFreeToSWSFactor...)
pK1 < - pK1 + log10(ahFreeToSwsFactor(sal, temp, 0.0))

# ?? NB: no concentration scale conversion needed, as both on molinity [sic]

return (10 ^ (-pK1))  # K1
}


# T- and S-dependent K2 from Millero et al. (2006)
# ** pH scale: SWS for calculation
# ** Return: K2 -- not pK2 -- on FREE pH scale

# ----> NB: Millero (2010) slightly changes some coefficients <----

getK2 < - function(temp, sal, p)
{

if (is.null(sal))
return ()

sqrtS < - sqrt(sal)
lnT < - log(temp)

pK2z < - -90.18333 + (5143.692 / temp) + 14.613358 * lnT

A < - 21.0894 * sqrtS + 0.1248 * sal - 0.0003687 * sal * sal  # was "21.08945"
B < - -772.483 * sqrtS - 20.051 * sal
C < - -3.3336 * sqrtS  # was "-3.3336" or "3.32254"

# ** NB: THIS pK2 is on the SWS pH scale
pK2 < - pK2z + A + (B / temp) + C * lnT;

pK2 < - pK2 + log10(ahFreeToSwsFactor(sal, temp, 0.0))

return (10 ^ (-pK2))
}

# ---- Proton Activity Coefficient ----

calcProtonActivityCoeffZg < - function(temp, sal, p)
{

rootGamma < - sqrt(calcIonicStrength(sal))

myHActivityCoeff < - 1820000.0 * (79 * temp) ^ (-1.5)

myHActivityCoeff < - myHActivityCoeff * ((rootGamma / (1 + rootGamma)) - 0.2 * calcIonicStrength(sal))

myHActivityCoeff < - 10 ^ (-myHActivityCoeff)

return (myHActivityCoeff)
}


# ---- ah pH Conversion Methods ----
# ** NB: calcKSdicksonOfTemp: uses ionic strength calc,
# **     which can return I(s) in either MOLAL or MOLIN

ahMolalToMolinforSalinity < - function(sal)
{

return (1.0 - 0.001005 * sal)
}


ahFreeToSwsFactor < - function(sal, temp, p)
{

return (1 + (calcTS(sal) / calcKsDickson(temp, sal, 0.0)) +
        (calcTF(sal) / calcKfDickson(temp, sal, 0.0)))
}


ahFreeToTotFactor < - function(sal, temp, p)
{

return (1 + (calcTS(sal) / calcKsDickson(temp, sal, 0.0)))
}


ahSwsToNbsFactor < - function(sal, temp, p)
{

return (calcProtonActivityCoeffZg(temp, sal, 0.0) / ahMolalToMolinforSalinity(sal))
}


# NB: pH(NBS) = pH(Free) -
#               log10(ahFreeToSwsFactor(S, T(Kelvin), 0)) -
#               log10(ahSwsToNbsFactor())
phNbsToPhFree < - function(ph, sal, temp, p)
{

return (ph +
        log10(ahSwsToNbsFactor(sal, temp, p)) +
        log10(ahFreeToSwsFactor(sal, temp, p))
        )
}


# F & S ----

calcTF < - function(sal)
{

return (0.0000019522 * sal)
}

calcTS < - function(sal)
{

return (0.0008067267 * sal)
}

# pH scale: FREE
# concentration scale: mole/kg-H2O ?? -> molin...?
calcKfDickson < - function(temp, sal, p)
{

fluorFactor1 < - 1590.2 / temp
fluorFactor2 < - -12.641
fluorFactor3 < - 1.525 * sqrt(calcIonicStrength(sal))

# ** NB: molalToMolin factor in sqrt()...
#    double fluorFactor3 = 1.525 * sqrt([self calcIonicStrength:s] * (1.0 - 0.001005 * s));

molal2molin < - log(1.0 - 0.001005 * sal)

KF < - fluorFactor1 + fluorFactor2 + fluorFactor3 + molal2molin

return (exp(KF))
}

# bisulfate dissociation
# Dickson (1990); DOE (1994), ch. 5 p. 13; Z & W-G (2001) p. 260
# pH scale: Free
# concentration scale: mol/kg-H2O, CONVERTED TO AND RETURNED AS mol/kg-soln (molin)
# **** NB **** if called from within pH conversion, T already C -> K *******
# **** NB **** else if called from getKS(), must add 273.15 in call ****************
calcKsDickson < - function(temp, sal, p)
{

# ** NB: ionic strength calc now returns molal, so
# **     change to molin (mol/kg-soln) here for this calc
#    double myIS = [self calcIonicStrength:s] * (1.0 - 0.001005 * s);
myIS < - calcIonicStrength(sal)

sulfFactor1 < - 141.328 - 4276.1 / temp
sulfFactor2 < - -23.093 * log(temp)
sulfFactor3 < - (324.57 - 47.986 * log(temp) - 13856 / temp) * sqrt(myIS)
sulfFactor4 < - (-771.54 + 114.723 * log(temp) + 35474 / temp) * myIS
sulfFactor5 < - -2698.0 * myIS ^ (1.5) / temp
sulfFactor6 < -  1776.0 * myIS ^ 2 / temp

molal2molin < - log(1.0 - 0.001005 * sal)

# ** in mol/kg-soln (MOLIN)
KS < - sulfFactor1 + sulfFactor2 + sulfFactor3 + sulfFactor4 + sulfFactor5 + sulfFactor6 + molal2molin

# ** in mol/kg-H2O (MOLAL)
#	double KS = sulfFactor1 + sulfFactor2 + sulfFactor3 + sulfFactor4 + sulfFactor5 + sulfFactor6;

return (exp(KS))
}


# ionic strength (molal) ----

# ** calc ionic strength for SW from salinity
# ** (for low-salinity solns, implement Butler's formulae)
# ** concentration scale: mol/kg-H2O (molal)
# ** CONVERT TO MOLIN??
calcIonicStrength < - function(sal)
{

myIS < - 19.924 * sal / (1000.0 - 1.005 * sal)  # mole/kg-H2O (molal)
# //    myIS *= 1.0 - 0.001005 * sal           # mole/kg-soln (molin)
return (myIS)
}

# ---- calc Critical CO2 border ----
# return: g/kg-soln

calcCo2OfDic < - function(dic, t, s, ph)
{

myCo2 < - dic * alphaZero(t, s, ph)

# return mg/kg
myCo2 < - 44.0096 * myCo2

return (myCo2)
}

# used to insure that the unsafe CO2 region on the Deffeyes Dgm is filled properly
calcPhForCritCO2FromDIC < - function(dic, co2Crit, t, s)
{

# dic must be > (not == to?) co2Crit
if (dic <= co2Crit) {
return ()
}

# calculate pH at which, for a given DIC, [CO2] exceeds the entered CO2Crit

k1 < - getK1(t, s)
k2 < - getK2(t, s)

a < - co2Crit - dic
b < - co2Crit * k1
c < - co2Crit * k1 * k2

# cat('      t = ', t, ',         s = ', s, '\n')
# cat('co2Crit = ', co2Crit, ', dic = ', dic, '\n')
# cat('a = ', a, ', b = ', b, ', c = ', c,'\n')

discrim < - b ^ 2 - 4 * a * c

# NB: Want 'negative' of sqrt to insure 'positive' result (denom is negative -- always here?)
x < - (-b - sqrt(discrim)) / (2 * a)

# cat('x = ', x, '\n\n')

return (-log10(x))
}


# calc alkalinity for DIC and pH (FREE)
# use to trace critical CO2 boundary when supply pH of crit CO2 & DIC
calcAlkOfDicPhTempSal < - function(dic, ph, t, s)
{

alk < - dic * (alphaOne(t, s, ph) + 2 * alphaTwo(t, s, ph))

alk < - alk + calcHydroxide(ph, t, s)

alk < - alk - calcHydronium(ph)

alk < - alk + calcBorate(ph, t, s)

return (alk)
}


# calc DIC for a given [Alk] & pH -- COULD USE WHEN pH is pHCrit for CO2Crit, no ???
# ** What are the units of DIC? Do [Alk] units need converted from "/liter" to "/kg" ?
# calcDicOfAlk <- function(alk,ph,t,s) {
#
#   m <- alphaOne(t,s,ph)
#
#   m <- m + 2 * alphaTwo(t,s,ph)
#
#   dic <- (alk - calcHydroxide(ph,t,s) -
#                   calcBorate(ph,t,s) +
#                   calcHydronium(ph)) / m
#
#   return(dic)
# }


# pragma mark - pH of [Alk] & DIC
# ** NB: Use the secant method to solve the resulting quartic polynomial
calcPhForAlkDic < - function(alk, dic, t, s)
{

# ** assemble the Ki and concentrations...
KW < - calcKWMehrbach(t, s)
K1 < - getK1(t, s, 0.0)
K2 < - getK2(t, s, 0.0)
B < - calcBorateConcOfSalinity(s)
KB < - calcBorateFactor(t, s)

# ** calculate the coefficients of the quartic polynomial...
q4 < - 1 - KW
q3 < - alk - KW * KB + KB - K1 * KW + K1
q2 < - alk * KB - KB * B + alk * K1 - K1 * KW * KB + K1 * KB - K1 * K2 * KW + K1 * K2 - dic * K1
q1 < - alk * K1 * KB - K1 * KB * B + alk * K1 * K2 - K1 * K2 * KW * KB + K1 * K2 * KB - dic * K1 * (KB + 2 * K2)
q0 < - (K1 * K2 * KB) * (alk - 2 * dic - B)

thePh < - calcSecantMethod(q4, q3, q2, q1, q0)
thePh < - -log10(thePh)

return (thePh)
}


# ---- TANCalc methods ----

# calc pH at which un-ionized ammonia becomes unsafe for a given level of TAN
# from Fivelstad formula
calcCritPhTan < - function(tan, unIonized, temp, sal)
{

temp < - temp - 273.15  # added for R version

critPhTan < - 10.0869 + 0.002 * sal - 0.034 * temp
critPhTan < - critPhTan - 0.43429448190325182765 * log((tan - unIonized) / unIonized)

return (critPhTan)
}

# calc % un-ionized ammonia according to Fivelstad formula
calcUnIonPoStoFivelsted < - function(mypH, temp, sal)
{

temp < - temp - 273.15  # added for R version

unIonPoSto < - 9.242
unIonPoSto < - unIonPoSto + 0.002 * sal
unIonPoSto < - unIonPoSto + (0.034 * (24.85 - temp) - mypH)
unIonPoSto < - 1.0 / (1.0 + 10 ^ unIonPoSto)

return (unIonPoSto)
}

# calc % un-ionized ammonia according to Johansson & Wedborg formula
calcUnIonPoStoJohanssonWedborg < - function(mypH, temp, sal)
{

unIonPoSto < - -0.467
unIonPoSto < - unIonPoSto + 0.00113 * sal
#  unIonPoSto <- unIonPoSto + 2887.9 / (temp + 273.15) # original formulation
unIonPoSto < - unIonPoSto + 2887.9 / temp
unIonPoSto < - unIonPoSto + -mypH
unIonPoSto < - 1.0 / (1.0 + 10 ^ unIonPoSto)

return (unIonPoSto)
}

# TANCalc methods from WQTech 0.95 (xCode project)
# pragma mark - NH3 & HNO2 calcs

# ** calc the percentage of un-ionized ammonia
# ** [CHECK] pH on FREE proton scale...Yes

# ** output percentage (same for total ammonia or total ammonia nitrogen)
# ** and percentage need not be converted to, e.g., the NBS scale, eh?
# ** double thePercentage = 100.0 / (1.0 + (1.0 / pow(10,-(-log10(kNH4))+pH)));

# ** NB: "threshold level of 0.025 mg/L (25 μg/L)
# **     "Un-ionized Ammonia of 0.05 mg/L (50 μg/L) may harm fish.
# **     "As Un-ionized Ammonia approaches 2.0 mg/L (2000 μg/L), fish will begin to die."

percentNh3ForTemp < - function(t, sal, ph)
{

if (is.null(sal))
return ()

pKNH4 < - -log10(getKNH4(t, sal, 0))

expOfTen < - pKNH4 - ph

return (100.0 / (1.0 + 10 ^ expOfTen))
}

# NB: On the FREE scale
critPhFreeForTanMillero < - function(tan, uia, t, s)
{

# cat('IN critPhFreeForTanMillero, uia = ', uia, ' and sal = ', s, '\n')

return (-log10((tan / uia) - 1) - log10(getKNH4(t, s, 0)))
}

# ** T-, S-, & pH-dependent K of NH4+ from Millero et al. (1995)
# ** pH scale: SWS
# ** concentration scale: mol/kg-soln
getKNH4 < - function(t, sal, p)
{

if (is.null(sal))
return ()

sqrtS < - sqrt(sal)

A < - -0.25444 + 0.46532 * sqrtS - 0.01992 * sal
B < - -6285.33 - 123.7184 * sqrtS + 3.17556 * sal
D < - 0.0001635

KNH4 < - A + (B / t) + D * t

# ** NB: THIS conversion puts it on the FREE pH scale, as per AquaEnv
# **     factor for sws2free = 1.0 / ahFreeToSwsFactorForSalinity:temp:pressure:
# **     WHEN DEALING WITH -log10, -log10(1 / ah) = -(-log10(ah)) = +log10(ahFreeToSWSFactor...)

pKNH4 < - -log10(exp(KNH4))

pKNH4_FREE < - pKNH4 + log10(ahFreeToSwsFactor(sal, t, 0.0))

# ** do a calc in terms of NBS scale
pKNH4_Nbs < - pKNH4 - log10(ahSwsToNbsFactor(sal, t, 0.0))

sf < - (log10(ahFreeToSwsFactor(sal, t, 0.0)) +
        log10(ahSwsToNbsFactor(sal, t, 0.0)))

pKNH4_Nbs2 < - pKNH4_FREE - sf

return (10 ^ (-pKNH4_FREE))  # K-NH4
}

# ---- calc CO3 ----

calcCO3 < - function(dic, t, s, ph)
{

carbonate = dic * alphaTwo(t, s, ph)

return (carbonate)
}


# ---- CO2 GAS CALCS ----

# $K0_CO2, see: p. 536
# // ** NB: CO2 sat = (fugacity CO2) * (Henry's coefficient CO2)

calcCO2SolubilityAhOfTempAndSal < - function(t, sal)
{
# // ** Henry's in mol/(kg-soln atm)
A < -    0.023517 * sal - 167.810768
B < - 9345.17
C < -   23.3585
D < -   -0.00023656 * sal
E < -    0.00000047036 * sal

co2Henrys < - A + B / t + C * log(t) + D * t + E * t * t

cat("in calcCO2SolubilityAhOfTemp:...Henry's const = ", exp(co2Henrys), '\n')

return (exp(co2Henrys))
}

# Henry's Constant

# // ** Henry's constant for CO2 FUGACITY, K_sub_0
# in Dickson "Best Practices...",
# // ** Section 7.1, Eqn 30, via Weiss (1974)
# // **    Units: mole/(kg-soln * atm)
# // ** pH Scale: ??
calcKHWeissOfTempAndSal < - function(t, s)
{

# //	t += 273.15; // convert Celsius to Kelvin

exp1 < - -60.2409
exp2 < -  9345.17 / t
exp3 < -  23.3585 * log(t / 100.0)
exp4 < -  0.023517
exp5 < - -0.00023656 * t
exp6 < -  0.00000047036 * (t * t)

expSum < - exp1 + exp2 + exp3 + s * (exp4 + exp5 + exp6)

# cat("Henry's const = ", exp(expSum), 'mol/(kg*atm)\n')
# cat("Henry's const = ", exp(expSum) * 1000, 'mmol/(kg*atm)\n')
# cat("Henry's const = ", exp(expSum) * 1000000, 'μmol/(kg*atm)\n')

return (exp(expSum))
}


# return: mol/kg-soln (WITHOUT subtracting VP)
calc_CO2_gasSat < - function(t, s, co2_fugacity)
{

kh_co2 < - calcKHWeissOfTempAndSal(t, s)

return (kh_co2 * co2_fugacity)
}


# return: μmol/kg-soln  (**WITH** subtracting VP)
#
# NB: NO NEED for vp_ic in original function,
#     as calcVP(t, s) implementd in function body
#
# calc_CO2_gasSat_microMol_kg <- function(t, s,
#                                         bp_ic, vp_ic,
#                                         co2_mole_fraction) {

# [DEPRECATED] in favor of eponymous function (immediately below)
# that uses more detailed Weiss formulation for CO2 solubility

# calc_CO2_gasSat_microMol_kg <- function(t, s,
#                                         bp_ic,
#                                         co2_mole_fraction) {
#
#   # [mole / (kg-soln * atm)] * [1000 mmol / mol] * (atm - atm) * (μmol / mol) / [10^6 ---]
#   co2_sat_microMol_kg <-
#     calcKHWeissOfTempAndSal(t, s) *
#     (bp_ic - calcVP(t, s)) *
#     co2_mole_fraction
#
#   return(co2_sat_microMol_kg)
# }


# after Weiss (1974)
# see Colt, p. 256, Eqn. A-9

# see DEPRECATED function immediately above...
# calc_CO2_gasSat_microMol_kg_Weiss_74 <- function(t,                    # K
calc_CO2_gasSat_microMol_kg < - function(t,  # K
s,  # ppt
bp_ic,  # atm
co2_mole_fraction) {  # unitless

# Universal Gas Constant, [(atm * L) / (mol * K)]
R < - 0.08205601

# conversion from [cm^3 / mol] to [L / mol] for B, delta, & v_bar (below)
cc_to_L < - 0.001

B < - -1636.75 + 12.0408 * t - 0.0327957 * t ^ 2 + 0.0000316528 * t ^ 3

B < - cc_to_L * B

# cross-virial coefficient, CO2 & air, [cm3 / mol]
delta < - 57.7 - 0.118 * t
delta < - cc_to_L * delta

# partial molar volume of CO2, [cm^3 / mol]
v_bar < - 32.3
v_bar < - cc_to_L * v_bar

my_factor < - co2_mole_fraction * calcKHWeissOfTempAndSal(t, s) * (bp_ic - calcVP(t, s))

pwr_term_1 < - bp_ic * ((B + 2 * delta) / (R * t))

pwr_term_2 < - v_bar * ((1 - bp_ic) / (R * t))

co2_sat_microMol_kg < - my_factor * exp(pwr_term_1 + pwr_term_2)

# cat(' my_factor: ', my_factor, '\n')
# cat('pwr_term_1: ', pwr_term_1, '\n')
# cat('pwr_term_2: ', pwr_term_2, '\n')
# cat('pwr_term_2: ', pwr_term_2, '\n')

return (co2_sat_microMol_kg)  # because of deprecated legacy function, NOT multiply by 10^6 for μmol / kg
}


# return: mg/L  (WITH subtracting VP)
calc_CO2_gasSat_mg_L < - function(t, s,
# bp_ic, vp_ic,
bp_ic,
co2_mole_fraction) {

# cat('in calc_CO2_gasSat_mg_L...\n')
# cat('                t = ', t, '\n')
# cat('                s = ', s, '\n')
# cat('            bp_ic = ', bp_ic, '\n')
# cat('co2_mole_fraction = ', co2_mole_fraction, '\n\n')

# co2_sat_mg_L <- (calcKHWeissOfTempAndSal(t, s) * 1000.0) *
#   # (bp_ic - vp_ic) * (co2_mole_fraction / 1000.0 ) *
#   (bp_ic - calcVP(t, s)) * (co2_mole_fraction / 1000000.0 ) *
#   (calcRho(t, s) / 1000.0) * MW_CO2

co2_sat_mg_L < - calc_CO2_gasSat_microMol_kg(t, s,
                                             # bp_ic, vp_ic,
                                             bp_ic,
                                             co2_mole_fraction) *
(calcRho(t, s) / 1000.0) * (MW_CO2 / 1000.0)

return (co2_sat_mg_L)
}


# return: L / (L * atm)
calcBunsen_CO2 < - function(t, s)
{

# mol / (kg-soln * atm)
kh_co2 < - calcKHWeissOfTempAndSal(t, s)

# L / (kg * atm)
beta_Lkg_atm < - kh_co2 * MV_CO2

# cat('In calcBunsen_CO2(', t, ', ', s, ') ...\n')
# cat(' ... beta_Lkg_atm = ', beta_Lkg_atm, ' L / (kg * atm)\n')
# cat('  calcRho(', t, ', ', s, ') = ', calcRho(t, s) / 1000, ' kg/L \n')
# cat(' ...   Bunsen CO2 = ', beta_Lkg_atm * calcRho(t, s) / 1000, ' L / (L * atm)\n')

# return: L / (L * atm)
return (beta_Lkg_atm * calcRho(t, s) / 1000)
}



# ---- O2 (see: converter_gasses.R) ----

# K_O2, MOL/kg-soln*atm
calcO2SolubilityAhOfTempAndSal < - function(t, sal)
{
# // ** Henry's in mol/(kg-soln atm)
A = -0.037362 * sal - 846.9978
B = 25559.07
C = 146.4813
D = -0.22204 + 0.00016504 * sal
E = -0.00000020564 * sal

o2Henrys = A + B / t + C * log(t) + D * t + E * t * t

cat("in calc_O2_SolubilityAhOfTemp:...Henry's const = ", exp(o2Henrys), 'μmol/kg-soln*atm\n')

cat('O2 fugacity, ', 0.20946, ' atm * O2 solubility, ',
    exp(o2Henrys) / 10 ^ 6, ' MOL/kg-soln*atm = ',
    0.20946 * exp(o2Henrys) / 10 ^ 6, 'mol/kg-soln \n')

# return: MOL/kg-soln*atm
return (exp(o2Henrys) / 10 ^ 6)
}


# ---- Omega-calcite & -aragonite ----

convertCaToMolesPerKg < - function(ca, t, s)
{

caInMolesPerKg < - ca / 40.078
caInMolesPerKg < - caInMolesPerKg / calcRho(t, s)

#  463.0 mg/L => 0.011303558407068858 mol/kg

return (caInMolesPerKg)
}


# ** Compare with Plummer & Busenberg (1982) formula used in Wojtowicz swimming pool
# ** paper "A Revised and Updated Saturation Index Equation",
# ** J. Swimming Pool & Spa Industry, 3(1):28 - 34
# ** log(Ks) =  -171.9065 - 0.077993*T + 2839.319/T + 71.595*log(T)
# ** NB: It's the SAME as calcKspCa(myTemp, 0.00), eh?
# ** from Mucci (1983)
# ** concentration scale: mol^2 / kg-soln^2

calcKspCa < - function(t, s)
{

#	t += 273.15;   # convert from C to K

omegaCa < - -171.9065
omegaCa < - omegaCa + -0.77712 * sqrt(s)
omegaCa < - omegaCa + -0.07711 * s
omegaCa < - omegaCa + 0.0041249 * s ^ 1.5

omegaCa < - omegaCa + (2839.319 + 178.34 * sqrt(s)) / t

omegaCa < - omegaCa + 71.595 * log10(t)

omegaCa < - omegaCa + (-0.077993 + 0.0028426 * sqrt(s)) * t

return (10 ^ omegaCa)
}

calcKspAr < - function(t, s)
{

#	t += 273.15;   # convert from C to K

omegaAr < - -171.945
omegaAr < - omegaAr + -0.068393 * sqrt(s)
omegaAr < - omegaAr + -0.10018 * s
omegaAr < - omegaAr + 0.0059415 * s ^ 1.5

omegaAr < - omegaAr + (2903.293 + 88.135 * sqrt(s)) / t

omegaAr < - omegaAr + 71.595 * log10(t)

omegaAr < - omegaAr + (-0.077993 + 0.0017276 * sqrt(s)) * t

return (10 ^ omegaAr)
}


calcOmegaCa < - function(dic, ca, t, s, ph)
{

result < - ca * calcCO3(dic, t, s, ph)

result < - result / calcKspCa(t, s)

return (result)
}

calcOmegaAr < - function(dic, ca, t, s, ph)
{

result < - ca * calcCO3(dic, t, s, ph)

result < - result / calcKspAr(t, s)

return (result)
}


# ---- Langelier ----

# ** put pK values on NBS scale
# ** input as K values, convert to pK values
convertFreeToNbsForLangelier < - function(k2, kspca, kspar, t, s, p)
{

sf < - log10(ahFreeToSwsFactor(s, t, p)) +
log10(ahSwsToNbsFactor(s, t, p))

return (c(-log10(k2) - sf, -log10(kspca) - sf, -log10(kspar) - sf))
}


# ----calc OMEGA boundary ----

# ** [NEW--**CORRECTED**] to calc CALCITE saturation pH

calcPhSatForOmegaCa < - function(omega, alk, ca, t, s, p)
{

K1 < - getK1(t, s, p)
K2 < - getK2(t, s, p)
Kw < - calcKWMehrbach(t, s)
Ksp < - calcKspCa(t, s)
B < - calcBorateConcOfSalinity(s)
KB < - calcBorateFactor(t, s)
omf < - omega * Ksp / ca;

# ** 0.01028 mol/kg-soln @ 19.374 C & 35 psu,
# ** Riley & Tongudai (1967)

# ** Implement the secant algorithm
q4 < - 0.0
q3 < - K1 * (K2 - omf)
q2 < - K1 * (K2 * (alk + KB) - omf * (KB + 2 * K2))
q1 < - K1 * K2 * (KB * (alk - B - 2 * omf) - Kw)
q0 < - K1 * K2 * (-Kw * KB)

thePh < - calcSecantMethod(q4, q3, q2, q1, q0)
thePh < - -log10(thePh)

return (thePh)
}


calcPhSatForOmegaAr < - function(omega, alk, ca, t, s, p)
{

K1 < - getK1(t, s, p)
K2 < - getK2(t, s, p)
Kw < - calcKWMehrbach(t, s)
Ksp < - calcKspAr(t, s)
B < - calcBorateConcOfSalinity(s)
KB < - calcBorateFactor(t, s)
omf < - omega * Ksp / ca;

# ** 0.01028 mol/kg-soln @ 19.374C & 35 psu,
# ** Riley & Tongudai (1967)

# ** Implement the secant algorithm
q4 < - 0.0
q3 < - K1 * (K2 - omf)
q2 < - K1 * (K2 * (alk + KB) - omf * (KB + 2 * K2))
q1 < - K1 * K2 * (KB * (alk - B - 2 * omf) - Kw)
q0 < - K1 * K2 * (-Kw * KB)

thePh < - calcSecantMethod(q4, q3, q2, q1, q0)
thePh < - -log10(thePh)

return (thePh)
}


# [NEW OMEGA calc for iQuaCalc] ----

# [TRY THIS] calculate pH (and then [Alk]) for DIC and saturation omega-calcite
calc_ph_omega_ca_given_dic < - function(dic, ic_ca, ic_temp, ic_sal)
{

# treat as a quadratic...

k1_times_k2 < - getK1(ic_temp, ic_sal, 0) * getK2(ic_temp, ic_sal, 0)

a < - 1.0

b < - k1_times_k2

c < - k1_times_k2 - ((dic * k1_times_k2 * ic_ca) / calcKspCa(ic_temp, ic_sal))

h_plus < - (-b + sqrt(b ^ 2 - 4 * a * c)) / (2 * a)

ph_crit < - -log10(h_plus)

# cat('critical pH for Ω-calcite = ', ph_crit, ' (scale? Total?) \n')
}


# to plot Omega = 1 (saturation) curve
# @param omega set equal to 1.0 (for now; later, maybe user-entered)
# @param ic_temp in K
# @param ic_sal in ppt
# @param ic_ca, calcium in mole/kg-soln
draw_omega_isopleth_ca < - function(omega, ic_temp, ic_sal, ic_ca)
{

# now set omega_ca_prime to "1.0"
omega_ca_prime < - 1.0

# define starting DIC
dic_crit_omega_ca < - calcKspCa(ic_temp, ic_sal) * omega_ca_prime / ic_ca
cat('dic_crit_omega_ca = ', dic_crit_omega_ca, 'mol/kg \n')

# compute pH for dicCritOmegaCa and omega_ca_prime for T, S, & pressure
ph_crit_start < - calcPhTotForOmegaCa(omega_ca_prime, dic_crit_omega_ca,
                                      ic_ca,
                                      ic_temp, ic_sal, 0)
# cat('    ph_crit_start = ', ph_crit_start, ' \n')

my_dic < - dic_crit_omega_ca

while (my_dic < 0.005) {

my_ph < - calc_ph_omega_ca_given_dic(my_dic, ic_ca, ic_temp, ic_sal)
my_alk < - calcAlkOfDicPhTempSal(my_dic, my_ph, ic_temp, ic_sal)
cat('my_dic = ', my_dic, ', my_alk', my_alk, ', pH = ', my_ph, '\n')

# ph_crit_start <- calcPhTotForOmegaCa(omega_ca_prime, my_dic,
#                                      ic_ca,
#                                      ic_temp, ic_sal, 0)
my_dic < - my_dic + 0.0002
}

}


# ***OLD [??]*** Omega boundary calc ----
# calc the pH at which, for given DIC, T, S, & P, Omega-Ca = omega
# mais, en reflechissant, c'est peut-etre plus pratique en avoir un autre ou on y
# passe les K1- & K2-sub-i, qui ne changeront pas ici (donne que t, s, & p ne changent pas)
# alors, en calculant la ligne dans le diagrame pour omega, tout ce qu'il faut y passer,
# c'est le DIC (qui change a svaki korak)...et les "constants" K1(T, S, P) et K2(T, S, P)
# (voir ci-dessous)
calcPhTotForOmegaCa < - function(omega, dic, ca, t, s, p)
{

K1 < - getK1(t, s, p)
K2 < - getK2(t, s, p)
Ksp < - calcKspCa(t, s)
#        double Ca  = calcKsyCa(t, s);

# Ca <- convertCaToMolesPerKg(ca, t, s)    # [mol/kg-soln] & 40.078 g/mol
# Ca  <- calcSWCa(s)
# cat('Ca - ', Ca, 'mol/kg-soln \n')
# 0.01028 mol/kg-soln @ 19.374C & 35 psu,
# Riley & Tongudai (1967)

# **********************************************************************
# **********************************************************************
if (s < 5)
    ca < - 0.01028 / 100.0  # CHEAP KLUDGE for freshwater
# **********************************************************************
# **********************************************************************

# Implement the secant algorithm
q4 < - 0.0
q3 < - 0.0
q2 < - 1.0
q1 < - K1
q0 < - K1 * K2 * (1.0 - (ca * dic) / (omega * Ksp))

# **************************************** //
thePh < - calcSecantMethod(q4, q3, q2, q1, q0)
thePh < - -log10(thePh)
# **************************************** //
# cat("QUADRATIC Secant pH (Ca): ", thePh, '\n')
cat("Ca -> (DIC, [Alk]) = (", dic, ", ", calcAlkOfDicPhTempSal(dic, thePh, t, s), ")\n")

# solve the quadratic with the quadratic formula
root < - (-q1 + sqrt(q1 * q1 - 4 * q0)) / 2
# cat("root: ", root, '\n')
root < - -log10(root)
cat("Ca-secant pH: ", thePh, " vs quadForm pH: ", root, '\n\n')

return (root)

}


# ---- Conductivity to Salinity ----

conductivityToSalinity < - function(c, t, p, unitsIn, unitsOut)
{

# ** 0. convert input units to ICU, S/m
if (unitsIn != 'S/m') {
cat('In CarbCalc.R\'s conductivityToSalinity(), CHANGE from ', unitsIn, ' to ', 'S/m!!\n')
c < - c * conductivityToIcUFactor(unitsIn, 'S/m')
}

myConductivity < - 4.2914  # ** S/m

# ** 1. calculate conductivity ratio R
myR < - c / myConductivity

# ** 2. calculate rsubt -- function of temperature
c0 < -  0.6766097
c1 < -  0.0200564
c2 < -  0.0001104259
c3 < - -0.00000069698
c4 < -  0.0000000010031

rSubT < - c0 + c1 * t + c2 * t * t + c3 * t * t * t + c4 * t * t * t * t

# ** 3. calculate Rsubp -- function of pressure
e0 < -  0.00002070
e1 < - -0.0000000006370
e2 < -  0.000000000000003989
d1 < -  0.03426
d2 < -  0.0004464
d3 < -  0.4215
d4 < - -0.003107

RsubP < - 1 + p * (e0 + e1 * p + e2 * p * p) / (1 + d1 * t + d2 * t * t + (d3 + d4) * myR)

# ** 4. calclate RsubT
RsubT < - myR / (rSubT * RsubP)

# ** 5. calculate S'
k < -  0.0162
b0 < -  0.0005
b1 < - -0.0056
b2 < - -0.0066
b3 < - -0.0375
b4 < -  0.0636
b5 < - -0.0144

Sprime < - (t - 15) / (1 + k * (t - 15))

Sprime < - Sprime * (b0 + b1 * sqrt(RsubT) + b2 * RsubT + b3 * RsubT ^ 1.5 + b4 * RsubT * RsubT + b5 * RsubT ^ 2.5)

# ** 6. finish it off to calc salinity
a0 < -  0.0080
a1 < - -0.1692
a2 < - 25.385
a3 < - 14.0941
a4 < - -7.0261
a5 < -  2.7081

mySal < - a0 + a1 * sqrt(RsubT) + a2 * RsubT + a3 * RsubT ^ 1.5 + a4 * RsubT * RsubT + a5 * RsubT ^ 2.5 + Sprime

# ** 7. return salinity in ppt
return (mySal)
}

conductivityToIcUFactor < - function(inUnits, outUnits)
{

# convert inUnits to IC Units
if (inUnits == 'μS/cm')
    return (0.0001)
else if (inUnits == 'mS/cm')
return (0.1)
else
return (1.0)
}
