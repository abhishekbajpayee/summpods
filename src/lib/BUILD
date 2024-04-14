load("@3rdparty//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "lib",
    srcs = ["__init__.py"],
    deps = [
        ":models",
        ":utils",
        ":taddy",
        ":transcribe",
        ":summarize",
    ]
)

# Models
py_library(
    name = "models",
    srcs = ["models.py"],
)

# Utils
py_library(
    name = "utils",
    srcs = ["utils.py"],
)

# Taddy library
py_library(
    name = "taddy",
    srcs = ["taddy.py"],
    deps=[
        ":utils",
    ],
)

# Transcription library
py_library(
    name = "transcribe",
    srcs = ["transcribe.py"],
    deps=[
        ":utils",
        ":models",
    ],
)

# Summarization library
py_library(
    name = "summarize",
    srcs = ["summarize.py"],
    deps=[
        ":utils",
        ":models",
        ":transcribe",
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
