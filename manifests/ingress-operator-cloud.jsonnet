local ingress = import "ingress-operator.libsonnet";

ingress {
  service+: {
    spec+: {
      type: "LoadBalancer"
    },
  },
}