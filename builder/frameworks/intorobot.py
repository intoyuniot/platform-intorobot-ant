# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
IntoRobot

IntoRobot Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://www.intorobot.com
"""

from os.path import isdir, join

from SCons.Script import COMMAND_LINE_TARGETS, DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_NAME = "framework-intorobot-ant"
FRAMEWORK_DIR = platform.get_package_dir(FRAMEWORK_NAME)
FRAMEWORK_VERSION = platform.get_package_version(FRAMEWORK_NAME)
assert isdir(FRAMEWORK_DIR)

env.Replace(
    LIBS=[],
    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections,--relax",
        "-mthumb",
        "-nostartfiles",
        "-mcpu=%s" % env.BoardConfig().get("build.cpu")
    ]
)

env.Append(
    ASFLAGS=[
        "-fmessage-length=0",
    ],
    CFLAGS=[
        "-Wno-pointer-sign",
        "-std=gnu99"
    ],
    CCFLAGS=[
        "-fno-strict-aliasing",
        "-Wfatal-errors",
        "-w",
        "-fno-common",
        "-Wno-switch",
        "-Wno-error=deprecated-declarations",
        "-fmessage-length=0"
    ],
    CXXFLAGS=[
        "-fcheck-new",
        "-std=gnu++11",
        "-fpermissive"
    ],
    LINKFLAGS=[
        "%s" % (join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "build", "startup", board.get("build.startup_object"))),
        "-mlittle-endian",
        "-Xlinker",
        "--gc-sections",
        "-Wl,--defsym,__STACKSIZE__=400",
        "--specs=nano.specs",
        "--specs=nosys.specs"
    ],
)

env.Append(
    CPPDEFINES=[
        ("INTOROBOT", 1),
        ("INTOYUN", 1),
        ("FIRMLIB_VERSION_STRING", FRAMEWORK_VERSION),
        ("PLATFORM_THREADING", 1),
        ("INTOROBOT_ARCH_ARM"),
        ("INTOROBOT_PLATFORM"),
        ("RELEASE_BUILD")
    ],
    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "hal", "inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "hal", "shared"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "hal", "stm32"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "platform", "shared", "inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "platform", "MCU", "shared", "STM32", "inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "services", "inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "system", "inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "user", "inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "wiring", "inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "platform", "MCU", "STM32L1xx", "IntoRobot_Firmware_Driver", "inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "platform", "MCU", "STM32L1xx", "CMSIS", "Include"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "platform", "MCU", "STM32L1xx", "CMSIS", "Device", "ST", "STM32L1xx", "Include"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "platform", "MCU", "STM32L1xx", "STM32L1xx_HAL_Driver", "Inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "platform", "MCU", "STM32L1xx", "STM32_USB_Device_Library", "Class", "CDC", "Inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "platform", "MCU", "STM32L1xx", "STM32_USB_Device_Library", "Class", "DFU", "Inc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "platform", "MCU", "STM32L1xx", "STM32_USB_Device_Library", "Core", "Inc"),
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "hal"),
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "hal", "inc"),
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "wiring_ex", "inc"),
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "wiring_ex", "src"),
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "communication", "lorawan"),
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "communication", "mqtt", "inc")
    ],
    LIBPATH=[
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "lib"),
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "build", "linker")
    ],
    LIBS=[
        "wiring", "wiring_ex", "hal", "system", "services", "communication", "platform", "gcc", "c"
    ]
)
env.Replace(
    UPLOADERFLAGS=[
        "write",        # write in flash
        "$SOURCES",     # firmware path to flash
        board.get("upload.address")    # flash start address
    ]
)

if env.subst("$UPLOAD_PROTOCOL") in ("serial", "dfu"):
    _upload_tool = "serial_upload"
    _upload_flags = ["{upload.altID}", "{upload.usbID}"]
    if env.subst("$UPLOAD_PROTOCOL") == "dfu":
        _upload_tool = "intorobot_upload"
        _usbids = env.BoardConfig().get("build.hwids")
        _upload_flags = [0, "%s:%s" % (_usbids[0][0][2:], _usbids[0][1][2:])]

    env.Replace(
        UPLOADER=_upload_tool,
        UPLOADERFLAGS=["$UPLOAD_PORT"] + _upload_flags,
        UPLOADCMD=(
            '$UPLOADER $UPLOADERFLAGS $PROJECT_DIR/$SOURCES %s' %  board.get("upload.address"))
    )


if "__debug" in COMMAND_LINE_TARGETS:
    env.Append(CPPDEFINES=[
        "SERIAL_USB", "GENERIC_BOOTLOADER",
        ("CONFIG_MAPLE_MINI_NO_DISABLE_DEBUG", "1")
    ])

env.Prepend(_LIBFLAGS="-Wl,-whole-archive ")
env.Append(_LIBFLAGS=" -Wl,-no-whole-archive")

