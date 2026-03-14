require("dotenv/config");
const { Telegraf } = require("telegraf");

const token = process.env.BOT_TOKEN;
console.log("Token present:", !!token);
console.log("Token starts with:", token ? token.substring(0, 15) : "MISSING");

const bot = new Telegraf(token);

bot.start((ctx) => {
  console.log("Received /start from:", ctx.from.first_name);
  ctx.reply("Teste OK! Bot funcionando.");
});

bot.on("text", (ctx) => {
  console.log("Received text:", ctx.message.text, "from:", ctx.from.first_name);
  ctx.reply("Recebi: " + ctx.message.text);
});

bot.launch()
  .then(() => {
    console.log("=== BOT ONLINE E FUNCIONANDO ===");
  })
  .catch((err) => {
    console.error("=== ERRO AO INICIAR ===");
    console.error(err.message);
    console.error(err.stack);
  });

process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));
