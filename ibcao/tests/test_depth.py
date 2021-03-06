# encoding: utf-8
import common
from common import outdir
import logging as ll
import unittest as ut

from ibcao  import *
import cartopy.crs as ccrs

import matplotlib
import matplotlib.pyplot as plt

import os
import os.path

class IbcaoDepthTest (ut.TestCase):
  def setUp (self):
    self.i = IBCAO ()

  def tearDown (self):
    self.i.close ()
    del self.i

  def get_lon_lat (self, nlat = 100, nlon = 100):
    lat = np.linspace (60, 90, nlat)
    lon = np.linspace (-180, 180, nlon)

    lat, lon = np.meshgrid (lat, lon)
    lat = lat.ravel ()
    lon = lon.ravel ()

    return (lon, lat)


  def test_depths (self):
    ll.info ('calculating depth profile')
    # make a profile

    lon, lat = self.get_lon_lat ()

    xy  = self.i.projection.transform_points (ccrs.Geodetic (), lon, lat)

    d = self.i.interp_depth (xy[:,0], xy[:,1])
    ll.info ('d=')
    ll.info (d.shape)

    plt.figure ()
    plt.plot (lat, d)
    plt.title ('depth along')
    plt.xlabel ('Latitude')
    plt.savefig (os.path.join(outdir, 'depth.png'))

  def test_known_positions (self):
    ll.info ('testing depth on a few known positions')

    g = ccrs.Geodetic ()

    def check_pos (lon, lat, depth, _atol = 0.1, _rtol = 1e-7):
      xy = self.i.projection.transform_point(lon, lat, g)

      d = self.i.interp_depth (np.array([xy[0]]), np.array([xy[1]]))
      z = self.i.map_depth (np.array([xy[0]]), np.array([xy[1]]))

      np.testing.assert_allclose (d, depth, atol = _atol, rtol = _rtol)
      np.testing.assert_allclose (z, depth, atol = _atol, rtol = _rtol)


    # north pole
    check_pos (0, 90, -4261, 50)

    # longyearbyen
    check_pos (15.651140, 78.222665, 1.7, 7)

    # highest mountain on greenland (Gunnbjørn Fjeld)
    check_pos (-29.898533, 68.9195, 3694, 400)

  def test_against_great_circle_and_gmt (self):
    ll.info ('testing depth against gmt extracted depths')
    gmt = np.array ([
        -0.648317,81.9962170001,-2574.32325995,
        -1.253283,81.9983000001,-2304.80896863,
        -1.856417,81.9994330001,-1992.40861882,
        -2.396967,81.9947830001,-2540.36409855,
        -3.130133,81.9987830001,-3509.64727122,
        -3.707333,81.9998670001,-4018.8108823,
        -4.296033,81.997083,-4011.25898682,
        -4.920717,81.9994000001,-3525.6963024,
        -5.50345000001,82.0028670001,-3023.12097893,
        -6.130917,82.0015830001,-3006.31591506,
        -6.69468300003,81.9966170001,-3190.38107675,
        -7.31206699999,81.9941330001,-3115.38103425,
        -7.93959999997,82.000267,-2982.875422,
        -8.19741700001,81.9721330001,-2911.32670751,
        -0.62855,81.9993830001,-2589.30052845,
        -0.051117,81.999717,-2822.43058789,
        0.56,82,-3006.25619309,
        1.705833,81.9945,-3435.51613899,
        2.310417,82.0015,-2030.92420387,
        2.89165,81.9971670001,-1309.44942805,
        3.48035,81.996817,-1136.05331727,
        4.093633,81.99945,-1098.94253697,
        4.6825,81.998917,-1275.39851465,
        5.290717,81.998917,-1345.6958582,
        5.878783,82.000133,-989.180725733,
        6.76653300003,82.0143830001,-796.276219227,
        7.07896700002,82.00315,-777.077539801,
      ])

    gmt = gmt.reshape (27, 3)

    gmtz = gmt[:,2]
    lon = gmt[:,0]
    lat = gmt[:,1]

    xy = self.i.projection.transform_points (ccrs.Geodetic (), lon, lat)
    dz = self.i.interp_depth (xy[:,0], xy[:,1])
    mz = self.i.map_depth (xy[:,0], xy[:,1])

    plt.figure ()
    plt.plot (lon, mz, label = 'map_depth')
    plt.plot (lon, dz, label = 'interp_depth')
    plt.plot (lon, gmtz, label = 'gmt')
    plt.legend ()
    plt.title ('depth')
    plt.xlabel ('Longitude')
    plt.savefig (os.path.join (outdir, 'depth_vs_gmt.png'))

    # high atol = 22 needed for python 3.4
    np.testing.assert_allclose (gmtz, dz, atol = 22)
    np.testing.assert_allclose (gmtz, mz, atol = 22)
