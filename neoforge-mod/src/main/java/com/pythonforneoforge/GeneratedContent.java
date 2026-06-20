package com.pythonforneoforge;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
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
        registerItems(generatedMod.items());
        registerBlocks(generatedMod.blocks());
        registerCreativeTabs(generatedMod.creativeTabs());
    }

    private static void registerItems(List<GeneratedContentLoader.GeneratedItem> items) {
        for (GeneratedContentLoader.GeneratedItem item : items) {
            DeferredHolder<Item, Item> registeredItem =
                    ITEMS.register(item.id(), () -> new Item(new Item.Properties().stacksTo(item.maxStackSize())));
            ITEMS_BY_ID.put(item.id(), registeredItem);
        }
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

        throw new IllegalStateException("Unknown generated creative tab entry: " + id);
    }

    private static String stripOwnNamespace(String id) {
        String prefix = PythonForNeoForge.MOD_ID + ":";
        return id.startsWith(prefix) ? id.substring(prefix.length()) : id;
    }
}
