#!/usr/bin/python

# import relevant libraries
import os
from optparse import OptionParser
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, UserSwitch, Host
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI


#This is used to Parse command line options(two spines, two leafs, two host for each leaf )
def parseOptions():
    """Parse CLI options"""
    parser = OptionParser()
    parser.add_option('--spine', dest='spine', type='int', default=2,
                      help='number of spine switches, default=2')
    parser.add_option('--leaf', dest='leaf', type='int', default=2,
                      help='number of leaf switches, default=2')
    parser.add_option('--fanout', dest='fanout', type='int', default=2,
                      help='number of hosts per leaf switch, default=2')
    (options, args) = parser.parse_args()
    return options, args


opts, args = parseOptions()

#Create the leaf  and spine switches
class LeafAndSpine(Topo):
    def __init__(self, spine=2, leaf=2, fanout=2, **opts):
        "Create SR SDN Nework Topology."

        Topo.__init__(self, **opts)

        # Add spine switches
        spines = {}
        for s in range(spine):
            spines[s] = self.addSwitch('spine40%s' % (s + 1))
        # Set link speeds to 10Mbit/s
        linkopts = dict(bw=10)

        # Add Leaf switches
        for ls in range(leaf):
            leafSwitch = self.addSwitch('leaf%s' % (ls + 1))
            # Connect leaf to  spines
            for s in range(spine):
                switch = spines[s]

  # Connect leaf to  spines switches
            for s in range(spine):
                switch = spines[s]
                self.addLink(leafSwitch, switch, **linkopts)
            # Add two hosts for each leaf
            for f in range(fanout):
                host = self.addHost('h%s' % (ls * fanout + f + 1),
                                         cls=IpHost,
                                         ip='10.0.%s.%s/24' % ((ls + 1), (f + 1)),
                                         gateway='10.0.%s.254' % (ls + 1))
                self.addLink(host, leafSwitch, **linkopts)
#set gateway
class IpHost(Host):
    def __init__(self, name, gateway, *args, **kwargs):
        super(IpHost, self).__init__(name, *args, **kwargs)
        self.gateway = gateway

#set mtu
    def config(self, **kwargs):
        Host.config(self, **kwargs)
        mtu = "ifconfig "+self.name+"-eth0 mtu 1490"
        self.cmd(mtu)
        self.cmd('ip route add default via %s' % self.gateway)


def config(opts):
    spine = opts.spine
    leaf = opts.leaf
    fanout = opts.fanout
    controllers= [ os.environ['OC%s' % i] for i in range(1,4) ]
    #controllers = ['127.0.0.1']
    topo = LeafAndSpine(spine=spine, leaf=leaf, fanout=fanout)
    net = Mininet(topo=topo, link=TCLink,
                  switch=UserSwitch,
                  controller = None,
                  autoSetMacs = True)
    i = 0
    for ip in controllers:
        net.addController( "c%s" % (i), controller=RemoteController, ip=ip)
        i += 1;
    net.start()
    CLI(net)
    net.stop()

#main process
if __name__ == '__main__':
    setLogLevel('info')
    config(opts)
    os.system('sudo mn -c')
