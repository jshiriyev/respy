import unittest

import numpy as np

if __name__ == "__main__":
    import dirsetup

from flow.pormed import OnePhaseRadial

class TestRadialFlow(unittest.TestCase):

    def test_transient_ei(self):

        pass

    def test_transient_superposition(self):

        pass
##        clear
##        close all
##        clc
##
##        xw1 = -500;
##        yw1 = 0;
##
##        xw2 = 1000;
##        yw2 = 0;
##
##        Nx = 200;
##        Ny = 200;
##
##        Xlin = linspace(-2000,2000,Nx);
##        Ylin = linspace(-2000,2000,Ny);
##
##        [x,y] = meshgrid(Xlin,Ylin);
##
##        r12 = (x-xw1).^2+(y-yw1).^2;
##        r22 = (x-xw2).^2+(y-yw2).^2;
##
##        q1 = -250*1.32;
##        q2 = -400*1.32;
##
##        dt1 = 8;
##        dt2 = 5;
##
##        k = 25;
##        Pi = 2500;
##        phi = 0.16;
##        ct = 18e-6;
##        mu = 0.44;
##        h = 43;
##
##        P = Pi-(70.6*mu)/(k*h)*(...
##            q1*ei((-39.5*phi*mu*ct*r12)/(k*dt1))+...
##            q2*ei((-39.5*phi*mu*ct*r22)/(k*dt2)));
##
##        figure(1)
##        contourf(x,y,P);
##        colormap('jet')
##
##        caxis([2300,2500])
##        colorbar
##        pbaspect([1,1,1])

    def test_steady_state(self):

        def pressure(r):
            q = 250
            mu = 2.9
            h = 30
            B = 1.25
            pi = 4300
            k = 50
            re = 3000
            p = pi+141.2*(q*mu*B/k/h)*np.log(r/re)
            return p

        #r = np.array([0.33,1,5,10,20,50,100,200,300,400,500,1000,2000,3000])
        r = np.linspace(0.33,3000,2000)
        p = pressure(r)

        # print(r.shape)
        # print(p.shape)

        # fig,(ax1,ax2) = plt.subplots(2,1)

        # ax1.plot(r,p)

        # ax1.set_title('steady-state flow')

        # #ax1.set_xlabel('radius [ft]')
        # ax1.set_ylabel('pressure [psi]')

        # ax2.semilogx(r,p)

        # ax2.set_xlabel('radius [ft]')
        # ax2.set_ylabel('pressure [psi]')

        # plt.show()
        
    def test_conventional_solution(self):
        pass

