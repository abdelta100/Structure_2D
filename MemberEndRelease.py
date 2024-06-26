class MemberEndRelease2D:
    def __init__(
            self,
            Fxi: float = 1,
            Fyi: float = 1,
            Mxyi: float = 1,
            Fxj: float = 1,
            Fyj: float = 1,
            Mxyj: float = 1):
        """
        A 2D Member End Release Class. Holds values of allowed releases on each node of a 2D element.
        X and Y Forces, and XY Moment in 2D, with respect to an arbitrary XY Plane.
        1 is fixed, 0 is released
        :rtype: MemberEndRelease2D
        :param Fxi: Force release in x-direction at i-node
        :param Fyi: Force release in y-direction at i-node
        :param Mxyi: Moment release in xy-plane at i-node
        :param Fxj: Force release in x-direction at j-node
        :param Fyj: Force release in y-direction at j-node
        :param Mxyj: Moment release in xy-plane at j-node
        """
        self._Fxi = Fxi
        self._Fyi = Fyi
        self._Mxyi = Mxyi
        self._Fxj = Fxj
        self._Fyj = Fyj
        self._Mxyj = Mxyj

    def tolist(self):
        return [self.fx1, self.fy1, self.mxy1, self.fx2, self.fy2, self.mxy2]

    def iNodeRelease(self):
        return [self.fx1, self.fy1, self.mxy1]

    def jNodeRelease(self):
        return [self.fx2, self.fy2, self.mxy2]

    @staticmethod
    def init_from_array(releaseList: list[int]):
        for i in releaseList:
            if i < 0 or i > 1 or type(i) is not int:
                ValueError("Entries of release list should be either 0 or 1")

        release = MemberEndRelease2D(
            Fxi=releaseList[0],
            Fyi=releaseList[1],
            Mxyi=releaseList[2],
            Fxj=releaseList[3],
            Fyj=releaseList[4],
            Mxyj=releaseList[5])

        return release

    @property
    def fx1(self):
        return self._Fxi

    @fx1.setter
    def fx1(self, Fx1):
        self._Fxi = Fx1

    @property
    def fy1(self):
        return self._Fyi

    @fy1.setter
    def fy1(self, Fy1):
        self._Fyi = Fy1

    @property
    def mxy1(self):
        return self._Mxyi

    @mxy1.setter
    def mxy1(self, Mxy1):
        self._Mxyi = Mxy1

    @property
    def fx2(self):
        return self._Fxj

    @fx2.setter
    def fx2(self, Fx2):
        self._Fxj = Fx2

    @property
    def fy2(self):
        return self._Fyj

    @fy2.setter
    def fy2(self, Fy2):
        self._Fyj = Fy2

    @property
    def mxy2(self):
        return self._Mxyj

    @mxy2.setter
    def mxy2(self, Mxy2):
        self._Mxyj = Mxy2


class FixedEndMember(MemberEndRelease2D):
    def __init__(self):
        """
        A 2D Member End Release Class, where all releases are fixed, NOT free.
        :rtype: FixedEndMember
        """
        super().__init__()


class PinnedEndMember(MemberEndRelease2D):
    def __init__(self):
        super().__init__()
        self.mxy1 = 0
        self.mxy2 = 0
