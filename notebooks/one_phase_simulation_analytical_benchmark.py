import matplotlib.pyplot as plt

import numpy as np

import pint

import _setup

from flow.PorMed import OnePhaseRadialTransient as transient
from flow.PorMed import OnePhaseRadialPseudoSteady as pseudosteady

from flow.PorMed import OnePhase as singlephase

## INPUT

p = 0.15

ur = pint.UnitRegistry()

k = ur.Quantity(200,'millidarcy').to('m^2').magnitude
h = ur.Quantity(20,'ft').to('m').magnitude
A = ur.Quantity(40,'acre').to('m^2').magnitude

ct = ur.Quantity(25e-6,'1/psi').to('1/Pa').magnitude
qo = ur.Quantity(800*1.2,'oil_bbl/day').to('m^3/second').magnitude
rw = ur.Quantity(0.25,'ft').to('m').magnitude
Pi = ur.Quantity(4500,'psi').to('Pa').magnitude

##times = ur.Quantity(np.array([10.,20,50,100,200]),'hour').to('second').magnitude

muo = ur.Quantity(1.5,'centipoise').to('Pa.s').magnitude

## SETTING MODELS

# Transient Solution
trs = transient(qo)

trs.PorRock.set_porosity(p)
trs.PorRock.set_permeability(k)
trs.PorRock.set_thickness(h)

trs.Well.set_radii(rw)
trs.Fluids.set_viscosity(muo)

trs.initialize(Pi,ctotal=ct)

trs.set_tmax(66900)
trs.set_times(timespace="log")
trs.set_observers(np.array([rw]))
trs.solve()

# Pseudo-Steady-State Solution
pss = pseudosteady(qo,shape="square")

pss.PorRock.set_area(A)
pss.PorRock.set_thickness(h)
pss.PorRock.set_porosity(p)
pss.PorRock.set_permeability(k)

pss.Well.set_radii(rw)

pss.Fluids.set_viscosity(muo)

pss.initialize(pressure0=Pi,ctotal=ct)

pss.set_times(timespace="log")

pss.solve()

# Numerical solution
sps = singlephase()

sps.PorRock.set_area(A)
sps.PorRock.set_thickness(h)
sps.PorRock.set_grids((31,31))
sps.PorRock.set_porosity(p)
sps.PorRock.set_permeability(k)

sps.Wells.set_names("Prod#1")
sps.Wells.Trajectory.set_tracks(((( 200,200,60),( 200,200,0)),))
sps.Wells.set_radii(rw)
sps.Wells.set_skinfactors(0)
sps.Wells.set_flowconds(["rate"],[-qo],["mobfluid"]) #conditions,limits,fluids

sps.Fluids.set_viscosity(muo)

sps.initialize(pressure0=Pi,ctotal=ct)

##sps.set_times(pss.tmax/5000,pss.tmax)
sps.set_times(1e1,1e4)

sps.set_transmissibility()
sps.set_matrix()
sps.set_externalBC()
sps.set_wells()

sps.solve()

Pwf = sps.postprocess()

##fig,axis = plt.subplots()
##
##sps.PorRock.plot(axis,showVertices=False)
##
##plt.show()

## RESULTS

ur.Quantity(trs.times,'sec').ito('days')
ur.Quantity(trs.pressure,'Pa').ito('psi')

ur.Quantity(pss.times,'sec').ito('days')
ur.Quantity(pss.pressure,'Pa').ito('psi')

ur.Quantity(sps.times,'sec').ito('days')
ur.Quantity(Pwf,'Pa').ito('psi')

plt.semilogx(trs.times[0,:],trs.pressure[0,:],label="Transient Solution")
plt.semilogx(pss.times[0,:],pss.pressure[0,:],label="Pseudo-Steady-State Solution")
plt.scatter(sps.times,Pwf,c="red",s=1,label="Finite Difference Solution")

plt.xlabel("Time [days]")
plt.ylabel("Pressure [psi]")

plt.legend()

plt.grid()

plt.show()
