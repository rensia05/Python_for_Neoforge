package com.pyneoforge.generated;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;

@Mod(PythonForNeoForge.MOD_ID)
public final class PythonForNeoForge {
    public static final String MOD_ID = "__MOD_ID__";

    public PythonForNeoForge(IEventBus modEventBus) {
        GeneratedContent.registerAll(modEventBus);
    }
}
