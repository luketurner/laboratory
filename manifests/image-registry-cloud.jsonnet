local util = import "util.libsonnet";
local kube = util.kube;

function (dockerconfigjson, dockerconfigjson_write) {

  pushSecret: kube.Secret("do-registry-write") {
    data_: {
      ".dockerconfigjson": dockerconfigjson_write
    },
  },

  pullSecret: kube.Secret("do-registry") {
    type: "kubernetes.io/dockerconfigjson",
    data_: {
      ".dockerconfigjson": dockerconfigjson
    },
  },

}