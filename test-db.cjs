const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  try {
    const feedback = await prisma.courseFeedback.findMany({ take: 1 });
    console.log("Success reading courseFeedback:", feedback);
  } catch (e) {
    console.error("DB error:", e.message);
  }
}

main().finally(() => prisma.$disconnect());
