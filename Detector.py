import numpy as np
from pyFAI import detectors
from pyFAI.detectors import Pilatus300kw, Pilatus1M


class Pilatus1M_SMI(Pilatus1M):
    '''
    Pilatus 1M class inherited from the pyFAI Pilatus1M class
    This class is used to add a specific masking for the Pilatus 1M of SMI beamline at BNL
    '''

    def calc_mask(self, bs=None, bs_kind=None, optional_mask=None):
        '''
        :param bs: (string) This is the beamstop position on teh detctor (teh pixels behind will be mask inherently)
        :param bs_kind: (string) What beamstop is in: Only need to be defined if pindiode which have a different shape)
        :param optional_mask: (string) This is usefull for tender x-ray energy and will add extra max at the chips junction
        :return: (a 2D array) A mask array with 0 and 1 with 0s where the image will be masked
        '''
        mask = np.logical_not(detectors.Pilatus1M().calc_mask())
        mask[:, :5], mask[:, -5:], mask[:5, :], mask[-5:, :] = False, False, False, False

        #Hot pixels
        mask[20, 884], mask[56, 754], mask[111, 620], mask[145, 733], mask[178, 528], mask[
            189, 571] = False, False, False, False, False, False
        mask[372, 462], mask[454, 739], mask[657, 947], mask[869, 544], mask[870, 546], mask[
            870, 547] = False, False, False, False, False, False
        mask[870, 544], mask[871, 545], mask[871, 546], mask[871, 547] = False, False, False, False

        #For tender x-rays
        if optional_mask == 'tender':
            i = 60
            while i < np.shape(mask)[0]:
                if 480 < i < 530:
                    i = 554
                mask[:, i - 2: i + 2] = False
                i += 61

            j = 97
            while j < np.shape(mask)[0]:
                if 150 < j < 250:
                    j = 310
                elif 380 < j < 420:
                    j = 520
                elif 600 < j < 700:
                    j = 734
                elif 790 < j < 890:
                    j = 945
                mask[j - 2: j + 2, :] = False
                j += 100

        #Beamstop
        if bs == [0, 0]:
            return np.logical_not(mask)
        else:
            mask[bs[1]:, bs[0] - 11:bs[0] + 11] = False
            if bs_kind == 'pindiode': mask[bs[1]:bs[1] + 40, bs[0] - 22:bs[0] + 22] = False
            return np.logical_not(mask)


class VerticalPilatus300kw(Pilatus300kw):
    '''
    VerticalPilatus300kw class inherited from the pyFAI Pilatus300kw class but rotated by 90 deg to fit the position of the WAXS detector at SMI
    This class is used to add a specific masking for the Pilatus 300KW of SMI beamline at BNL
    '''

    MAX_SHAPE = (1475, 195)
    MODULE_SIZE = (487, 195)
    MODULE_GAP = (7, 17)
    aliases = ["Pilatus 300kw (Vertical)"]

    def calc_mask(self, bs, bs_kind=None, optional_mask=None):
        '''
        :param bs: (string) This is the beamstop position on teh detctor (teh pixels behind will be mask inherently)
        :param bs_kind: (string) Not used for now but can be used if different beamstop are used
        :param optional_mask: (string) This is usefull for tender x-ray energy and will add extra max at the chips junction
        :return: (a 2D array) A mask array with 0 and 1 with 0s where the image will be masked
        '''
        mask = np.rot90(np.logical_not(detectors.Pilatus300kw().calc_mask()), 1)

        #border of the detector and chips
        mask[:, :5], mask[:, -5:], mask[:5, :], mask[-5:, :] = False, False, False, False
        mask[486, :], mask[494, :], mask[980, :], mask[988, :]= False, False, False, False

        #Dead pixel
        dead_pix_x = [1386, 1387, 1386, 1387, 228, 307, 733, 733, 792, 1211, 1211, 1231, 1232, 1276, 1321, 1366, 1405, 1467, 1355, 1371, 1356]
        dead_pix_y = [96, 96, 97, 97, 21, 67, 170, 171, 37, 109, 110, 74, 74, 57, 81, 181, 46, 188, 84, 88, 105]
        for d_x, d_y in zip(dead_pix_x, dead_pix_y):
            mask[d_x, d_y] = False

        #Hot pixels
        mask[1314, 81] = False
        mask[732, 7], mask[732, 8], mask[733, 8], mask[733, 7], mask[733, 9] = False, False, False, False, False
        mask[1314, 82], mask[1315, 81] = False, False

        mask[674, 133], mask[674, 134], mask[1130, 20], mask[1239, 50] = False, False, False, False

        # For tender x-rays
        if optional_mask == 'tender':
            mask[:, 92:102] = False
            i = 59
            while i < np.shape(mask)[0]:
                if 450 < i < 550:
                    i = 553
                elif 970 < i < 1000:
                    i = 1047
                mask[1475 - i - 6:1475 - i, :] = False
                i += 61

        #Beamstop
        if bs == [0, 0]:
            return np.logical_not(mask)
        else:
            mask[bs[1]:, bs[0] - 8 : bs[0] + 8] = False
            return np.logical_not(mask)


# TODO: define rayonix class

from pyFAI.detectors._common import Detector

class rayonix(Detector):
    """
    Rayonix detector: generic description containing mask algorithm

    Nota: 1920x1920 pixels, 0.109mm pixel size
    """

    def __init__(self, pixel1=109e-6, pixel2=109e-6, max_shape=None):
        Detector.__init__(self, pixel1=pixel1, pixel2=pixel2, max_shape=max_shape)

    def __repr__(self):
        return "Detector %s\t PixelSize= %.3e, %.3e m" % \
               (self.name, self._pixel1, self._pixel2)


class Rayonix(rayonix):
    MAX_SHAPE = (1920, 1920)
    aliases = ["rayonix"]

    def calc_mask(self, bs, bs_kind=None, img=None, threshold=15):
        if img is None:
            mask = True
        else:
            mask = np.ones_like(img, dtype=bool)
            mask[:, :5], mask[:, -5:], mask[:5, :], mask[-5:, :] = False, False, False, False
            mask[np.where(img < threshold)] = False

        return np.logical_not(mask)
