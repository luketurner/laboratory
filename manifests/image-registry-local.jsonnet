local util = import "util.libsonnet";
local kube = util.kube;

local IMAGE = "registry:2.7.1";
local CONTAINER_PORT = 5000;
local MODULE_NAME = "registry";

function (httpSecret) {
  service: kube.Service(MODULE_NAME) {
    target_pod: $.deployment.spec.template,
    spec+: {
      ports: [{ name: "http", port: 443, targetPort: 5000 }],
    },
  },

  deployment: kube.Deployment(MODULE_NAME) {
    spec+: {
      template+: {
        spec+: {
          containers: [kube.Container(MODULE_NAME) {
            image: IMAGE,
            command: ["/bin/registry", "serve", "/etc/docker/registry/config.yml"],
            env_: {
              REGISTRY_HTTP_SECRET: kube.SecretKeyRef($.secret, "httpSecret"),
              REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY: "/var/lib/registry",
              // REGISTRY_HTTP_TLS_CERTIFICATE: "/data/tls/tls.crt",
              // REGISTRY_HTTP_TLS_KEY: "/data/tls/tls.key",
              // REGISTRY_HTTP_TLS_CLIENTCAS: "/config/ca.crt",
            },
            ports_: { registry: { containerPort: CONTAINER_PORT, protocol: "TCP" }},
            livenessProbe: util.basicProbe("HTTP", CONTAINER_PORT, "/"),
            readinessProbe: self.livenessProbe,
            volumeMounts_: {
              data: { mountPath: "/var/lib/registry/" },
              config: { mountPath: "/etc/docker/registry" },
              tls: { mountPath: "/data/tls" },
            }
          }],
          volumes_: {
            data: { persistentVolumeClaim: { claimName: $.pvc.metadata.name }},
            config: { configMap: { defaultMode: 420, name: $.config.metadata.name }},
            tls: { secret: util.certSecret(MODULE_NAME) },
          },
        },
      },
    },
  },

  certificate: util.Certificate(MODULE_NAME, $.service) {
    spec+: {
      usages: ["server auth"],
    },
  },

  config: kube.ConfigMap(MODULE_NAME) {
    data: {
      "config.yml": |||
        health:
          storagedriver:
            enabled: true
            interval: 10s
            threshold: 3
        http:
          addr: :5000
          headers:
            X-Content-Type-Options:
            - nosniff
        log:
          fields:
            service: registry
        storage:
          cache:
            blobdescriptor: inmemory
        version: 0.1
      |||
    },
  },

  pvc: kube.PersistentVolumeClaim(MODULE_NAME) {
    spec+: {
      accessModes: ["ReadWriteOnce"],
      resources: { requests: { storage: "50Gi" }},
    },
  },

  secret: kube.Secret(MODULE_NAME) {
    data_: {
      httpSecret: httpSecret
    },
  },
}
