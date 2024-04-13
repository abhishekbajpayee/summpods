load("@rules_python//python:defs.bzl", "py_library")
load("@3rdparty//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "flask",
    deps = [
        requirement("Flask"),
        requirement("Jinja2"),
        requirement("Werkzeug"),
        requirement("itsdangerous"),
        requirement("click"),
        requirement("MarkupSafe"),
        requirement("blinker"),
        requirement("flask-material"),
    ],
)
