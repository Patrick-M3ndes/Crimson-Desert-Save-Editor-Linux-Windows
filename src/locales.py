#!/usr/bin/env python3
"""
Módulo de internacionalização (i18n) para o Crimson Desert Save Editor.
Separa as strings de texto da lógica do programa.
"""

from typing import Dict

# ==============================================================================
# TABELA DE TRADUÇÕES (Lookup Table em Memória)
# ==============================================================================
LOCALES: Dict[str, Dict[str, str]] = {
    "pt": {
        # Menu Principal
        "APP_TITLE": "⚔️  CRIMSON DESERT - ITEM SAVE EDITOR (Enhanced Edition) ⚔️",
        "CHOOSE_LANGUAGE": "Escolha o idioma / Choose language:",
        "LANG_PT": "Português",
        "LANG_EN": "English",
        "INVALID_LANG": "❌ Opção inválida. Usando Português como padrão.",
        
        # Menu de Opções
        "MENU_HEADER": "📂 Slot Ativo: {slot}{status}",
        "MENU_NO_SAVE": "📂 Slot Ativo: Nenhum save carregado",
        "MENU_SAVE_TIME": "⏰ Horário do Save: {time}",
        "MENU_UNSAVED": " ⚠️ [ALTERAÇÕES NÃO SALVAS]",
        "OPT_1": "1. Escolher / Trocar Slot de Save (com Data e Horário)",
        "OPT_2": "2. 💰 Alterar Dinheiro & Recursos do Acampamento",
        "OPT_3": "3. Ver Inventário Completo (Paginação e Edição)",
        "OPT_4": "4. Buscar Item no Inventário Atual (ex: Abyss Artifact)",
        "OPT_5": "5. Pesquisar Banco de Dados Global (6.200+ itens)",
        "OPT_6": "6. Salvar alterações no save (com backup e anti-crash)",
        "OPT_7": "7. 🛡️ Restaurar Backup / Recuperar Save",
        "OPT_8": "8. Limpar manualmente 'steam_autocloud.vdf'",
        "OPT_0": "0. Sair",
        "CHOOSE_OPTION": "\nEscolha uma opção: ",
        
        # Slot Detection
        "SLOT_DETECTED": "\n💡 Slot mais recente detectado automaticamente:",
        "SLOT_INFO": "   👉 {label} (Gravado em: {time})",
        "LOAD_SLOT_NOW": "\nDeseja carregar este slot agora? (S/n/outros): ",
        
        # Save Loading
        "DECRYPTING": "\n⏳ Descriptografando e lendo save ({file})...",
        "SCANNING": "🔍 Escaneando itens do inventário...",
        "SAVE_LOADED": "✅ Save carregado com sucesso!",
        "SAVE_SLOT": "   • Slot: {slot}",
        "SAVE_TIME": "   • Data/Horário do Save: {time}",
        "HMAC_VALID": "   • Integridade HMAC: ✅ Válido",
        "HMAC_INVALID": "   • Integridade HMAC: ⚠️ Inconsistente (modificado previamente)",
        "ITEMS_COUNT": "   • Total de itens no inventário: {count}",
        "ERR_FILE_NOT_FOUND": "❌ Erro: O arquivo não foi encontrado: {path}",
        "ERR_LOAD_FAILED": "❌ Falha ao carregar o save: {error}",
        
        # Slot Selection
        "SLOTS_FOUND": "\n📂 Slots de Save Encontrados no seu Jogo:",
        "SLOT_RECENT": " ⭐ [Mais Recente]",
        "SLOT_FORMAT": "  [{idx}] {label:<28} | Horário: {time}{recent}",
        "OPT_MANUAL": "  [D] Digitar outro caminho manualmente",
        "OPT_CANCEL": "  [0] Cancelar / Voltar",
        "CHOOSE_SLOT": "\nEscolha o slot desejado (1 a {count}): ",
        "ENTER_PATH": "Cole ou digite o caminho completo do arquivo save.save: ",
        
        # Money Editing
        "NO_SAVE_LOADED": "⚠️ Nenhum save carregado. Selecione um slot primeiro.",
        "MONEY_HEADER": "\n💰 DINHEIRO E RECURSOS DO ACAMPAMENTO:",
        "NO_CURRENCIES": "⚠️ Nenhum registro de moeda/dinheiro encontrado neste save.",
        "MONEY_FORMAT": "  [{idx}] {name:<38} | Atual: {count:,}",
        "CHOOSE_CURRENCY": "\nEscolha qual deseja alterar (1 a {count} ou 0 para voltar): ",
        "ERR_INVALID_OPTION": "❌ Opção inválida.",
        "ALTERING": "\nAlterando: {name}",
        "CURRENT_AMOUNT": "Quantidade Atual: {count:,}",
        "ENTER_NEW_VALUE": "Digite o novo valor desejado (ex: 50000000 para 50 milhões): ",
        "ERR_INVALID_VALUE": "❌ Valor inválido.",
        "SUCCESS_CHANGE": "✅ {name} alterado de {old:,} para {new:,}!",
        
        # Inventory
        "NO_ITEMS": "Nenhum item encontrado no inventário.",
        "INVENTORY_HEADER": "\n📦 Inventário Completo (Página {page}/{total} - Itens {start} a {end}):",
        "ITEM_FORMAT": "  [{idx:3}] {item}",
        "NAV_COMMANDS": "Comandos: [N] Próxima pág | [P] Pág anterior | [Número do Item] Editar | [0] Voltar",
        "ENTER_OPTION": "\nDigite a opção desejada: ",
        "LAST_PAGE": "⚠️ Já está na última página.",
        "FIRST_PAGE": "⚠️ Já está na primeira página.",
        
        # Search
        "SEARCH_INVENTORY": "\n🔎 Digite o nome ou ID do item no inventário (ex: 'Abyss Artifact'): ",
        "NO_RESULTS": "❌ Nenhum item encontrado com o termo '{query}'.",
        "SEARCH_RESULTS": "\n📦 Resultados no Inventário ({count} encontrados):",
        "CHOOSE_ITEM": "\nDigite o número do item que deseja editar (ou 0 para cancelar): ",
        
        # Item Actions
        "EDITING_ITEM": "\n🎯 EDITANDO ITEM: {name}",
        "ITEM_CATEGORY": "     • Categoria: {category}",
        "ITEM_SLOT": "     • Slot no Inventário: {slot}",
        "ITEM_STACK": "     • Quantidade Atual: {count:,}",
        "ITEM_PRICE": "     • Preço Médio / Dinheiro (Average Price): {price:,}",
        "ITEM_ENCHANT": "     • Nível de Encanto: {enchant}",
        "ITEM_DURABILITY": "     • Durabilidade (Endurance): {durability}",
        "ITEM_SHARPNESS": "     • Afiação (Sharpness): {sharpness}",
        "ITEM_KEY": "     • ID Interno (Key): {key}",
        "ACTION_1": "  1. Alterar Quantidade (Stack Count)",
        "ACTION_2": "  2. Definir Nível de Encantamento (+0 até +20)",
        "ACTION_3": "  3. 🛠️ Reparar Equipamento (Durabilidade e Afiação Máximas)",
        "ACTION_4": "  4. Substituir / Trocar por outro Item do Banco de Dados",
        "ACTION_0": "  0. Concluir / Voltar",
        "CHOOSE_ACTION": "\nEscolha uma opção: ",
        
        # Stack Warning
        "STACK_WARNING": "\n⚠️ AVISO: Este item é um equipamento (Stack padrão = 1).",
        "STACK_OVERLAP": "   Colocar quantidade > 1 pode causar sobreposição visual no jogo.",
        "ENTER_NEW_STACK": "Digite a nova quantidade (atual: {count:,}): ",
        "ERR_INVALID_STACK": "❌ Quantidade inválida.",
        "CONFIRM_STACK": "Deseja realmente definir quantidade > 1 para este equipamento? (s/N): ",
        "SUCCESS_STACK": "✅ Quantidade alterada de {old:,} para {new:,}!",
        
        # Enchant
        "ENTER_ENCHANT": "Digite o nível de encanto (ex: 0 para normal, 10 para +10, 20 para +20): ",
        "ERR_INVALID_ENCHANT": "❌ Valor inválido.",
        "SUCCESS_ENCHANT": "✅ Encantamento alterado de +{old} para +{new}!",
        
        # Repair
        "SUCCESS_REPAIR": "🛠️ Equipamento reparado com sucesso! Durabilidade: {durability}, Afiação: {sharpness}",
        
        # Swap Item
        "SEARCH_NEW_ITEM": "\n🔎 Digite o nome do novo item para buscar no banco global (6.200+ itens): ",
        "NO_DB_RESULTS": "❌ Nenhum item encontrado no banco com o termo '{query}'.",
        "DB_RESULTS": "\n📚 Itens Encontrados no Banco Global ({count}):",
        "DB_ITEM_FORMAT": "  [{idx:2}] {name} (ID: {key}) [{cat}] - Stack Máx: {max}",
        "CHOOSE_NEW_ITEM": "\nDigite o número do item desejado para substituir o atual (ou 0 para cancelar): ",
        "CONFIRM_SWAP": "Confirma trocar '{old}' por '{new}'? (S/n): ",
        "SUCCESS_SWAP": "✅ Item '{old}' substituído com sucesso por '{new}'!",
        
        # Global Search
        "GLOBAL_SEARCH": "\n🔎 Pesquisar no Banco de Dados Global de Itens (ex: 'Sword', 'Plate', 'Artifact'): ",
        "GLOBAL_RESULTS": "\n📚 Resultados da Busca Global ({count} itens):",
        "GLOBAL_ITEM_FORMAT": "  [{idx:2}] {name} (ID: {key}) [{cat}] | Interno: {internal}",
        "PRESS_ENTER": "Pressione Enter para voltar ao menu...",
        
        # Save Changes
        "NO_CHANGES": "ℹ️ Nenhuma alteração foi feita neste save.",
        "CONFIRM_SAVE": "Deseja regravar mesmo assim? (s/N): ",
        "CREATING_BACKUP": "\n💾 1. Criando cópia de segurança automática (.bak)...",
        "BACKUP_SAVED": "   🛡️ Backup salvo em: {path}",
        "RECOMPACTING": "⏳ 2. Recompactando em LZ4 e recriptografando ChaCha20...",
        "SAVE_SUCCESS": "   ✅ Save gravado com integridade HMAC 100% válida!",
        "CHECKING_AUTOCLOUD": "🧹 3. Verificando 'steam_autocloud.vdf'...",
        "AUTOCLOUD_REMOVED": "   ✨ 'steam_autocloud.vdf' removido com sucesso! O jogo iniciará sem travar no menu.",
        "AUTOCLOUD_NOT_FOUND": "   ℹ️ 'steam_autocloud.vdf' já não estava presente.",
        "ALL_SAVED": "\n🎉 Todas as alterações foram salvas com sucesso! Pronto para jogar.",
        "ERR_SAVE_FAILED": "❌ Erro ao salvar arquivo: {error}",
        
        # Restore Backup
        "NO_BACKUPS": "❌ Nenhum backup encontrado na pasta 'backups' deste slot.",
        "BACKUP_HEADER": "\n🛡️ BACKUPS DISPONÍVEIS PARA RESTAURAÇÃO:",
        "BACKUP_RECENT": " ⭐ [Mais Recente]",
        "BACKUP_FORMAT": "  [{idx:2}] {time} ({size:.1f} KB){recent}",
        "BACKUP_FILE": "       Arquivo: {filename}",
        "CHOOSE_BACKUP": "\nEscolha o backup para restaurar (1 a {count} ou 0 para cancelar): ",
        "CONFIRM_RESTORE": "⚠️ ATENÇÃO: Confirma restaurar o backup de '{time}'? O save atual será substituído. (s/N): ",
        "RESTORE_CANCELLED": "Restauração cancelada.",
        "RESTORE_SUCCESS": "✅ Backup de {time} restaurado com sucesso!",
        "RELOADING": "⏳ Recarregando save na memória...",
        "ERR_RESTORE_FAILED": "❌ Erro ao restaurar backup: {error}",
        
        # Steam Autocloud Manual
        "AUTOCLOUD_MANUAL_SUCCESS": "✨ 'steam_autocloud.vdf' removido com sucesso!",
        "AUTOCLOUD_MANUAL_NOT_FOUND": "ℹ️ 'steam_autocloud.vdf' não encontrado (o diretório já está limpo).",
        
        # Exit
        "UNSAVED_CHANGES": "⚠️ Existem alterações não salvas. Deseja sair mesmo assim? (s/N): ",
        "GOODBYE": "\nAté logo e bom jogo em Crimson Desert! ⚔️\n",
    },
    
    "en": {
        # Main Menu
        "APP_TITLE": "⚔️  CRIMSON DESERT - ITEM SAVE EDITOR (Enhanced Edition) ⚔️",
        "CHOOSE_LANGUAGE": "Choose language / Escolha o idioma:",
        "LANG_PT": "Português",
        "LANG_EN": "English",
        "INVALID_LANG": "❌ Invalid option. Using Portuguese as default.",
        
        # Options Menu
        "MENU_HEADER": "📂 Active Slot: {slot}{status}",
        "MENU_NO_SAVE": "📂 Active Slot: No save loaded",
        "MENU_SAVE_TIME": "⏰ Save Time: {time}",
        "MENU_UNSAVED": " ⚠️ [UNSAVED CHANGES]",
        "OPT_1": "1. Choose / Change Save Slot (with Date and Time)",
        "OPT_2": "2. 💰 Change Money & Camp Funds",
        "OPT_3": "3. View Full Inventory (Pagination and Editing)",
        "OPT_4": "4. Search Item in Current Inventory (ex: Abyss Artifact)",
        "OPT_5": "5. Search Global Database (6,200+ items)",
        "OPT_6": "6. Save changes to save file (with backup and anti-crash)",
        "OPT_7": "7. 🛡️ Restore Backup / Recover Save",
        "OPT_8": "8. Manually clean 'steam_autocloud.vdf'",
        "OPT_0": "0. Exit",
        "CHOOSE_OPTION": "\nChoose an option: ",
        
        # Slot Detection
        "SLOT_DETECTED": "\n💡 Most recent slot automatically detected:",
        "SLOT_INFO": "   👉 {label} (Saved at: {time})",
        "LOAD_SLOT_NOW": "\nDo you want to load this slot now? (Y/n/others): ",
        
        # Save Loading
        "DECRYPTING": "\n⏳ Decrypting and reading save ({file})...",
        "SCANNING": "🔍 Scanning inventory items...",
        "SAVE_LOADED": "✅ Save loaded successfully!",
        "SAVE_SLOT": "   • Slot: {slot}",
        "SAVE_TIME": "   • Save Date/Time: {time}",
        "HMAC_VALID": "   • HMAC Integrity: ✅ Valid",
        "HMAC_INVALID": "   • HMAC Integrity: ⚠️ Inconsistent (previously modified)",
        "ITEMS_COUNT": "   • Total items in inventory: {count}",
        "ERR_FILE_NOT_FOUND": "❌ Error: File not found: {path}",
        "ERR_LOAD_FAILED": "❌ Failed to load save: {error}",
        
        # Slot Selection
        "SLOTS_FOUND": "\n📂 Save Slots Found in Your Game:",
        "SLOT_RECENT": " ⭐ [Most Recent]",
        "SLOT_FORMAT": "  [{idx}] {label:<28} | Time: {time}{recent}",
        "OPT_MANUAL": "  [D] Enter another path manually",
        "OPT_CANCEL": "  [0] Cancel / Back",
        "CHOOSE_SLOT": "\nChoose the desired slot (1 to {count}): ",
        "ENTER_PATH": "Paste or type the full path to the save.save file: ",
        
        # Money Editing
        "NO_SAVE_LOADED": "⚠️ No save loaded. Select a slot first.",
        "MONEY_HEADER": "\n💰 MONEY AND CAMP RESOURCES:",
        "NO_CURRENCIES": "⚠️ No currency/money records found in this save.",
        "MONEY_FORMAT": "  [{idx}] {name:<38} | Current: {count:,}",
        "CHOOSE_CURRENCY": "\nChoose which to change (1 to {count} or 0 to go back): ",
        "ERR_INVALID_OPTION": "❌ Invalid option.",
        "ALTERING": "\nChanging: {name}",
        "CURRENT_AMOUNT": "Current Amount: {count:,}",
        "ENTER_NEW_VALUE": "Enter the new desired value (ex: 50000000 for 50 million): ",
        "ERR_INVALID_VALUE": "❌ Invalid value.",
        "SUCCESS_CHANGE": "✅ {name} changed from {old:,} to {new:,}!",
        
        # Inventory
        "NO_ITEMS": "No items found in inventory.",
        "INVENTORY_HEADER": "\n📦 Full Inventory (Page {page}/{total} - Items {start} to {end}):",
        "ITEM_FORMAT": "  [{idx:3}] {item}",
        "NAV_COMMANDS": "Commands: [N] Next page | [P] Previous page | [Item Number] Edit | [0] Back",
        "ENTER_OPTION": "\nEnter desired option: ",
        "LAST_PAGE": "⚠️ Already on the last page.",
        "FIRST_PAGE": "⚠️ Already on the first page.",
        
        # Search
        "SEARCH_INVENTORY": "\n🔎 Enter the name or ID of the item in inventory (ex: 'Abyss Artifact'): ",
        "NO_RESULTS": "❌ No items found with the term '{query}'.",
        "SEARCH_RESULTS": "\n📦 Results in Inventory ({count} found):",
        "CHOOSE_ITEM": "\nEnter the number of the item you want to edit (or 0 to cancel): ",
        
        # Item Actions
        "EDITING_ITEM": "\n🎯 EDITING ITEM: {name}",
        "ITEM_CATEGORY": "     • Category: {category}",
        "ITEM_SLOT": "     • Inventory Slot: {slot}",
        "ITEM_STACK": "     • Current Quantity: {count:,}",
        "ITEM_PRICE": "     • Average Price / Money: {price:,}",
        "ITEM_ENCHANT": "     • Enchant Level: {enchant}",
        "ITEM_DURABILITY": "     • Durability (Endurance): {durability}",
        "ITEM_SHARPNESS": "     • Sharpness: {sharpness}",
        "ITEM_KEY": "     • Internal ID (Key): {key}",
        "ACTION_1": "  1. Change Quantity (Stack Count)",
        "ACTION_2": "  2. Set Enchantment Level (+0 to +20)",
        "ACTION_3": "  3. 🛠️ Repair Equipment (Max Durability and Sharpness)",
        "ACTION_4": "  4. Replace / Swap with another Item from Database",
        "ACTION_0": "  0. Finish / Back",
        "CHOOSE_ACTION": "\nChoose an option: ",
        
        # Stack Warning
        "STACK_WARNING": "\n⚠️ WARNING: This item is equipment (Default stack = 1).",
        "STACK_OVERLAP": "   Setting quantity > 1 may cause visual overlap in the game.",
        "ENTER_NEW_STACK": "Enter new quantity (current: {count:,}): ",
        "ERR_INVALID_STACK": "❌ Invalid quantity.",
        "CONFIRM_STACK": "Do you really want to set quantity > 1 for this equipment? (y/N): ",
        "SUCCESS_STACK": "✅ Quantity changed from {old:,} to {new:,}!",
        
        # Enchant
        "ENTER_ENCHANT": "Enter enchantment level (ex: 0 for normal, 10 for +10, 20 for +20): ",
        "ERR_INVALID_ENCHANT": "❌ Invalid value.",
        "SUCCESS_ENCHANT": "✅ Enchantment changed from +{old} to +{new}!",
        
        # Repair
        "SUCCESS_REPAIR": "🛠️ Equipment repaired successfully! Durability: {durability}, Sharpness: {sharpness}",
        
        # Swap Item
        "SEARCH_NEW_ITEM": "\n🔎 Enter the name of the new item to search in global database (6,200+ items): ",
        "NO_DB_RESULTS": "❌ No items found in database with the term '{query}'.",
        "DB_RESULTS": "\n📚 Items Found in Global Database ({count}):",
        "DB_ITEM_FORMAT": "  [{idx:2}] {name} (ID: {key}) [{cat}] - Max Stack: {max}",
        "CHOOSE_NEW_ITEM": "\nEnter the number of the desired item to replace the current one (or 0 to cancel): ",
        "CONFIRM_SWAP": "Confirm swap '{old}' for '{new}'? (Y/n): ",
        "SUCCESS_SWAP": "✅ Item '{old}' successfully replaced with '{new}'!",
        
        # Global Search
        "GLOBAL_SEARCH": "\n🔎 Search in Global Item Database (ex: 'Sword', 'Plate', 'Artifact'): ",
        "GLOBAL_RESULTS": "\n📚 Global Search Results ({count} items):",
        "GLOBAL_ITEM_FORMAT": "  [{idx:2}] {name} (ID: {key}) [{cat}] | Internal: {internal}",
        "PRESS_ENTER": "Press Enter to return to menu...",
        
        # Save Changes
        "NO_CHANGES": "ℹ️ No changes were made to this save.",
        "CONFIRM_SAVE": "Do you want to save anyway? (y/N): ",
        "CREATING_BACKUP": "\n💾 1. Creating automatic backup (.bak)...",
        "BACKUP_SAVED": "   🛡️ Backup saved at: {path}",
        "RECOMPACTING": "⏳ 2. Recompressing in LZ4 and re-encrypting with ChaCha20...",
        "SAVE_SUCCESS": "   ✅ Save written with 100% valid HMAC integrity!",
        "CHECKING_AUTOCLOUD": "🧹 3. Checking 'steam_autocloud.vdf'...",
        "AUTOCLOUD_REMOVED": "   ✨ 'steam_autocloud.vdf' removed successfully! Game will start without crashing on menu.",
        "AUTOCLOUD_NOT_FOUND": "   ℹ️ 'steam_autocloud.vdf' was not present.",
        "ALL_SAVED": "\n🎉 All changes saved successfully! Ready to play.",
        "ERR_SAVE_FAILED": "❌ Error saving file: {error}",
        
        # Restore Backup
        "NO_BACKUPS": "❌ No backups found in the 'backups' folder of this slot.",
        "BACKUP_HEADER": "\n🛡️ AVAILABLE BACKUPS FOR RESTORATION:",
        "BACKUP_RECENT": " ⭐ [Most Recent]",
        "BACKUP_FORMAT": "  [{idx:2}] {time} ({size:.1f} KB){recent}",
        "BACKUP_FILE": "       File: {filename}",
        "CHOOSE_BACKUP": "\nChoose backup to restore (1 to {count} or 0 to cancel): ",
        "CONFIRM_RESTORE": "⚠️ WARNING: Confirm restoring backup from '{time}'? Current save will be replaced. (Y/n): ",
        "RESTORE_CANCELLED": "Restoration cancelled.",
        "RESTORE_SUCCESS": "✅ Backup from {time} restored successfully!",
        "RELOADING": "⏳ Reloading save in memory...",
        "ERR_RESTORE_FAILED": "❌ Error restoring backup: {error}",
        
        # Steam Autocloud Manual
        "AUTOCLOUD_MANUAL_SUCCESS": "✨ 'steam_autocloud.vdf' removed successfully!",
        "AUTOCLOUD_MANUAL_NOT_FOUND": "ℹ️ 'steam_autocloud.vdf' not found (directory is already clean).",
        
        # Exit
        "UNSAVED_CHANGES": "⚠️ There are unsaved changes. Do you want to exit anyway? (y/N): ",
        "GOODBYE": "\nSee you later and enjoy Crimson Desert! ⚔️\n",
    }
}

# ==============================================================================
# ESTADO GLOBAL DO IDIOMA
# ==============================================================================
CURRENT_LANG = "pt"


def t(key: str) -> str:
    """
    Função de tradução (lookup).
    Retorna a string traduzida para o idioma atual.
    Se a chave não existir, retorna a própria chave como fallback.
    """
    lang_dict = LOCALES.get(CURRENT_LANG, LOCALES["pt"])
    return lang_dict.get(key, f"[MISSING: {key}]")


def set_language(lang_code: str) -> None:
    """Define o idioma atual."""
    global CURRENT_LANG
    if lang_code in LOCALES:
        CURRENT_LANG = lang_code


def get_available_languages() -> list:
    """Retorna lista de códigos de idiomas disponíveis."""
    return list(LOCALES.keys())