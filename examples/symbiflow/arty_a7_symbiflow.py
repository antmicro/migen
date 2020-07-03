#!/usr/bin/env python3
# This file is Copyright (c) 2020 Antmicro <www.antmicro.com>
# License: BSD

from migen import *
from migen.genlib.io import CRG
from migen.build.platforms import arty_a7

class Demo(Module):
    def __init__(self, platform):
        freq = 1000 * 1000 * 1000 // platform.default_clk_period

        counter = Signal(int(freq - 1).bit_length())
        color = Signal(3)

        self.sync += [
            If(counter == int(freq - 1),
                color.eq(color + 1),
                counter.eq(0),
            ).Else(
                counter.eq(counter + 1),
            )
        ]

        leds = []
        switches = []
        for i in range(4):
            leds.append(platform.request("rgb_led", i))
            switches.append(platform.request("user_sw", i))
            self.comb += If(switches[i] == 1,
                    leds[i].raw_bits().eq(color)
                ).Else(
                    leds[i].raw_bits().eq(0)
                )

class _CRG(CRG):
    def __init__(self, platform):
        clk = platform.request(platform.default_clk_name)
        clk_ibuf = Signal()
        clk_bufg = Signal()
        self.specials += Instance("IBUF", i_I=clk, o_O=clk_ibuf)
        self.specials += Instance("BUFG", i_I=clk_ibuf, o_O=clk_bufg)

        super().__init__(clk_bufg)

        platform.add_period_constraint(clk_bufg, platform.default_clk_period)

def main():
    platform = arty_a7.Platform(toolchain="symbiflow", programmer="symbiflow", device="xc7a35tcsg324-1")

    demo = Demo(platform)
    demo.submodules.crg = _CRG(platform)

    platform.build(demo)

if __name__ == "__main__":
    main()
