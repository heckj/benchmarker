""" utility methods for benchmarking """
import math

def calculate_results(measurements):
    """Take a list of measurements and calculate results from it.
    Results:
    (minimum, mean, maximum, std. deviation, median, 90th percentile)
    This whole segment borrowed from
    http://www.testing-software.org/Tools/timeit/
    """

    def calculate_std(measurements, mean):
        # calculate the standard deviation
        std = 0
        for i in measurements:
            std = std + (i - mean)**2
        return math.sqrt(std/ float(len(measurements)))
    def calculate_percentile(m_sorted, percentile):
        # This function calculates the linear interpolation between
        # the two closest ranks (p(k) <= p <= pk+1).
        if not m_sorted:
            return None
        m_sorted.sort()
        if percentile < 0.0:
            return m_sorted[0]
        elif percentile > 1.0:
            return m_sorted[-1]
        k = (len(m_sorted)-1) * percentile
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return m_sorted[int(f)]
        return m_sorted[int(f)] + (m_sorted[int(c)] -
            m_sorted[int(f)])*(k-f)

    # sort the measurements
    measurements.sort()

    # calculate the results
    minimum = measurements[0]
    mean = sum(measurements)/ float(len(measurements))
    maximum = measurements[-1]
    std = calculate_std(measurements, mean)
    median = calculate_percentile(measurements, 0.5)
    p90 = calculate_percentile(measurements, 0.9)
    return minimum, mean, maximum, std, median, p90
