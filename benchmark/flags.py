import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_string('graphite_server', '192.168.1.121', 'host running graphite and pystatsd service')
gflags.DEFINE_integer('graphite_port', 2003, 'graphite/(py)statsd port to send data into')
gflags.DEFINE_integer('benchagent_interval', 10, 'interval in which benchagent sends in metrics')

#gflags.DEFINE_boolean('debug', False, 'produce debugging output')
