package com.pythonforneoforge;

import com.google.gson.Gson;
import com.google.gson.annotations.SerializedName;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;

public final class GeneratedContentLoader {
    private static final Gson GSON = new Gson();

    private GeneratedContentLoader() {
    }

    public static GeneratedMod load(String modId) {
        String resourcePath = "/assets/" + modId + "/pyneoforge/generated.json";
        try (InputStream stream = GeneratedContentLoader.class.getResourceAsStream(resourcePath)) {
            if (stream == null) {
                return GeneratedMod.empty();
            }
            try (InputStreamReader reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) {
                GeneratedMod generatedMod = GSON.fromJson(reader, GeneratedMod.class);
                return generatedMod == null ? GeneratedMod.empty() : generatedMod.withDefaults();
            }
        } catch (IOException exception) {
            throw new IllegalStateException("Failed to load generated Python NeoForge definitions", exception);
        }
    }

    public record GeneratedMod(
            int schema,
            @SerializedName("minecraft_version") String minecraftVersion,
            List<GeneratedItem> items,
            List<GeneratedBlock> blocks,
            @SerializedName("creative_tabs") List<GeneratedCreativeTab> creativeTabs) {
        static GeneratedMod empty() {
            return new GeneratedMod(1, null, List.of(), List.of(), List.of());
        }

        GeneratedMod withDefaults() {
            return new GeneratedMod(
                    schema == 0 ? 1 : schema,
                    minecraftVersion,
                    items == null ? List.of() : items,
                    blocks == null ? List.of() : blocks,
                    creativeTabs == null ? List.of() : creativeTabs);
        }
    }

    public record GeneratedItem(
            String id,
            @SerializedName("display_name") String displayName,
            @SerializedName("max_stack_size") int maxStackSize,
            String kind,
            GeneratedFood food,
            String tier,
            @SerializedName("attack_damage") Float attackDamage,
            @SerializedName("attack_speed") Float attackSpeed) {
        public int maxStackSize() {
            return maxStackSize <= 0 ? 64 : maxStackSize;
        }

        public String kind() {
            return kind == null ? "item" : kind;
        }

        public float attackDamage(float fallback) {
            return attackDamage == null ? fallback : attackDamage;
        }

        public float attackSpeed(float fallback) {
            return attackSpeed == null ? fallback : attackSpeed;
        }
    }

    public record GeneratedFood(
            int nutrition,
            float saturation,
            @SerializedName("always_edible") boolean alwaysEdible,
            boolean fast) {
    }

    public record GeneratedBlock(
            String id,
            @SerializedName("display_name") String displayName,
            double hardness,
            double resistance,
            @SerializedName("needs_block_item") boolean needsBlockItem,
            @SerializedName("max_stack_size") int maxStackSize) {
        public double hardness() {
            return hardness < 0 ? 1.5 : hardness;
        }

        public double resistance() {
            return resistance < 0 ? 6.0 : resistance;
        }

        public int maxStackSize() {
            return maxStackSize <= 0 ? 64 : maxStackSize;
        }
    }

    public record GeneratedCreativeTab(String id, @SerializedName("display_name") String displayName, String icon, List<String> entries) {
        public List<String> entries() {
            return entries == null ? List.of() : entries;
        }
    }
}
