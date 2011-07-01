#!/usr/bin/env python
""" Benchmarking script to run celery benchmarks """

import math
import timeit
from benchmark.celerybench.tasks import add

def dumb_test_code():
    """ my little 'how the hell does this work anyway' testing code.
    Probably useless and should be deleted
    """
    print "add.delay(4, 4)"
    result = add.delay(4, 4)
    print "result.ready() is ",result.ready()
    print "result.get() ", result.get() #wait for the result
    print "result.successful() is ",result.successful()
    print "and the result is ", result.result
    print "delivery_mode is ",add.delivery_mode

    print "delivery_mode is ",add.delivery_mode
    print "add.apply_async(args=[4, 4])"
    result = add.apply_async(args=[4, 4])
    print "result.ready() is ",result.ready()
    print "result.get() ", result.get() #wait for the result
    print "result.successful() is ",result.successful()
    print "and the result is ", result.result
    print "delivery_mode is ",add.delivery_mode

def do_work(wait_for_result=False):
    """ here's our magic function that inserts into the message
    queue, does something, and optionally waits for a result.
    Highly dependent on the 
    import benchmark.celerybench.tasks module """ 
    result = add.apply_async(args=[4, 4])
    if wait_for_result:
        result.get() #block and wait for the result

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

def run_benchmark(iterations=100, roundtrip=False):
    """ run the benchmarks with timeit - using the do_work method
    defined above. This is setup to prodigously print, and be able
    to be run in chunks. i.e.

    for chunk in range(1,1000):
        (measurements,result_set) = run_benchmark(iterations=100)
        append_results(measurements, result_set) 
    """
    command_to_run = "do_work()"
    if roundtrip:
        command_to_run = "do_work(wait_for_result=True"
    t = timeit.Timer(stmt=command_to_run,
                     setup='from __main__ import do_work; gc.enable()')
    # run the timer against a single stmt loop 100 times
    measurements = t.repeat(iterations, 1)
    #print "=== RESULT ===", measurements
    result_set = calculate_results(measurements)
    print "==================================================="
    print "measurements: ", len(measurements)
    print "minimum: %.2f ms " % (result_set[0]*1000, )
    print "mean: %.2f ms" % (result_set[1]*1000, )
    print "maximum: %.2f ms" % (result_set[2]*1000, )
    print "std: %.2f ms" % (result_set[3]*1000, )
    print "median: %.2f ms" % (result_set[4]*1000, )
    print "p90: %.2f ms" % (result_set[5]*1000, )
    return (measurements, result_set)

def start_results_log():
    """ start writing a benchmark results output file """
    FOUT = open("benchmark_results.txt", "w")
    FOUT.write("measurements\tmin\tmean\tman\tstddev\tmedian\tp90\n")
    FOUT.close()

def append_results(measurements, result_set):
    """ append a chunk a results to the output file """
    FOUT = open("benchmark_results.txt", "a")
    stringout = "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (len(measurements),
                                               result_set[0],
                                               result_set[1],
                                               result_set[2],
                                               result_set[3],
                                               result_set[4],
                                               result_set[5])
    FOUT.write(stringout)
    FOUT.close()

if __name__ == '__main__':
    #dumb_test_code()
    start_results_log()
    for chunk in range(1,1000):
        (measurements,result_set) = run_benchmark(iterations=100)
        append_results(measurements, result_set) 
    print "FINI!"
