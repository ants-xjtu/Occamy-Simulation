build_example(
  NAME sig_100g_log
  SOURCE_FILES sig_100g_log.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libpoint-to-point}
    ${libinternet}
    ${libapplications}
    ${libnetwork}
    ${libflow-monitor}
)
