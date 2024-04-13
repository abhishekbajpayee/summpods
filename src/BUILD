load("@3rdparty//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "ws",
    srcs = glob(["**/*.py"]),
    deps = [
        # Flask
        "//3rdparty:flask",
    ],
    data = [
        "//src:templates",
    ]
)

py_binary(
  name = "wsgi",
  srcs = ["wsgi.py"],
  deps = [
    ":ws"
  ]
)

py_binary(
    name="app",
    srcs=[
        "app.py",
    ],
    deps=[],
)
