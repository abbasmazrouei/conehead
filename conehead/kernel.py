# kernel.py
#
# Energy deposition kernel data for varian 6MV source created with EDKnrc.
#
# Simulation details:
#
# Histories - 20000000
# Num cones - 48
# Angles - 3.75 degree spacing
# Num spheres - 24
# Medium - H20521ICRU
# ECUT - 0.521
# PCUT - 0.010
#
import numpy as np



class KernelMono:

    def __init__(self, egslst_path=None) -> None:
        if egslst_path is not None:
            self._from_egslst(egslst_path)
        else:
            raise NotImplementedError

    def _from_egslst(self, egslst_path: str):
        with open(egslst_path) as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "KINETIC ENERGY OF THE INCIDENT BEAM:" in line:
                    self.energy = float(line.split()[-2])
                if "angle/deg.  radius/cm" in line:
                    start = i + 2
                if "END OF RUN" in line:
                    end = i - 1

            data_raw = np.array(
                [l.split()[:3] for l in lines[start:end]], dtype=np.float32
            )
            self.angles = np.unique(data_raw[:, 0])
            self.radii = np.unique(data_raw[:, 1])
            self.kernel_diff = data_raw[:, 2].reshape((48, 24))
            self.kernel_diff = self.kernel_diff / self.kernel_diff.sum()  # normalise
            self.kernel_cum = self.kernel_diff.cumsum(axis=1)
            kernel_cum_interp = np.zeros((48, 5996))
            for i in range(self.kernel_cum.shape[0]):
                kernel_cum_interp[i, :] = np.interp(  # Resample to 0.1 mm
                    np.linspace(0.05, 60.0, 5996),
                    self.radii,
                    self.kernel_cum[i, :]
                )
            self.kernel_cum = kernel_cum_interp



class KernelPoly:

    def __init__(self, angles, radii, kernel_diff) -> None:
        self.angles = angles
        self.radii = radii
        self.kernel_diff = kernel_diff
        self.kernel_diff = self.kernel_diff / self.kernel_diff.sum()  # normalise
        self.kernel_cum = kernel_diff.cumsum(axis=1)
        kernel_cum_interp = np.zeros((48, 5996))
        for i in range(self.kernel_cum.shape[0]):
            kernel_cum_interp[i, :] = np.interp(  # Resample to 0.1 mm
                np.linspace(0.05, 60.0, 5996),
                self.radii,
                self.kernel_cum[i, :]
            )
        self.kernel_cum = kernel_cum_interp






# settings = {
#     # 'stepSize': 0.1,  # Stepsize when raytracing effective depth (cm)
#     'sPri': 0.90924,  # Primary source strength
#     'sAnn': 2.887e-3,  # Annular source strength
#     'zAnn': 4.0,  # Distance of annular source from point source (cm)
#     'rInner': 0.2,  # Inner radius of annular source
#     'rOuter': 1.4,  # Outer radius of annular source
#     'zExp': 12.5,  # Distance of exponential source from point source (cm)
#     'sExp': 8.289e-3,  # Exponential source strength
#     'kExp': 0.4816,  # Exponential source exponent coefficient
#     'softRatio': 0.0025,  # cm^-1
#     'softLimit': 20,  # cm
#     'hornRatio': 0.0065,  # % per cm
#     'eLow': 0.01,  # MeV
#     'eHigh': 7.0,  # MeV
#     'eNum': 500,  # Spectrum samples
#     'fluenceResampling': 3,  # Split voxels for fluence calculation
#     'energy_weights': {  # Varian Clinac iX 6MV
#         "0.5": 0.08196,
#         "1.0": 0.12385,
#         "1.5": 0.10605,
#         "2.0": 0.08307,
#         "2.5": 0.05881,
#         "3.0": 0.03911,
#         "3.5": 0.02131,
#         "4.0": 0.02426,
#         "4.5": 0.0,
#         "5.0": 0.00881,
#         "5.5": 0.0,
#         "6.0": 0.00498,
#     }    
# }