##        q = -350*1.13/6.2898/86400
##
##        pi = 3000*6894.76
##
##        radius = np.linspace(0.333,3500,1000)*0.3048
##
##        well_radius = 0.333*0.3048
##
##        reservoir_radius = 3500*0.3048
##        
##        time = np.array([0.1,1,40,100])*86400
##
##        permeability = 25*9.869233e-16
##
##        porosity = 0.16
##
##        thickness = 50*0.3048
##
##        viscosity = 0.5e-3
##
##        totalCompressibility = 2e-5/6894.76
##
##        ls = singlephase(permeability,porosity,viscosity,totalCompressibility,well_radius,reservoir_radius,thickness)
##
##        ls.solve(radius,time,q)
##
##        plt.plot(radius,(pi+ls.deltap[:,0])/6894.76,label="at {} days".format(time[0]/86400))
##        plt.plot(radius,(pi+ls.deltap[:,1])/6894.76,label="at {} days".format(time[1]/86400))
##        plt.plot(radius,(pi+ls.deltap[:,2])/6894.76,label="at {} days".format(time[2]/86400))
##        plt.plot(radius,(pi+ls.deltap[:,3])/6894.76,label="at {} days".format(time[3]/86400))
##
##        plt.xlabel("radius [m]")
##        plt.ylabel("pressure [psi]")
##
##        plt.legend()
##
##        plt.show()
##
##        # For the unittest of transient
##
##        # radius = np.array([0.333,1,10,100,1000,3160])*0.3048
##        # time = np.array([0.1,1,10])*86400
##
##        # (pi+ls.deltap[0,:])/6894.76 must be np.array([2863.65131155 2837.93292432 2812.21451173])
##        # (pi+ls.deltap[1,:])/6894.76 must be np.array([2888.21501563 2862.49685438 2836.77846438])
##        # (pi+ls.deltap[2,:])/6894.76 must be np.array([2939.62390686 2913.93088964 2888.21501563])
##        # (pi+ls.deltap[3,:])/6894.76 must be np.array([2988.43390321 2965.08992094 2939.62390686])
##        # (pi+ls.deltap[4,:])/6894.76 must be np.array([3000.         2999.73190234 2988.43390321])
##        # (pi+ls.deltap[5,:])/6894.76 must be np.array([3000.         3000.         2999.7306157 ])

    def test_everdingen_solution(self):
        pass

        # EVERDINGEN SOLUTION

        # # beta = np.logspace(-4,3,10000)
        # # u = 1e-2
        # # print(bessel_y0(u))
        # # print(2/np.pi*(np.log(u)-0.11593))
        # # beta = np.linspace(0,100,100000)

        # # tt = np.linspace(8,40)
        # # tt = [0.06,0.08,0.1,0.12,0.14,0.16,0.18,0.2,0.22,0.24,0.26,0.28,0.3,0.35,0.4,0.45,0.5,0.55,0.6]
        # # tt = np.linspace(0.22,0.5,15)
        # # tt = np.linspace(0.4,0.6,11)
        # # tt = np.linspace(1,2,11)
        # # tt = np.linspace(1e-2,50,9)

        # tt = [1e-2,1e-1,0.5,3,5,7,9,11,16]

        # # print(tt)

        # sol = everdingen(rr=np.linspace(1,10,10000),tt=tt,RR=10,num_of_terms=100) #np.linspace(1,10)

        # sol.solve()

        # # print(sol.beta_n)
        # # print(sol.PP[0,:])

        # plt.plot(sol.rr,sol.PP[:,0])
        # plt.plot(sol.rr,sol.PP[:,1])
        # plt.plot(sol.rr,sol.PP[:,2])
        # plt.plot(sol.rr,sol.PP[:,3])
        # plt.plot(sol.rr,sol.PP[:,4])
        # plt.plot(sol.rr,sol.PP[:,5])
        # plt.plot(sol.rr,sol.PP[:,6])
        # plt.plot(sol.rr,sol.PP[:,7])
        # plt.plot(sol.rr,sol.PP[:,8])

        # plt.gca().invert_yaxis()

        # plt.show()

        # # J0B = bessel_j0(sol.beta_n)
        # # Y0B = bessel_y0(sol.beta_n)

        # # J1B = bessel_j1(sol.beta_n)
        # # Y1B = bessel_y1(sol.beta_n)

        # # print(np.pi*sol.beta_n*(J1B*Y0B-Y1B*J0B))

        # # print(sol.beta_n)

        # # # P = everdingen(10,1000)

        # # # f0 = P.root_function(R)
        # # # f1A = P.root_function_first_derivative(R)
        # # # f1N = P.root_function_first_derivative_numerical(R)

        # # # f0 = root_function(1e-20)

        # # # x, fsol, XE, FE, IE = odelay(root_function_first_derivative,f0,beta, events=[e1])

        # # # print(C[0]+D[0])

        # # # plt.plot(beta,root_function(beta,R),label="root function")
        # # # plt.plot(beta,root_function_first_derivative_numerical(beta,R),label="root function derivative")

        # # plt.plot(beta,sol.root_function(beta),label="J1BR*Y1B-J1B*Y1BR")
        # # plt.plot(sol.beta_n,np.zeros(sol.beta_n.shape),'.')
        # # # plt.semilogy(beta,np.abs(B),label="J1BR*Y1B_prime")
        # # # plt.semilogy(beta,np.abs(C),label="J1B_prime*Y1BR")
        # # # plt.semilogy(beta,np.abs(D),label="J1B*Y1BR_prime")

        # # # plt.axhline(y=0,xmin=beta[0],xmax=beta[-1],color='k')
        # # # plt.axhline(y=0,xmin=np.log10(beta[0]),xmax=np.log10(beta[-1]),color='k')

        # # # plt.ylim([-10,10])

        # # # plt.legend()

        # plt.show()

if __name__ == "__main__":

    unittest.main()
