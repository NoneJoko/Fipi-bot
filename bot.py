import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# 🔑 Вставь свои ключи
TELEGRAM_TOKEN = "8338060279:AAHciQs3L88SZDgasBDYzIEt416zO9sxsrk"
SPOONACULAR_KEY = "9bac1711bfa749ddaa4ca9675cc17e5a"

# ===== API Запросы =====

def search_recipes(ingredients):
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients,
        "number": 3,  # количество рецептов
        "ranking": 1,
        "apiKey": SPOONACULAR_KEY
    }
    r = requests.get(url, params=params)
    return r.json()

def get_recipe_info(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_KEY}
    r = requests.get(url, params=params)
    return r.json()

# ===== Хендлеры =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Напиши список продуктов через запятую, и я найду рецепты.")

async def find_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ingredients = update.message.text
    recipes = search_recipes(ingredients)

    if not recipes:
        await update.message.reply_text("😔 Ничего не нашёл, попробуй другие продукты.")
        return

    for recipe in recipes:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Подробнее", callback_data=str(recipe["id"]))]
        ])
        await update.message.reply_photo(
            photo=recipe["image"],
            caption=f"🍴 {recipe['title']}",
            reply_markup=keyboard
        )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    recipe_id = query.data
    info = get_recipe_info(recipe_id)

    ingredients = ", ".join([i["original"] for i in info["extendedIngredients"]])
    instructions = info.get("instructions", "🤷 Инструкции не найдены")

    text = (
        f"🍴 {info['title']}\n\n"
        f"🛒 Ингредиенты:\n{ingredients}\n\n"
        f"👩‍🍳 Приготовление:\n{instructions}"
    )

    await query.edit_message_caption(caption=text)

# ===== Запуск =====

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, find_recipes))
    app.add_handler(CallbackQueryHandler(button_click))

    print("🤖 Бот запущен...")
    app.run_polling()

if name == "main":
    main()
