import uuid

# satin_ip,hosts,ifaces must have same amount of items in each
satin_ips    = ('192.168.122.71', '192.168.122.72')
satin_hosts  = ('vac.system',     'phpadmin.system')
satin_ifaces = ('dummy0',         'dummy0:1')
# end satin iface setup

# DO NOT EDIT BELOW
class SetupHosts(object):
    def __init__(self):
        self.satin_domains = zip(satin_ips, satin_hosts, satin_ifaces)
        self.host_out = list()

    def run(self):
        gen_uuid = uuid.uuid1()
        uuid_str = "# UUID: %s\n" % (gen_uuid,)
        self.host_out.append(uuid_str)
        for ip, host, iface in self.satin_domains:
            self.host_out.append("%s %s # Attach to interface %s" % (ip, host, iface))
        self.host_out.append("""\n\n
# Typically you'll want to use something like ifconfig
# to create your interfaces. For example,
# modprobe dummy
# ifconfig dummy0 192.168.122.71 netmask 255.0.0.0
# ifconfig dummy0:1 192.168.122.72 netmask 255.0.0.0
""")
        return self.host_out
