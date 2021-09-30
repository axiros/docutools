# :srcref:fn=src/lcdoc/mkdocs/lp/plugs/python/pyplugs/diag_diagram/__init__.py,t=Diagrams Rendering Support

[Diagram](https://diagrams.mingrammer.com/) rendering support with svg mode.

## Requirements

`pip install diagrams`


## Example

[Set up][s1] your [defaults][s2], typically in a [silent](../../parameters.md#silent) block:

[s1]: https://diagrams.mingrammer.com/docs/guides/diagram 
[s2]: https://www.graphviz.org/doc/info/attrs.html

```python lp:python addsrc=5 eval=always session=gvdiag
# graphviz setup
gv = {
    "fontsize": "17",
    "fontcolor": "gray",
    "labelfontcolor": "white",
    "bgcolor": "transparent",
}

def diagr(**kw):
    '''factory creating same style Diagram context mgr objects'''
    from diagrams import Diagram
    setup = dict(show=False, outformat='svg', filename='tmpf',
                 graph_attr=gv,
                 node_attr=gv,
                 edge_attr=gv)
    setup.update(kw)
    return Diagram(**setup)

def T(typ, *a, **kw):
    kw['graph_attr'] = gv
    return typ(*a, **kw)
```

- Note the `outformat` is `svg`
- No limits regarding sophistication - the factory approach is just an example

Then use the library like normal, added our `show` based renderer at the end:


```python lp:python addsrc eval=always session=gvdiag
from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS
from diagrams.aws.database import ElastiCache, RDS
from diagrams.aws.network import ELB
from diagrams.aws.network import Route53

with diagr(name="Clustered Web Services") as d:
    dns = Route53("dns")
    lb = ELB("lb")

    with Cluster("Services"):
        svc_group = [ECS("web1"),
                     ECS("web2"),
                     ECS("web3")]

    with Cluster("DB Cluster"):
        db_main = RDS("userdb")
        db_main - [RDS("userdb ro")]

    memcached = ElastiCache("memcached")

    dns >> lb >> svc_group
    svc_group >> db_main
    svc_group >> memcached
show(d)
```

### Inline Colors

```python lp:python addsrc="Cloud Computing Example" eval=always session=gvdiag
from diagrams import Cluster, Edge
from diagrams.onprem.analytics import Spark
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.aggregator import Fluentd
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Nginx
from diagrams.onprem.queue import Kafka


with diagr(name="Advanced Web Service with On-Premise (colored)") as diag:
    ingress = Nginx("ingress")

    metrics = Prometheus("metric")
    metrics << Edge(color="firebrick", style="dashed") << Grafana("monitoring")

    with T(Cluster, "Service Cluster"):
        grpcsvc = [
            Server("grpc1", fontcolor="black"),
            Server("grpc2"),
            Server("grpc3")]

    with T(Cluster,"Sessions HA"):
        main = Redis("session")
        main - Edge(color="brown", style="dashed") - Redis("replica") << Edge(label="collect") << metrics
        grpcsvc >> Edge(color="brown") >> main

    with T(Cluster, "Database HA"):
        main = PostgreSQL("users")
        main - Edge(color="brown", style="dotted") - PostgreSQL("replica") << Edge(label="collect") << metrics
        grpcsvc >> Edge(color="black") >> main

    aggregator = Fluentd("logging")
    aggregator >> Edge(label="parse") >> Kafka("stream") >> Edge(color="black", style="bold") >> Spark("analytics")

    ingress >> Edge(color="darkgreen") << grpcsvc >> Edge(color="darkorange") >> aggregator

show(diag) # this is passed into the plugin rendering function
```

`lp:lightbox match='.diagrams_container'`

## Tech

The challenge here is to get **svgs** displayable within your docs.


They normally contain xlinked png images, pointing to your diagram package in site-directory - i.e.
not served by a static documentation server.

Solution:

Through a patched icon loader, we detect *which* png icons your diagram requires and copy them over to
`docsdir/icons_diagram`. You can git-ignore that directory, so that images do not pile up there.


