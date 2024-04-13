load("@3rdparty//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "ws",
    srcs = [
        "conf/flask_conf.py",
        "home.py",
    ],
    deps = [
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
        ":ws",
        ":models",
    ],
)

py_binary(
    name="app",
    srcs=[
        "app.py",
    ],
    deps=[
        ":taddy",
        ":transcribe",
        ":models",
        ":utils",
    ],
)

# Taddy library
py_library(
    name = "taddy",
    srcs = ["taddy.py"],
    deps=[
        ":utils",
        requirement("requests"),
        requirement("urllib3"),
        requirement("chardet"),
        requirement("idna"),
        requirement("certifi"),
    ],
)

# Transcription library
py_library(
    name = "transcribe",
    srcs = ["transcribe.py"],
    deps=[
        ":utils",
        ":models",
        requirement("openai"),
        requirement("urllib3"),
    ],
)

# Utils
py_library(
    name = "utils",
    srcs = ["utils.py"],
    deps=[
        requirement("pyyaml"),
    ],
)

# Models
py_library(
    name = "models",
    srcs = ["models.py"],
    deps=[
        requirement("flask-mongoengine"),
        "//3rdparty:flask",
    ]
)

py_test(
    name = "flake",
    srcs = [
        "flake.py",
    ],
    main = "flake.py",
    args = glob(["*.py"]),
    data = glob(["*.py"]),
    legacy_create_init = 0,
    deps = [
        requirement("flake8"),
        requirement("pyflakes"),
        requirement("pycodestyle"),
    ],
)
