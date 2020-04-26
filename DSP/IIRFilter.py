class IIRFilter(object):
    def __init__(self, coeffs):
        self.yM0_coeffs = []
        self.yM1_coeffs = []
        self.yM2_coeffs = []
        self.xM0_coeffs = []
        self.xM1_coeffs = []
        self.xM2_coeffs = []
        self.coeffs = coeffs

    def reset(self):
        """
        Reset the internal state of the filter.
        :return: None.
        """
        self.yM0_coeffs = []
        self.yM1_coeffs = []
        self.yM2_coeffs = []
        self.xM0_coeffs = []
        self.xM1_coeffs = []
        self.xM2_coeffs = []

    def filter(self, x):
        """
        Look, don't worry about it. I don't remember why this works the way it does.
        This is an iterative implementation of the recursive method for applying an IIR filter
        through a second-order system cascade.
        :param x: Signal to be filtered.
        :return: Filtered signal.
        """

        coeffs = self.coeffs
        for i in range(len(coeffs)):
            g = coeffs[i][0]
            a = coeffs[i][1]
            b = coeffs[i][2]

            if i >= len(self.yM1_coeffs):
                self.yM0_coeffs.append(0.0)
                self.yM1_coeffs.append(0.0)
                self.yM2_coeffs.append(0.0)
                self.xM0_coeffs.append(0.0)
                self.xM1_coeffs.append(0.0)
                self.xM2_coeffs.append(0.0)

            xM0 = self.xM0_coeffs[i]
            xM1 = self.xM1_coeffs[i]

            yM0 = self.yM0_coeffs[i]
            yM1 = self.yM1_coeffs[i]

            yM2 = yM1
            yM1 = yM0
            xM2 = xM1
            xM1 = xM0
            xM0 = g*x

            yv = -a[2] * yM2 - a[1] * yM1 + b[2] * xM2 + b[1] * xM1 + b[0] * xM0
            yM0 = yv
            x = yv

            self.xM0_coeffs[i] = xM0
            self.xM1_coeffs[i] = xM1
            self.xM2_coeffs[i] = xM2
            self.yM0_coeffs[i] = yM0
            self.yM1_coeffs[i] = yM1
            self.yM2_coeffs[i] = yM2

        return x