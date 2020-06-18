local util = import "util.libsonnet";
local kube = util.kube;

local IMAGE = "gitea/gitea:latest";
local MODULE_NAME = "gitea";

function (secretKey) {
  service: kube.Service(MODULE_NAME) {target_pod: $.deployment.spec.template},

  deployment: kube.Deployment(MODULE_NAME) {
    spec+: {
      template+: {
        spec+: {
          containers: [kube.Container(MODULE_NAME) {
            image: IMAGE,
            env_: {
              RUN_MODE: "prod",
              INSTALL_LOCK: "true",
              DISABLE_REGISTRATION: "true",
              SECRET_KEY: kube.SecretKeyRef($.secret, "secretKey"),
            },
            ports_: { 
              http: { containerPort: 3000, protocol: "TCP" },
              ssh: { containerPort: 22, protocol: "TCP" },
            },
            livenessProbe: util.basicProbe("HTTP", 3000, "/"),
            readinessProbe: self.livenessProbe,
            volumeMounts_: {
              data: { mountPath: "/data" }
            }
          }],
          volumes_: {
            data: { persistentVolumeClaim: { claimName: $.pvc.metadata.name }},
          },
        },
      },
    },
  },

  pvc: kube.PersistentVolumeClaim(MODULE_NAME) {
    spec+: {
      accessModes: ["ReadWriteOnce"],
      resources: { requests: { storage: "5Gi" }},
    },
  },

  secret: kube.Secret(MODULE_NAME) {
    data_: {
      secretKey: secretKey
    },
  },
}
