local util = import "util.libsonnet";
local kube = util.kube;

local MODULE_NAME = "ingress";

{

  rbac: {
    account: kube.ServiceAccount(MODULE_NAME) {
      metadata+: {
        namespace: "default" # Note - subjects_ ref. requires some namespace value to always be present
      }, 
    },
    role: kube.ClusterRole(MODULE_NAME) {
      rules: [
        {
          apiGroups: ["extensions"],
          resources: ["ingresses"],
          verbs: ["get", "list"],
        },
        {
          apiGroups: [""],
          resources: ["namespaces", "services", "endpoints", "pods"],
          verbs: ["get", "list"],
        },
        {
          apiGroups: ["zalando.org"],
          resources: ["routegroups"],
          verbs: ["get", "list"],
        },
      ],
    },
    roleBinding: kube.ClusterRoleBinding(MODULE_NAME) {
      subjects_: [$.rbac.account],
      roleRef_: $.rbac.role
    },
  },

  service: kube.Service(MODULE_NAME) {
    target_pod: $.deployment.spec.template,
    spec+: {
      ports: [{ name: "ingress", port: 80, targetPort: 9999 }],
    },
  },

  deployment: kube.Deployment(MODULE_NAME) {
    spec+: {
      strategy: { rollingUpdate: { maxSurge: 0 },},
      template+: {
        spec+: {
          serviceAccountName: MODULE_NAME,
          containers: [
            kube.Container("skipper") {
              image: "registry.opensource.zalan.do/pathfinder/skipper:v0.11.40",
              ports_: { ingress: { containerPort: 9999 }},
              args: [
                "skipper",
                "-kubernetes",
                "-kubernetes-in-cluster",
                "-kubernetes-path-mode=path-prefix",
                "-address=:9999",
                "-wait-first-route-load",
                "-proxy-preserve-host",
                "-serve-host-metrics",
                "-disable-metrics-compat",
                "-enable-profile",
                "-enable-ratelimits",
                "-experimental-upgrade",
                "-metrics-exp-decay-sample",
                "-reverse-source-predicate",
                "-lb-healthcheck-interval=3s",
                "-metrics-flavour=prometheus",
                "-enable-connection-metrics",
                "-max-audit-body=0",
                "-histogram-metric-buckets=.0001,.00025,.0005,.00075,.001,.0025,.005,.0075,.01,.025,.05,.075,.1,.2,.3,.4,.5,.75,1,2,3,4,5,7,10,15,20,30,60,120,300,600",
                "-expect-continue-timeout-backend=30s",
                "-keepalive-backend=30s",
                "-max-idle-connection-backend=0",
                "-response-header-timeout-backend=1m",
                "-timeout-backend=1m",
                "-tls-timeout-backend=1m",
                "-close-idle-conns-period=20s",
                "-idle-timeout-server=62s",
                "-read-timeout-server=5m",
                "-write-timeout-server=60s",
                '-default-filters-prepend=enableAccessLog(4,5) -> lifo(2000,20000,"3s")'
              ],
              readinessProbe: {
                httpGet: { path: "/kube-system/healthz", port: 9999 },
                initialDelaySeconds: 60,
                timeoutSeconds: 5
              },
            }
          ],
        },
      },
    },
  },
}

/*
        resources:
          limits:
            cpu: "4"
            memory: "1Gi"
          requests:
            cpu: "4"
            memory: "1Gi"
*/