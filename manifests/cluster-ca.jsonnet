local util = import "util.libsonnet";
local kube = util.kube;

local MODULE_NAME = "cluster-ca";


function (cert, key) {
  cert: kube.Secret(MODULE_NAME) {
    metadata+: { namespace: "default" },
    data_: {
      "tls.crt": cert,
    },
  },
  keypair: kube.Secret(MODULE_NAME + "-private") {
    metadata+: { namespace: "cert-manager" },
    data_: {
      "tls.crt": cert,
      "tls.key": key,
    },
  },
  issuer: kube._Object("cert-manager.io/v1alpha2", "ClusterIssuer", MODULE_NAME) {
    metadata+: { namespace: "cert-manager" },
    spec+: { ca: { secretName: $.keypair.metadata.name }},
  },

  // Insert cert into all hosts so we can pull images
  
}