# print("Building Polyenergetic Kernel...")
# kernels = {
#     "0.5": KernelMono("kernels/0.5MeV/0.5MeV.egslst"),
#     "1.0": KernelMono("kernels/1.5MeV/1.5MeV.egslst"),
#     "1.5": KernelMono("kernels/1.5MeV/1.5MeV.egslst"),
#     "2.0": KernelMono("kernels/2.0MeV/2.0MeV.egslst"),
#     "2.5": KernelMono("kernels/2.5MeV/2.5MeV.egslst"),
#     "3.0": KernelMono("kernels/3.0MeV/3.0MeV.egslst"),
#     "3.5": KernelMono("kernels/3.5MeV/3.5MeV.egslst"),
#     "4.0": KernelMono("kernels/4.0MeV/4.0MeV.egslst"),
#     "4.5": KernelMono("kernels/4.5MeV/4.5MeV.egslst"),
#     "5.0": KernelMono("kernels/5.0MeV/5.0MeV.egslst"),
#     "5.5": KernelMono("kernels/5.5MeV/5.5MeV.egslst"),
#     "6.0": KernelMono("kernels/6.0MeV/6.0MeV.egslst"),
# }
# kernel_diff = np.zeros_like(kernels["0.5"].kernel_diff)
# for e in settings['energy_weights'].keys():
#     kernel_diff += kernels[e].kernel_diff * settings['energy_weights'][e]
# kernel_diff = kernel_diff / kernel_diff.sum()  # normalise
# kernel_poly = KernelPoly(kernels["0.5"].angles, kernels["0.5"].radii, kernel_diff)

# import matplotlib.pyplot as plt
# plt.plot(np.linspace(0.05, 60.0, 5996), kernel_poly.kernel_cum[0, :], '.')
# plt.plot(np.linspace(0.05, 60.0, 5996), kernel_poly.kernel_cum[4, :], '.')
# plt.plot(np.linspace(0.05, 60.0, 5996), kernel_poly.kernel_cum[8, :], '.')
# plt.plot(np.linspace(0.05, 60.0, 5996), kernel_poly.kernel_cum[12, :], '.')
# plt.plot(np.linspace(0.05, 60.0, 5996), kernel_poly.kernel_cum[16, :], '.')
# plt.plot(np.linspace(0.05, 60.0, 5996), kernel_poly.kernel_cum[30, :], '.')
# plt.plot(np.linspace(0.05, 60.0, 5996), kernel_poly.kernel_cum[47, :], '.')
# plt.show()
















# class PolyenergeticKernel:

