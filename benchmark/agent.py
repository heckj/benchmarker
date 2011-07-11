#!/usr/bin/env python
#  Copyright (c) 2011 Joe Heck (heckj@mac.com)
#
#
#  part of this code is forked from http://code.google.com/p/linux-metrics/
#  Copyright (c) 2010-2011 Corey Goldberg (http://goldb.org)
#
#  This file is part of linux-metrics
#
#  License :: OSI Approved :: MIT License:
#      http://www.opensource.org/licenses/mit-license
#
#      Permission is hereby granted, free of charge, to any person obtaining a copy
#      of this software and associated documentation files (the "Software"), to deal
#      in the Software without restriction, including without limitation the rights
#      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#      copies of the Software, and to permit persons to whom the Software is
#      furnished to do so, subject to the following conditions:
#
#      The above copyright notice and this permission notice shall be included in
#      all copies or substantial portions of the Software.


""" python utility/script to run on machines under test to spew relevant metrics
to an instance of pystatsd
"""
import re
import subprocess
import sys
import time

class LocalSystem(object):
    """ encapsulates local system details """
    def __init__(self):
        self.hostname_string = None

    def process_map(self):
        """ runs ps -aux locally on the host and breaks it down into a list of dictionaries
        returning that list for further processing """
        result = []
        ps_aux = subprocess.Popen(["ps", "auxw"], stdout=subprocess.PIPE)
        (ps_data, ps_error) = ps_aux.communicate()
        list_of_processes = ps_data.splitlines()
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            for ps_string in list_of_processes:
                process_set = ps_string.split()
                process_dict = {}
                # process_set[0] = user
                process_dict['user'] = process_set[0]
                # process_set[1] = pid
                process_dict['pid'] = process_set[1]
                # process_set[2] = %cpu
                process_dict['cpu'] = process_set[2]
                # process_set[3] = %mem
                process_dict['mem'] = process_set[3]
                # process_set[4] = VSZ (in KB)
                process_dict['vsz'] = process_set[4]
                # process_set[5] = RSS (in KB)
                process_dict['rss'] = process_set[5]
                # process_set[6] = tty
                process_dict['tty'] = process_set[6]
                # process_set[7] = status
                process_dict['status'] = process_set[7]
                # process_set[8] = start
                process_dict['start'] = process_set[8]
                # process_set[9] = time
                process_dict['time'] = process_set[9]
                # process_set[10] = command
                process_dict['command'] = process_set[10]
                result.append(process_dict)
        else:
            raise RuntimeError("Not implemented on sys.platform == %s" % sys.platform)
        return result

    def hostname(self):
        """ runs hostname and returns the result as a string """
        if self.hostname_string:
            return self.hostname_string
        print "LOADING!"
        self.hostname_string = subprocess.Popen(["hostname"], stdout=subprocess.PIPE).communicate()[0]
        return self.hostname_string.rstrip("\r\n")

    def load_avg(self):
        """Return a sequence of system load averages (1min, 5min, 15min).

        number of jobs in the run queue or waiting for disk I/O
        averaged over 1, 5, and 15 minutes
        """
        with open('/proc/loadavg') as f:
            line = f.readline()
        load_avgs = [float(x) for x in line.split()[:3]]
        return load_avgs

    def cpu_times(self):
        """Return a sequence of cpu times.

        each number in the sequence is the amount of time, measured in units
        of USER_HZ (1/100ths of a second on most architectures), that the system
        spent in each cpu mode: (user, nice, system, idle, iowait, irq, softirq, [steal], [guest]).

        on SMP systems, these are aggregates of all processors/cores.
        """
        with open('/proc/stat') as f:
            line = f.readline()
        cpu_times = [int(x) for x in line.split()[1:]]
        return cpu_times

    def cpu_percents(self, sample_duration=1):
        """Return a dictionary of usage percentages and cpu modes.
        elapsed cpu time samples taken at 'sample_time (seconds)' apart.
        cpu modes: 'user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq'
        on SMP systems, these are aggregates of all processors/cores.
        """

        deltas = self.__cpu_time_deltas(sample_duration)
        total = sum(deltas)
        percents = [100 - (100 * (float(total - x) / total)) for x in deltas]

        return {
            'user': percents[0],
            'nice': percents[1],
            'system': percents[2],
            'idle': percents[3],
            'iowait': percents[4],
            'irq': percents[5],
            'softirq': percents[6],
        }

    def __cpu_time_deltas(self, sample_duration):
        """Return a sequence of cpu time deltas for a sample period.
        elapsed cpu time samples taken at 'sample_time (seconds)' apart.
        each value in the sequence is the amount of time, measured in units
        of USER_HZ (1/100ths of a second on most architectures), that the system
        spent in each cpu mode: (user, nice, system, idle, iowait, irq, softirq, [steal], [guest]).
        on SMP systems, these are aggregates of all processors/cores.
        """

        with open('/proc/stat') as f1:
            with open('/proc/stat') as f2:
                line1 = f1.readline()
                time.sleep(sample_duration)
                line2 = f2.readline()
        deltas = [int(b) - int(a) for a, b in zip(line1.split()[1:], line2.split()[1:])]
        return deltas

    def __proc_stat(self, stat):
        """ parses through /proc/stat and returns specific results based on variable stat """
        with open('/proc/stat') as f:
            for line in f:
                if line.startswith(stat):
                    return int(line.split()[1])

    def procs_running(self):
        """Return number of processes in runnable state."""
        return self.__proc_stat('procs_running')

    def procs_blocked(self):
        """Return number of processes blocked waiting for I/O to complete."""
        return self.__proc_stat('procs_blocked')


    def disk_busy(self, device, sample_duration=1):
        """Return disk busy percent."""
        with open('/proc/diskstats') as f1:
            with open('/proc/diskstats') as f2:
                content1 = f1.read()
                time.sleep(sample_duration)
                content2 = f2.read()
        sep = '%s ' % device
        for line in content1.splitlines():
            if sep in line:
                io_ms1 = line.strip().split(sep)[1].split()[9]
                break
        for line in content2.splitlines():
            if sep in line:
                io_ms2 = line.strip().split(sep)[1].split()[9]
                break
        delta = int(io_ms2) - int(io_ms1)
        total = sample_duration * 1000
        busy_pct = 100 - (100 * (float(total - delta) / total))
        return busy_pct

    def disk_reads_writes(self, device):
        """Return number of disk (reads, writes)."""
        with open('/proc/diskstats') as f:
            content = f.read()
        sep = '%s ' % device
        for line in content.splitlines():
            if sep in line:
                fields = line.strip().split(sep)[1].split()
                num_reads = int(fields[0])
                num_writes = int(fields[4])
                break
        return num_reads, num_writes

    def disk_reads_writes_persec(self, device, sample_duration=1):
        """Return number of disk (reads, writes) per sec during the sample_duration."""
        with open('/proc/diskstats') as f1:
            with open('/proc/diskstats') as f2:
                content1 = f1.read()
                time.sleep(sample_duration)
                content2 = f2.read()
        sep = '%s ' % device
        for line in content1.splitlines():
            if sep in line:
                fields = line.strip().split(sep)[1].split()
                num_reads1 = int(fields[0])
                num_writes1 = int(fields[4])
                break
        for line in content2.splitlines():
            if sep in line:
                fields = line.strip().split(sep)[1].split()
                num_reads2 = int(fields[0])
                num_writes2 = int(fields[4])
                break
        reads_per_sec = (num_reads2 - num_reads1) / float(sample_duration)
        writes_per_sec = (num_writes2 - num_writes1) / float(sample_duration)
        return reads_per_sec, writes_per_sec

    def mem_stats(self):
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1]) * 1024
                if line.startswith('MemFree:'):
                    mem_used = mem_total - (int(line.split()[1]) * 1024)
        return (mem_used, mem_total)

    def rx_tx_bytes(self, interface):  # by reading /proc
        for line in open('/proc/net/dev'):
            if interface in line:
                data = line.split('%s:' % interface)[1].split()
                rx_bytes, tx_bytes = (int(data[0]), int(data[8]))
                return (rx_bytes, tx_bytes)

    def rx_tx_bits(self, interface):  # by reading /proc
        rx_bytes, tx_bytes = rx_tx_bytes(interface)
        rx_bits = rx_bytes * 8
        tx_bits = tx_bytes * 8
        return (rx_bits, tx_bits)

    def net_stats_ifconfig(self, interface):  # by parsing ifconfig output
        output = subprocess.Popen(['ifconfig', interface], stdout=subprocess.PIPE).communicate()[0]
        rx_bytes = int(re.findall('RX bytes:([0-9]*) ', output)[0])
        tx_bytes = int(re.findall('TX bytes:([0-9]*) ', output)[0])
        return (rx_bytes, tx_bytes)

if __name__ == '__main__':
    # x = LocalSystem()
    # ps_set = x.process_map()
    # for ps_dict in ps_set:
    #     print "%s %s %s %s %s" % (ps_dict['cpu'], ps_dict['mem'], ps_dict['rss'], ps_dict['vsz'], ps_dict['command'])
    print LocalSystem().hostname()
