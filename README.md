Benchmarking Code
=================

This project contains various benchmark tests and associated code to measure
the performance of OpenStack components.

The initial benchmark is against the message queue to allow for testing of
various queue configurations.

Default is RabbitMQ, stock install for Ubuntu based systems

Variations to test:

* stock Ubuntu with RabbitMQ
* reconfigured Ubuntu with durable message queues configured
* reconfigured Ubuntu with durable message queues configured and RabbitMQ
configured HA with Pacemaker
* reconfigured Ubuntu with durable message queues on a replicated
(GlusterFS?) volume