#     def __init__(self):
#         # Differential kernel data
#         differential = {}
#         differential["radii"] = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 60.0]  # noqa: E501
#         differential["180.00"] = [3.1716E-04, 2.5264E-04, 2.1302E-04, 1.8333E-04, 3.0595E-04, 2.4602E-04, 1.9975E-04, 1.6384E-04, 2.5529E-04, 1.7490E-04, 2.3665E-04, 8.6741E-05, 5.5999E-05, 4.5275E-05, 4.1749E-05, 4.0469E-05, 8.0128E-05, 8.0949E-05, 1.9521E-04, 1.7018E-04, 2.8309E-04, 2.2974E-04, 1.7404E-04, 1.2039E-04]  # noqa: E501
#         differential["176.25"] = [7.2165E-04, 6.3060E-04, 5.5289E-04, 4.8706E-04, 8.2215E-04, 6.6658E-04, 5.5138E-04, 4.6444E-04, 7.2564E-04, 5.0608E-04, 6.9715E-04, 2.3333E-04, 1.4331E-04, 1.1612E-04, 1.1245E-04, 1.1293E-04, 2.2100E-04, 2.2231E-04, 5.3458E-04, 4.7877E-04, 8.1573E-04, 6.2310E-04, 4.6339E-04, 3.2844E-04]  # noqa: E501
#         differential["172.50"] = [8.4685E-04, 7.9086E-04, 7.2081E-04, 6.5611E-04, 1.1427E-03, 9.5434E-04, 8.0386E-04, 6.8647E-04, 1.0887E-03, 7.8219E-04, 1.0742E-03, 3.6535E-04, 2.1252E-04, 1.7489E-04, 1.7220E-04, 1.7387E-04, 3.3594E-04, 3.3092E-04, 7.6439E-04, 6.9551E-04, 1.1541E-03, 9.1071E-04, 6.7804E-04, 4.8089E-04]  # noqa: E501
#         differential["168.75"] = [8.4584E-04, 8.1946E-04, 7.6561E-04, 7.1448E-04, 1.2802E-03, 1.1070E-03, 9.5402E-04, 8.2517E-04, 1.3376E-03, 9.7297E-04, 1.3463E-03, 4.5901E-04, 2.6123E-04, 2.0943E-04, 2.1519E-04, 2.0986E-04, 4.0380E-04, 3.8816E-04, 9.3038E-04, 8.3548E-04, 1.3945E-03, 1.0967E-03, 8.2102E-04, 5.6321E-04]  # noqa: E501
#         differential["165.00"] = [8.0639E-04, 7.8837E-04, 7.4898E-04, 7.0527E-04, 1.2883E-03, 1.1396E-03, 1.0066E-03, 8.8100E-04, 1.4377E-03, 1.0692E-03, 1.4940E-03, 5.1991E-04, 2.9443E-04, 2.3323E-04, 2.2870E-04, 2.2541E-04, 4.3784E-04, 4.2120E-04, 9.8409E-04, 8.9360E-04, 1.5153E-03, 1.1751E-03, 8.7806E-04, 6.1513E-04]  # noqa: E501
#         differential["161.25"] = [7.6179E-04, 7.3486E-04, 6.9465E-04, 6.6212E-04, 1.2289E-03, 1.1034E-03, 9.8904E-04, 8.8066E-04, 1.4649E-03, 1.0981E-03, 1.5662E-03, 5.3722E-04, 2.9804E-04, 2.3786E-04, 2.3426E-04, 2.2963E-04, 4.4411E-04, 4.1852E-04, 9.9531E-04, 9.1262E-04, 1.5531E-03, 1.1884E-03, 8.8075E-04, 5.9886E-04]  # noqa: E501
#         differential["157.50"] = [7.1818E-04, 6.7447E-04, 6.3802E-04, 6.0651E-04, 1.1303E-03, 1.0312E-03, 9.3643E-04, 8.3233E-04, 1.3953E-03, 1.0662E-03, 1.5193E-03, 5.1621E-04, 2.9557E-04, 2.2723E-04, 2.2446E-04, 2.1688E-04, 4.2738E-04, 4.2076E-04, 9.7855E-04, 8.9418E-04, 1.5244E-03, 1.1698E-03, 8.5538E-04, 5.7492E-04]  # noqa: E501
#         differential["153.75"] = [6.7658E-04, 6.1540E-04, 5.7532E-04, 5.4720E-04, 1.0200E-03, 9.2992E-04, 8.4690E-04, 7.6627E-04, 1.3054E-03, 1.0005E-03, 1.4111E-03, 4.8297E-04, 2.7556E-04, 2.1500E-04, 2.1181E-04, 2.1111E-04, 4.0428E-04, 4.0710E-04, 9.4993E-04, 8.6838E-04, 1.4739E-03, 1.1324E-03, 8.2091E-04, 5.3919E-04]  # noqa: E501
#         differential["150.00"] = [6.3405E-04, 5.5391E-04, 5.1345E-04, 4.8458E-04, 9.1052E-04, 8.3040E-04, 7.5965E-04, 6.9305E-04, 1.1716E-03, 9.0157E-04, 1.2540E-03, 4.3450E-04, 2.4990E-04, 2.0210E-04, 1.9757E-04, 1.9522E-04, 3.8828E-04, 3.7953E-04, 8.9903E-04, 8.2638E-04, 1.4203E-03, 1.0746E-03, 7.7758E-04, 4.9989E-04]  # noqa: E501
#         differential["146.25"] = [5.9239E-04, 4.9818E-04, 4.5722E-04, 4.3104E-04, 8.0957E-04, 7.3495E-04, 6.7005E-04, 6.0908E-04, 1.0264E-03, 7.8272E-04, 1.0847E-03, 3.7920E-04, 2.2103E-04, 1.8665E-04, 1.8743E-04, 1.8437E-04, 3.6438E-04, 3.5427E-04, 8.5345E-04, 7.9466E-04, 1.3560E-03, 1.0289E-03, 7.2738E-04, 4.5573E-04]  # noqa: E501
#         differential["142.50"] = [5.4884E-04, 4.4403E-04, 4.0454E-04, 3.8118E-04, 7.0872E-04, 6.4063E-04, 5.8139E-04, 5.2776E-04, 8.8941E-04, 6.7246E-04, 9.1427E-04, 3.0503E-04, 2.0246E-04, 1.7411E-04, 1.7282E-04, 1.6942E-04, 3.4169E-04, 3.3300E-04, 8.0558E-04, 7.5282E-04, 1.2828E-03, 9.5956E-04, 6.7840E-04, 4.1800E-04]  # noqa: E501
#         differential["138.75"] = [5.0387E-04, 3.9403E-04, 3.5620E-04, 3.3441E-04, 6.1678E-04, 5.5673E-04, 5.0291E-04, 4.5181E-04, 7.5055E-04, 5.6018E-04, 7.4490E-04, 2.4504E-04, 1.8335E-04, 1.5971E-04, 1.5794E-04, 1.5723E-04, 3.1436E-04, 3.1037E-04, 7.6244E-04, 7.1723E-04, 1.2162E-03, 9.0495E-04, 6.2809E-04, 3.7932E-04]  # noqa: E501
#         differential["135.00"] = [4.5929E-04, 3.4622E-04, 3.1165E-04, 2.9223E-04, 5.3502E-04, 4.7394E-04, 4.3083E-04, 3.8076E-04, 6.2776E-04, 4.6466E-04, 6.0328E-04, 1.9721E-04, 1.5906E-04, 1.4507E-04, 1.4877E-04, 1.4736E-04, 2.9644E-04, 2.9500E-04, 7.2121E-04, 6.7684E-04, 1.1486E-03, 8.4828E-04, 5.7979E-04, 3.4414E-04]  # noqa: E501
#         differential["131.25"] = [4.1570E-04, 3.0430E-04, 2.7254E-04, 2.5212E-04, 4.5951E-04, 4.0316E-04, 3.5740E-04, 3.1780E-04, 5.1491E-04, 3.7487E-04, 4.8182E-04, 1.5421E-04, 1.4502E-04, 1.3598E-04, 1.3664E-04, 1.3784E-04, 2.7512E-04, 2.7719E-04, 6.7961E-04, 6.3643E-04, 1.0783E-03, 7.9408E-04, 5.3400E-04, 3.1229E-04]  # noqa: E501
#         differential["127.50"] = [3.7222E-04, 2.6613E-04, 2.3706E-04, 2.1814E-04, 3.9330E-04, 3.4399E-04, 2.9867E-04, 2.5998E-04, 4.1839E-04, 3.0357E-04, 3.8412E-04, 1.2583E-04, 1.3008E-04, 1.2540E-04, 1.2670E-04, 1.2804E-04, 2.5806E-04, 2.5730E-04, 6.3958E-04, 5.9929E-04, 1.0205E-03, 7.4628E-04, 4.9456E-04, 2.8071E-04]  # noqa: E501
#         differential["123.75"] = [3.2926E-04, 2.3076E-04, 2.0436E-04, 1.8552E-04, 3.3393E-04, 2.8693E-04, 2.4707E-04, 2.0931E-04, 3.3541E-04, 2.4016E-04, 2.9392E-04, 1.0056E-04, 1.1919E-04, 1.1830E-04, 1.1838E-04, 1.1972E-04, 2.4157E-04, 2.4598E-04, 6.0117E-04, 5.7378E-04, 9.6782E-04, 6.9766E-04, 4.5383E-04, 2.5212E-04]  # noqa: E501
#         differential["120.00"] = [2.0018E-04, 2.9021E-04, 1.7512E-04, 1.5780E-04, 2.8435E-04, 2.3883E-04, 2.0341E-04, 1.7182E-04, 2.6805E-04, 1.8426E-04, 2.3122E-04, 8.1548E-05, 1.1032E-04, 1.0954E-04, 1.1115E-04, 1.1201E-04, 2.2623E-04, 2.3039E-04, 5.7168E-04, 5.3930E-04, 9.1368E-04, 6.4999E-04, 4.2181E-04, 2.3166E-04]  # noqa: E501
#         differential["116.25"] = [2.5407E-04, 1.7267E-04, 1.5079E-04, 1.3576E-04, 2.3662E-04, 1.9939E-04, 1.6703E-04, 1.3930E-04, 2.1094E-04, 1.4436E-04, 1.7130E-04, 6.8033E-05, 1.0214E-04, 1.0262E-04, 1.0264E-04, 1.0455E-04, 2.1294E-04, 2.1726E-04, 5.4212E-04, 5.1589E-04, 8.5933E-04, 6.0752E-04, 3.9103E-04, 2.0807E-04]  # noqa: E501
#         differential["112.50"] = [2.2059E-04, 1.4787E-04, 1.2686E-04, 1.1332E-04, 1.9461E-04, 1.6058E-04, 1.3490E-04, 1.1259E-04, 1.6921E-04, 1.1107E-04, 1.3146E-04, 5.8540E-05, 9.3765E-05, 9.4428E-05, 9.6542E-05, 9.8591E-05, 2.0026E-04, 2.0492E-04, 5.1171E-04, 4.8802E-04, 8.1772E-04, 5.7003E-04, 3.5869E-04, 1.8877E-04]  # noqa: E501
#         differential["108.75"] = [1.9068E-04, 1.2671E-04, 1.0692E-04, 9.5358E-05, 1.6284E-04, 1.3076E-04, 1.0793E-04, 8.9688E-05, 1.3566E-04, 8.4571E-05, 1.0335E-04, 5.1427E-05, 8.6782E-05, 8.8733E-05, 8.9266E-05, 9.1932E-05, 1.8887E-04, 1.9310E-04, 4.8552E-04, 4.6205E-04, 7.7340E-04, 5.3642E-04, 3.3040E-04, 1.7148E-04]  # noqa: E501
#         differential["105.00"] = [1.6454E-04, 1.0750E-04, 9.0399E-05, 8.0101E-05, 1.3355E-04, 1.0612E-04, 8.5501E-05, 6.9826E-05, 1.0295E-04, 6.5236E-05, 8.4861E-05, 4.7840E-05, 8.1719E-05, 8.1954E-05, 8.5154E-05, 8.7281E-05, 1.7831E-04, 1.8316E-04, 4.6377E-04, 4.3929E-04, 7.2843E-04, 5.0080E-04, 3.0646E-04, 1.5546E-04]  # noqa: E501
#         differential["101.25"] = [1.4141E-04, 9.0846E-05, 7.5437E-05, 6.6187E-05, 1.0826E-04, 8.4390E-05, 6.6536E-05, 5.4533E-05, 7.5954E-05, 5.1385E-05, 6.7181E-05, 4.1454E-05, 7.4861E-05, 7.7795E-05, 8.0611E-05, 8.3181E-05, 1.6964E-04, 1.7533E-04, 4.4043E-04, 4.1737E-04, 6.9278E-04, 4.7027E-04, 2.8141E-04, 1.4110E-04]  # noqa: E501
#         differential["97.50"] = [1.2026E-04, 7.6143E-05, 6.3061E-05, 5.3343E-05, 8.7541E-05, 6.7819E-05, 5.3238E-05, 4.2576E-05, 6.0480E-05, 3.9709E-05, 5.7370E-05, 3.7398E-05, 7.1143E-05, 7.2476E-05, 7.5547E-05, 7.6621E-05, 1.6069E-04, 1.6521E-04, 4.1804E-04, 3.9911E-04, 6.5362E-04, 4.3854E-04, 2.6233E-04, 1.2992E-04]  # noqa: E501
#         differential["93.75"] = [1.0050E-04, 6.3714E-05, 5.2265E-05, 4.3544E-05, 7.0593E-05, 5.4596E-05, 4.2572E-05, 3.3573E-05, 5.0281E-05, 3.1304E-05, 4.8468E-05, 3.4627E-05, 6.5352E-05, 6.9441E-05, 7.0732E-05, 7.3136E-05, 1.5149E-04, 1.5638E-04, 3.9784E-04, 3.7766E-04, 6.1687E-04, 4.1271E-04, 2.4115E-04, 1.1695E-04]  # noqa: E501
#         differential["90.00"] = [8.4523E-05, 5.3150E-05, 4.3112E-05, 3.5893E-05, 5.7140E-05, 4.3473E-05, 3.3943E-05, 2.7218E-05, 3.8688E-05, 2.7291E-05, 4.2161E-05, 3.1897E-05, 6.1242E-05, 6.4256E-05, 6.6531E-05, 6.9268E-05, 1.4449E-04, 1.4947E-04, 3.7704E-04, 3.5858E-04, 5.8342E-04, 3.8301E-04, 2.2395E-04, 1.0777E-04]  # noqa: E501
#         differential["86.25"] = [7.1524E-05, 4.3973E-05, 3.5190E-05, 2.8362E-05, 4.6338E-05, 3.5676E-05, 2.6989E-05, 2.2356E-05, 3.2092E-05, 2.4890E-05, 3.6172E-05, 2.8842E-05, 5.7259E-05, 6.0585E-05, 6.3205E-05, 6.6234E-05, 1.3634E-04, 1.4060E-04, 3.5742E-04, 3.4096E-04, 5.5175E-04, 3.5949E-04, 2.0605E-04, 9.7662E-05]  # noqa: E501
#         differential["82.50"] = [6.0198E-05, 3.6437E-05, 2.8418E-05, 2.3047E-05, 3.7237E-05, 2.8207E-05, 2.1189E-05, 1.7914E-05, 2.6353E-05, 1.8248E-05, 3.1345E-05, 2.6860E-05, 5.4125E-05, 5.6886E-05, 5.9153E-05, 6.2602E-05, 1.2761E-04, 1.3324E-04, 3.4173E-04, 3.2211E-04, 5.2076E-04, 3.3710E-04, 1.9070E-04, 8.9070E-05]  # noqa: E501
#         differential["78.75"] = [5.0571E-05, 2.9960E-05, 2.3074E-05, 1.8660E-05, 2.9868E-05, 2.2872E-05, 1.7032E-05, 1.5122E-05, 2.1415E-05, 1.5426E-05, 2.7954E-05, 2.4902E-05, 5.0585E-05, 5.3388E-05, 5.5320E-05, 5.7658E-05, 1.2154E-04, 1.2679E-04, 3.2238E-04, 3.0421E-04, 4.8897E-04, 3.1349E-04, 1.7532E-04, 8.1466E-05]  # noqa: E501
#         differential["75.00"] = [4.2112E-05, 2.4868E-05, 1.9209E-05, 1.5771E-05, 2.4387E-05, 1.8370E-05, 1.4433E-05, 1.1372E-05, 1.8894E-05, 1.2702E-05, 2.6132E-05, 2.2908E-05, 4.7598E-05, 5.0406E-05, 5.2701E-05, 5.4958E-05, 1.1547E-04, 1.2008E-04, 3.0619E-04, 2.8934E-04, 4.6305E-04, 2.9374E-04, 1.6237E-04, 7.4364E-05]  # noqa: E501
#         differential["71.25"] = [3.5140E-05, 2.0106E-05, 1.5781E-05, 1.2674E-05, 1.9914E-05, 1.4716E-05, 1.2017E-05, 9.3152E-06, 1.5772E-05, 1.1428E-05, 2.3570E-05, 2.1059E-05, 4.4634E-05, 4.6299E-05, 4.9933E-05, 5.1585E-05, 1.0925E-04, 1.1250E-04, 2.9000E-04, 2.7223E-04, 4.3512E-04, 2.7371E-04, 1.4938E-04, 6.6982E-05]  # noqa: E501
#         differential["67.50"] = [2.9286E-05, 1.6452E-05, 1.2964E-05, 1.0114E-05, 1.5891E-05, 1.2147E-05, 1.0520E-05, 8.3620E-06, 1.2840E-05, 1.1288E-05, 2.1241E-05, 2.0213E-05, 4.1167E-05, 4.4238E-05, 4.6407E-05, 4.8614E-05, 1.0265E-04, 1.0686E-04, 2.7185E-04, 2.5662E-04, 4.0728E-04, 2.5477E-04, 1.3807E-04, 6.1209E-05]  # noqa: E501
#         differential["63.75"] = [2.4118E-05, 1.3769E-05, 1.0322E-05, 8.4989E-06, 1.3293E-05, 1.0001E-05, 8.3676E-06, 7.0608E-06, 1.1076E-05, 8.8150E-06, 1.9295E-05, 1.8468E-05, 3.8582E-05, 4.1889E-05, 4.3535E-05, 4.5996E-05, 9.4374E-05, 1.0044E-04, 2.5425E-04, 2.4127E-04, 3.8241E-04, 2.3690E-04, 1.2783E-04, 5.6103E-05]  # noqa: E501
#         differential["60.00"] = [1.9921E-05, 1.1152E-05, 8.7769E-06, 7.1134E-06, 1.1489E-05, 8.2340E-06, 7.1545E-06, 6.6486E-06, 9.7345E-06, 8.1614E-06, 1.7375E-05, 1.7143E-05, 3.6222E-05, 3.8469E-05, 4.1865E-05, 4.2909E-05, 9.0061E-05, 9.4438E-05, 2.3842E-04, 2.2529E-04, 3.5583E-04, 2.1954E-04, 1.1558E-04, 5.1538E-05]  # noqa: E501
#         differential["56.25"] = [1.6478E-05, 9.3111E-06, 7.1408E-06, 5.7957E-06, 9.3849E-06, 6.9035E-06, 6.1328E-06, 5.3341E-06, 8.8836E-06, 7.0220E-06, 1.6906E-05, 1.6119E-05, 3.3211E-05, 3.5654E-05, 3.7704E-05, 3.9604E-05, 8.4395E-05, 8.7387E-05, 2.2391E-04, 2.1084E-04, 3.2961E-04, 2.0237E-04, 1.0695E-04, 4.6271E-05]  # noqa: E501
#         differential["52.50"] = [1.3729E-05, 7.6613E-06, 5.8978E-06, 5.0069E-06, 7.9888E-06, 6.4184E-06, 5.3932E-06, 4.6443E-06, 8.1948E-06, 6.7958E-06, 1.5177E-05, 1.4775E-05, 3.1523E-05, 3.2805E-05, 3.4995E-05, 3.6855E-05, 7.8183E-05, 8.1048E-05, 2.0615E-04, 1.9582E-04, 3.0772E-04, 1.8553E-04, 9.8400E-05, 4.3035E-05]  # noqa: E501
#         differential["48.75"] = [1.1683E-05, 6.1489E-06, 4.6910E-06, 4.1438E-06, 7.0684E-06, 5.7430E-06, 4.8885E-06, 3.7239E-06, 7.0706E-06, 5.9175E-06, 1.3686E-05, 1.3864E-05, 2.9220E-05, 3.0304E-05, 3.2185E-05, 3.4739E-05, 7.1921E-05, 7.5360E-05, 1.9248E-04, 1.8069E-04, 2.8134E-04, 1.7080E-04, 8.9134E-05, 3.8131E-05]  # noqa: E501
#         differential["45.00"] = [9.6669E-06, 5.3314E-06, 4.0359E-06, 3.5299E-06, 5.6401E-06, 4.8351E-06, 3.8513E-06, 3.6767E-06, 6.4602E-06, 5.5178E-06, 1.2459E-05, 1.1834E-05, 2.6032E-05, 2.8431E-05, 2.9872E-05, 3.0974E-05, 6.6230E-05, 6.9055E-05, 1.7669E-04, 1.6689E-04, 2.6012E-04, 1.5618E-04, 8.0220E-05, 3.4567E-05]  # noqa: E501
#         differential["41.25"] = [8.1039E-06, 4.3802E-06, 3.3861E-06, 2.8837E-06, 4.6254E-06, 4.3044E-06, 3.0168E-06, 2.9967E-06, 5.2890E-06, 5.1153E-06, 1.0890E-05, 1.1139E-05, 2.4034E-05, 2.5572E-05, 2.6688E-05, 2.7943E-05, 6.0299E-05, 6.3059E-05, 1.6143E-04, 1.5127E-04, 2.3578E-04, 1.3992E-04, 7.2338E-05, 3.1372E-05]  # noqa: E501
#         differential["37.50"] = [6.6839E-06, 3.5194E-06, 2.7873E-06, 2.4502E-06, 3.8755E-06, 4.0265E-06, 2.9740E-06, 2.4874E-06, 4.5577E-06, 4.1924E-06, 1.0051E-05, 9.9657E-06, 2.1477E-05, 2.3384E-05, 2.4574E-05, 2.5795E-05, 5.4366E-05, 5.8139E-05, 1.4542E-04, 1.3774E-04, 2.1221E-04, 1.2609E-04, 6.4985E-05, 2.7197E-05]  # noqa: E501
#         differential["33.75"] = [5.4205E-06, 3.0132E-06, 2.2823E-06, 2.0303E-06, 3.4066E-06, 3.1506E-06, 2.4831E-06, 2.6402E-06, 4.0542E-06, 3.6739E-06, 8.5538E-06, 8.9198E-06, 1.9130E-05, 2.0660E-05, 2.1998E-05, 2.2942E-05, 4.9046E-05, 5.2065E-05, 1.3037E-04, 1.2230E-04, 1.8883E-04, 1.1259E-04, 5.7872E-05, 2.4007E-05]  # noqa: E501
#         differential["30.00"] = [4.4794E-06, 2.3208E-06, 1.9045E-06, 1.7752E-06, 2.7487E-06, 2.6283E-06, 2.2053E-06, 2.2446E-06, 3.3323E-06, 3.3947E-06, 7.6504E-06, 7.7172E-06, 1.6868E-05, 1.8606E-05, 1.9170E-05, 2.0488E-05, 4.3444E-05, 4.4756E-05, 1.1402E-04, 1.0756E-04, 1.6706E-04, 9.8860E-05, 5.0241E-05, 2.0998E-05]  # noqa: E501
#         differential["26.25"] = [3.6190E-06, 1.9781E-06, 1.5474E-06, 1.4782E-06, 2.5637E-06, 2.2222E-06, 1.8544E-06, 1.6636E-06, 2.8783E-06, 2.9583E-06, 6.6380E-06, 6.7006E-06, 1.4251E-05, 1.5777E-05, 1.6892E-05, 1.7315E-05, 3.7043E-05, 3.9403E-05, 1.0003E-04, 9.3364E-05, 1.4344E-04, 8.4999E-05, 4.3674E-05, 1.8103E-05]  # noqa: E501
#         differential["22.50"] = [2.8792E-06, 1.6257E-06, 1.3511E-06, 1.2484E-06, 2.0387E-06, 1.6028E-06, 1.5019E-06, 1.5448E-06, 2.4277E-06, 2.2792E-06, 5.4835E-06, 5.6299E-06, 1.2351E-05, 1.2781E-05, 1.3828E-05, 1.4799E-05, 3.1985E-05, 3.2963E-05, 8.3673E-05, 7.8273E-05, 1.2302E-04, 7.1391E-05, 3.6519E-05, 1.5241E-05]  # noqa: E501
#         differential["18.75"] = [2.2285E-06, 1.2837E-06, 1.0038E-06, 9.3018E-07, 1.4714E-06, 1.4703E-06, 1.2415E-06, 1.0601E-06, 2.1188E-06, 1.8897E-06, 4.6771E-06, 4.8616E-06, 1.0071E-05, 1.0745E-05, 1.1537E-05, 1.1880E-05, 2.5866E-05, 2.6522E-05, 6.9206E-05, 6.3770E-05, 9.9828E-05, 5.8104E-05, 2.9840E-05, 1.2388E-05]  # noqa: E501
#         differential["15.00"] = [1.6887E-06, 9.8109E-07, 7.5927E-07, 8.1086E-07, 1.1912E-06, 1.0432E-06, 1.0587E-06, 7.3229E-07, 1.4687E-06, 1.3897E-06, 3.8158E-06, 3.6272E-06, 7.7893E-06, 8.6792E-06, 8.7601E-06, 9.4267E-06, 2.0269E-05, 2.0877E-05, 5.3562E-05, 4.9758E-05, 7.7073E-05, 4.4854E-05, 2.2521E-05, 9.5734E-06]  # noqa: E501
#         differential["11.25"] = [1.2278E-06, 6.5707E-07, 5.5487E-07, 5.5538E-07, 8.1350E-07, 6.7887E-07, 6.0759E-07, 6.5650E-07, 1.1594E-06, 9.9556E-07, 2.5199E-06, 2.5024E-06, 5.4025E-06, 5.8759E-06, 6.5228E-06, 6.6626E-06, 1.4082E-05, 1.4625E-05, 3.8040E-05, 3.5522E-05, 5.4874E-05, 3.2601E-05, 1.6259E-05, 6.8731E-06]  # noqa: E501
#         differential["7.50"] = [6.9232E-07, 4.0662E-07, 3.5639E-07, 2.5825E-07, 4.8402E-07, 3.7525E-07, 3.4523E-07, 3.6394E-07, 7.2706E-07, 5.1378E-07, 1.6728E-06, 1.6227E-06, 3.3101E-06, 3.5233E-06, 3.9192E-06, 4.0388E-06, 8.5304E-06, 9.2223E-06, 2.2812E-05, 2.2137E-05, 3.2240E-05, 1.9541E-05, 9.8272E-06, 3.8354E-06]  # noqa: E501
#         differential["3.75"] = [2.4651E-07, 1.2914E-07, 9.1505E-08, 1.0763E-07, 1.8127E-07, 1.2452E-07, 1.2995E-07, 9.3706E-08, 2.4620E-07, 1.6966E-07, 5.1805E-07, 5.1261E-07, 1.1530E-06, 1.1284E-06, 1.4826E-06, 1.3001E-06, 2.8917E-06, 2.9277E-06, 7.6516E-06, 7.3830E-06, 1.1174E-05, 6.4535E-06, 3.0976E-06, 1.3647E-06]  # noqa: E501

#         # Normalise kernel data
#         f_total = 0.289622754141
#         for key in differential.keys():
#             if key != "radii":
#                 differential[key] = np.array(differential[key]) / f_total
#         self.differential = differential

#         # Calculate cumulative kernel data
#         cumulative = {}
#         cumulative["radii"] = differential["radii"]
#         for key in differential.keys():
#             if key != "radii":
#                 cumulative[key] = np.cumsum(differential[key])
#                 cumulative[key] = np.interp(  # Resample to 0.1 mm
#                     np.linspace(0.05, 60.0, 5996),
#                     cumulative["radii"],
#                     cumulative[key]
#                 )
#         self.cumulative = cumulative
