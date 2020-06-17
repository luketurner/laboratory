local kube = import "./vendor/kube.libsonnet";

{

  kube: kube,

  basicProbe(scheme, port, path): {
    failureThreshold: 3,
    httpGet: { path: path, port: port, scheme: scheme },
    periodSeconds: 10,
    successThreshold: 1,
    timeoutSeconds: 1
  },

  Certificate(name, resourceRef): kube._Object("cert-manager.io/v1alpha2", "Certificate", name) {
    spec+: {
      secretName: name + "-tls",
      duration: "2160h", #90d
      renewBefore: "360h", #15d
      // organization: ["picluster"],
      // commonName: "registry",
      keySize: 4096,
      keyAlgorithm: "rsa",
      keyEncoding: "pkcs1",
      usages: ["client auth", "server auth"],
      dnsNames: [resourceRef.metadata.name], // TODO -- should have better dns name like registry.default.svc.cluster.local?
      issuerRef: { name: "cluster-ca", kind: "ClusterIssuer" },
    },
  },

  certSecret(certName): { secretName: certName + "-tls" },
  certCA(certName): self.certSecret(certName) { items: [{ key: "ca.crt", path: "ca.crt" }], },

}