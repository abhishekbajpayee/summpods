load("@3rdparty//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "ws",
    srcs = [
        "conf/flask_conf.py",
        "views.py",
    ],
    deps = [
        "//src/lib",
    ],
    data = [
        "//src:templates",
    ]
)

py_binary(
    name = "wsgi",
    srcs = ["wsgi.py"],
    deps = [
        ":ws",
    ],
)

py_binary(
    name="app",
    srcs=[
        "app.py",
    ],
    deps=[
        "//src/lib",
    ],
)

py_test(
    name = "static_tests",
    srcs = [
        "flake.py",
    ],
    main = "flake.py",
    args = glob(["**/*.py"]),
    data = glob(["**/*.py"]),
    legacy_create_init = 0,
)
