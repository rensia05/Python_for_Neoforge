# NeoForge side

This directory contains the Java side of the MVP.

Use it inside a normal NeoForge MDK project:

1. Create or copy a NeoForge MDK project into `neoforge-mod`.
2. Keep the Java package under `src/main/java/com/pythonforneoforge`.
3. Keep generated Python resources under `src/main/resources/assets/python_for_neoforge`.
4. Run the Python builder before launching the mod.

The Java loader reads:

```text
assets/python_for_neoforge/pyneoforge/generated.json
```

Then it registers generated items and blocks through `DeferredRegister`.
