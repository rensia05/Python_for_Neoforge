package com.pythonforneoforge;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.DiggerItem;
import net.minecraft.world.item.HoeItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.PickaxeItem;
import net.minecraft.world.item.ShovelItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class GeneratedContent {
    private static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(Registries.ITEM, PythonForNeoForge.MOD_ID);
    private static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(Registries.BLOCK, PythonForNeoForge.MOD_ID);
    private static final DeferredRegister<CreativeModeTab> CREATIVE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, PythonForNeoForge.MOD_ID);

    private static final Map<String, DeferredHolder<Item, ? extends Item>> ITEMS_BY_ID = new HashMap<>();
    private static final Map<String, DeferredHolder<Block, Block>> BLOCKS_BY_ID = new HashMap<>();
    private static final Map<String, Tier> CUSTOM_TIERS_BY_ID = new HashMap<>();

    private static boolean loaded;

    private GeneratedContent() {
    }

    public static void registerAll(IEventBus modEventBus) {
        loadGeneratedDefinitions();
        ITEMS.register(modEventBus);
        BLOCKS.register(modEventBus);
        CREATIVE_TABS.register(modEventBus);
    }

    private static void loadGeneratedDefinitions() {
        if (loaded) {
            return;
        }
        loaded = true;

        GeneratedContentLoader.GeneratedMod generatedMod = GeneratedContentLoader.load(PythonForNeoForge.MOD_ID);
        registerCustomTiers(generatedMod.customTiers());
        registerItems(generatedMod.items());
        registerBlocks(generatedMod.blocks());
        registerCreativeTabs(generatedMod.creativeTabs());
    }

    private static void registerCustomTiers(List<GeneratedContentLoader.GeneratedTier> tiers) {
        for (GeneratedContentLoader.GeneratedTier tier : tiers) {
            Tier baseTier = tier(tier.baseTier());
            CUSTOM_TIERS_BY_ID.put(
                    tier.id(),
                    new GeneratedTier(
                            baseTier,
                            tier.durability(),
                            tier.miningSpeed(),
                            tier.attackDamageBonus(),
                            tier.enchantmentValue(),
                            () -> repairIngredient(tier.repairIngredient())));
        }
    }

    private static void registerItems(List<GeneratedContentLoader.GeneratedItem> items) {
        for (GeneratedContentLoader.GeneratedItem item : items) {
            DeferredHolder<Item, Item> registeredItem =
                    ITEMS.register(item.id(), () -> createItem(item));
            ITEMS_BY_ID.put(item.id(), registeredItem);
        }
    }

    private static Item createItem(GeneratedContentLoader.GeneratedItem item) {
        Item.Properties properties = new Item.Properties().stacksTo(item.maxStackSize());
        if (item.food() != null) {
            properties.food(createFoodProperties(item.food()));
        }

        Tier tier = tier(item.tier());
        return switch (item.kind()) {
            case "sword" -> new SwordItem(
                    tier,
                    properties.attributes(SwordItem.createAttributes(tier, item.attackDamage(3.0F), item.attackSpeed(-2.4F))));
            case "pickaxe" -> new PickaxeItem(
                    tier,
                    properties.attributes(DiggerItem.createAttributes(tier, item.attackDamage(1.0F), item.attackSpeed(-2.8F))));
            case "axe" -> new AxeItem(
                    tier,
                    properties.attributes(DiggerItem.createAttributes(tier, item.attackDamage(6.0F), item.attackSpeed(-3.1F))));
            case "shovel" -> new ShovelItem(
                    tier,
                    properties.attributes(DiggerItem.createAttributes(tier, item.attackDamage(1.5F), item.attackSpeed(-3.0F))));
            case "hoe" -> new HoeItem(
                    tier,
                    properties.attributes(DiggerItem.createAttributes(tier, item.attackDamage(-2.0F), item.attackSpeed(-1.0F))));
            default -> new Item(properties);
        };
    }

    private static FoodProperties createFoodProperties(GeneratedContentLoader.GeneratedFood food) {
        FoodProperties.Builder builder = new FoodProperties.Builder()
                .nutrition(food.nutrition())
                .saturationModifier(food.saturation());
        if (food.alwaysEdible()) {
            builder.alwaysEdible();
        }
        if (food.fast()) {
            builder.fast();
        }
        return builder.build();
    }

    private static Tier tier(String tier) {
        String tierId = tier == null ? "iron" : tier;
        Tier customTier = CUSTOM_TIERS_BY_ID.get(tierId);
        if (customTier != null) {
            return customTier;
        }
        return switch (tierId) {
            case "wood" -> Tiers.WOOD;
            case "stone" -> Tiers.STONE;
            case "diamond" -> Tiers.DIAMOND;
            case "gold" -> Tiers.GOLD;
            case "netherite" -> Tiers.NETHERITE;
            default -> Tiers.IRON;
        };
    }

    private static Ingredient repairIngredient(String id) {
        if (id == null || id.isBlank()) {
            return Ingredient.of();
        }
        if (id.startsWith("#")) {
            ResourceLocation tagId = resourceLocation(id.substring(1));
            return Ingredient.of(TagKey.create(Registries.ITEM, tagId));
        }
        return Ingredient.of(resolveItemLike(id));
    }

    private static void registerBlocks(List<GeneratedContentLoader.GeneratedBlock> blocks) {
        for (GeneratedContentLoader.GeneratedBlock block : blocks) {
            DeferredHolder<Block, Block> registeredBlock = BLOCKS.register(
                    block.id(),
                    () -> new Block(BlockBehaviour.Properties.of()
                            .strength((float) block.hardness(), (float) block.resistance())));
            BLOCKS_BY_ID.put(block.id(), registeredBlock);

            if (block.needsBlockItem()) {
                DeferredHolder<Item, BlockItem> registeredBlockItem =
                        ITEMS.register(
                                block.id(),
                                () -> new BlockItem(
                                        registeredBlock.get(),
                                        new Item.Properties().stacksTo(block.maxStackSize())));
                ITEMS_BY_ID.put(block.id(), registeredBlockItem);
            }
        }
    }

    private static void registerCreativeTabs(List<GeneratedContentLoader.GeneratedCreativeTab> tabs) {
        for (GeneratedContentLoader.GeneratedCreativeTab tab : tabs) {
            CREATIVE_TABS.register(tab.id(), () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup." + PythonForNeoForge.MOD_ID + "." + tab.id()))
                    .icon(() -> new ItemStack(resolveItemLike(tab.icon()).asItem()))
                    .displayItems((parameters, output) -> {
                        for (String entry : tab.entries()) {
                            output.accept(resolveItemLike(entry));
                        }
                    })
                    .build());
        }
    }

    private static ItemLike resolveItemLike(String id) {
        String localId = stripOwnNamespace(id);
        DeferredHolder<Item, ? extends Item> item = ITEMS_BY_ID.get(localId);
        if (item != null) {
            return item.get();
        }

        DeferredHolder<Block, Block> block = BLOCKS_BY_ID.get(localId);
        if (block != null) {
            return block.get();
        }

        if (id.contains(":")) {
            return BuiltInRegistries.ITEM.get(resourceLocation(id));
        }

        throw new IllegalStateException("Unknown generated creative tab entry: " + id);
    }

    private static ResourceLocation resourceLocation(String id) {
        return id.contains(":")
                ? ResourceLocation.parse(id)
                : ResourceLocation.fromNamespaceAndPath(PythonForNeoForge.MOD_ID, id);
    }

    private static String stripOwnNamespace(String id) {
        String prefix = PythonForNeoForge.MOD_ID + ":";
        return id.startsWith(prefix) ? id.substring(prefix.length()) : id;
    }

    private record GeneratedTier(
            Tier baseTier,
            int durability,
            float miningSpeed,
            float attackDamageBonus,
            int enchantmentValue,
            Supplier<Ingredient> repairIngredient) implements Tier {
        @Override
        public int getUses() {
            return durability;
        }

        @Override
        public float getSpeed() {
            return miningSpeed;
        }

        @Override
        public float getAttackDamageBonus() {
            return attackDamageBonus;
        }

        @Override
        public TagKey<Block> getIncorrectBlocksForDrops() {
            return baseTier.getIncorrectBlocksForDrops();
        }

        @Override
        public int getEnchantmentValue() {
            return enchantmentValue;
        }

        @Override
        public Ingredient getRepairIngredient() {
            return repairIngredient.get();
        }
    }
}
