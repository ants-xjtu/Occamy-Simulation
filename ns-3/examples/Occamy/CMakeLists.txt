build_example(
  NAME occamy_100g_utilization
  SOURCE_FILES occamy_100g_utilization.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libpoint-to-point}
    ${libinternet}
    ${libapplications}
    ${libnetwork}
    ${libflow-monitor}
)

build_example(
  NAME occamy_100g_benchmark
  SOURCE_FILES occamy_100g_benchmark.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libpoint-to-point}
    ${libinternet}
    ${libapplications}
    ${libnetwork}
    ${libflow-monitor}
)

build_example(
  NAME occamy_100g_alltoall
  SOURCE_FILES occamy_100g_alltoall.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libpoint-to-point}
    ${libinternet}
    ${libapplications}
    ${libnetwork}
    ${libflow-monitor}
)

build_example(
  NAME occamy_100g_allreduce
  SOURCE_FILES occamy_100g_allreduce.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libpoint-to-point}
    ${libinternet}
    ${libapplications}
    ${libnetwork}
    ${libflow-monitor}
)

build_example(
  NAME occamy_100g_queryload
  SOURCE_FILES occamy_100g_queryload.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libpoint-to-point}
    ${libinternet}
    ${libapplications}
    ${libnetwork}
    ${libflow-monitor}
)