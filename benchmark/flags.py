import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_string('graphite-server', '192.168.1.18', 'host running graphite and pystatsd service')
gflags.DEFINE_integer('graphite-port', 8125, 'graphite/(py)statsd port to send data into')
#gflags.DEFINE_boolean('debug', False, 'produce debugging output')