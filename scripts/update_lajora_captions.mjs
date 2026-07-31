#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const planPath = path.join(root, "content-plan.json");
const plan = JSON.parse(await fs.readFile(planPath, "utf8"));

const updates = {
  1: {
    pillar: "Craft",
    caption:
      "A brand can begin with one tactile detail. Material, rhythm, and restraint turn a familiar object into a recognisable world.",
    cta: "Which detail stays with you?",
    hashtags: "#ArtDirection #BrandDesign",
  },
  3: {
    pillar: "Attention",
    caption:
      "Scale earns attention, but character earns memory. This frame turns a city surface into a confident brand gesture.",
    cta: "Where does your eye land first?",
    hashtags: "#ArtDirection #VisualIdentity",
  },
  6: {
    pillar: "Distinctiveness",
    caption:
      "Recognition grows when one bold idea travels consistently across every touchpoint. The object changes; the attitude stays.",
    cta: "What would you keep?",
    hashtags: "#BrandDesign",
  },
  8: {
    pillar: "Memory",
    caption:
      "Visibility is only the first step. A clear visual code gives people something specific to recognise, remember, and return to.",
    cta: "Save this for your next visual review.",
    hashtags: "#VisualIdentity #BrandStrategy",
  },
  10: {
    pillar: "Distinctiveness",
    caption:
      "Distinctiveness does not need more noise. A focused brand system can stay quiet while every colour, shape, and interaction points to the same unmistakable character.",
    cta: "Which detail makes it recognisable?",
    hashtags: "#BrandDesign #VisualIdentity",
  },
  11: {
    pillar: "Experience",
    caption:
      "A good digital journey feels like choosing the right door without hesitation. Clear pathways, warm cues, and one confident destination can make a website feel genuinely welcoming.",
    cta: "Which path would you take?",
    hashtags: "#WebDesign #HospitalityDesign",
  },
  12: {
    pillar: "Experience",
    caption:
      "Hospitality begins before arrival. A thoughtful website system guides every choice toward one clear welcome, turning navigation into part of the guest experience.",
    cta: "Save this for your next guest-journey review.",
    hashtags: "#HospitalityDesign #WebDesign",
  },
  13: {
    pillar: "Distinctiveness",
    caption:
      "Positioning gives every brand decision somewhere to land. When the idea is clear, typography, service, and digital experience can all claim the same place.",
    cta: "What should your brand own?",
    hashtags: "#BrandStrategy #ArtDirection",
  },
  14: {
    pillar: "Personality",
    caption:
      "A brand voice should travel through colour, movement, service, and every digital touchpoint. The system works when different expressions still sound like the same character.",
    cta: "Where does the personality come through first?",
    hashtags: "#BrandDesign #CreativeDirection",
  },
  15: {
    pillar: "Process",
    caption:
      "The strongest website systems have personality beneath the surface. Structure creates clarity; layered colour, rhythm, and interaction give the experience its own voice.",
    cta: "Keep this close for the next concept round.",
    hashtags: "#WebDesign #BrandSystems",
  },
  16: {
    pillar: "Personality",
    caption:
      "Brand voice becomes visible through repeated choices: the pace of a website, the tone of a welcome, and the confidence of every small detail.",
    cta: "Which choice says the most?",
    hashtags: "#VisualIdentity #BrandVoice",
  },
  17: {
    pillar: "Experience",
    caption:
      "Good hospitality feels like an open threshold. The website, arrival, and service flow should guide people forward with the same sense of ease.",
    cta: "What makes an experience feel welcoming to you?",
    hashtags: "#HospitalityDesign #ExperienceDesign",
  },
  18: {
    pillar: "Consistency",
    caption:
      "Consistency is rhythm, not repetition. A clear website and payment flow can move through many moments while keeping the same familiar signals from entry to confirmation.",
    cta: "Save this for your next system review.",
    hashtags: "#DigitalExperience #BrandSystems",
  },
  19: {
    pillar: "Experience",
    caption:
      "Before people notice features, they feel the flow. Hospitality-led digital design removes friction so the website and payment experience can feel calm, clear, and considered.",
    cta: "Where would you simplify first?",
    hashtags: "#ExperienceDesign #WebDesign",
  },
  20: {
    pillar: "Consistency",
    caption:
      "A flexible brand system keeps one recognisable code across different poses. Website modules, service moments, and campaign expressions can change without losing the central idea.",
    cta: "Which expression feels strongest?",
    hashtags: "#BrandSystems #ArtDirection",
  },
  21: {
    pillar: "Craft",
    caption:
      "A website becomes memorable when its forms carry a voice. Modules, pathways, and interactions should feel designed from the same brand logic, not assembled from generic parts.",
    cta: "Which form would you repeat?",
    hashtags: "#WebDesign #VisualIdentity",
  },
  22: {
    pillar: "Consistency",
    caption:
      "Recognition comes from repeating the right code. One visual language can connect branding, website structure, hospitality touchpoints, and payment moments without making them identical.",
    cta: "Share this with a team building a coherent system.",
    hashtags: "#BrandSystems #CreativeDirection",
  },
  23: {
    pillar: "Experience",
    caption:
      "Payment should feel like a quiet gateway, not a dramatic interruption. One clear cue, one confident action, and the guest can keep moving through the experience.",
    cta: "What makes a payment flow feel trustworthy?",
    hashtags: "#PaymentExperience #ExperienceDesign",
  },
  24: {
    pillar: "Consistency",
    caption:
      "A payment gateway is strongest when many routes become one coherent system. Brand, website, and service need to meet at the same clear center.",
    cta: "Save this for your next journey-mapping session.",
    hashtags: "#PaymentGateway #BrandSystems",
  },
  25: {
    pillar: "Personality",
    caption:
      "Colour does more than decorate. Used consistently across branding, website states, and service cues, it becomes attitude people can recognise before they read a word.",
    cta: "Which colour carries the strongest personality?",
    hashtags: "#ColorDirection #BrandDesign",
  },
  26: {
    pillar: "Experience",
    caption:
      "Hospitality often lives in one small gesture. A warm cue at the right moment can make arrival, service, and payment feel personal rather than procedural.",
    cta: "Which small gesture do you remember?",
    hashtags: "#HospitalityDesign #ExperienceDesign",
  },
  27: {
    pillar: "Memory",
    caption:
      "People remember how a digital experience felt. Brand atmosphere, website flow, and hospitality details can work together to leave a softer, more human memory.",
    cta: "What feeling should your experience leave behind?",
    hashtags: "#BrandExperience #HospitalityDesign",
  },
  28: {
    pillar: "Craft",
    caption:
      "Trust can begin with one tiny signal: a clear confirmation, a familiar colour, or a payment detail placed exactly where people expect it.",
    cta: "Which detail builds confidence for you?",
    hashtags: "#PaymentExperience #DesignDetails",
  },
  29: {
    pillar: "Consistency",
    caption:
      "A clear website, payment flow, and brand system should align without feeling rigid. Shared structure creates confidence; expressive details keep the experience alive.",
    cta: "Where does your system need better alignment?",
    hashtags: "#WebDesign #BrandSystems",
  },
  30: {
    pillar: "Experience",
    caption:
      "The best branding is not only seen. It is felt through the welcome, the website journey, the payment moment, and every detail that holds the experience together.",
    cta: "Follow @lajora.brands for more visual thinking.",
    hashtags: "#BrandExperience #CreativeDirection",
  },
};

for (const item of plan) {
  const update = updates[item.id];
  if (!update) continue;
  Object.assign(item, update);
  item.final_caption = [update.caption, update.cta, update.hashtags]
    .filter(Boolean)
    .join("\n\n");
  if (item.id >= 10) {
    item.visual_revision = "hospitality_web_payment_branding_abstract_v2";
    item.asset_version = "service-system-v2-20260731";
    item.asset = `posts/editorial-system-v2-20260731/day-${String(item.id).padStart(2, "0")}.jpg`;
    item.public_asset_url = `PUBLIC_ASSET_BASE_URL/${item.asset}`;
  }
}

await fs.writeFile(planPath, `${JSON.stringify(plan, null, 2)}\n`);

const delivery = plan
  .map(
    (item) =>
      `POST ${String(item.id).padStart(2, "0")}\n` +
      `${item.date} — ${item.time_wib} WIB\n` +
      `${item.title}\n\n${item.final_caption}`,
  )
  .join("\n\n");
await fs.writeFile(
  path.join(root, "editorial-30-en", "CAPTION-SIAP-POSTING.txt"),
  `${delivery}\n`,
);

console.log(`Updated ${Object.keys(updates).length} captions; all 30 posts now have caption copy.`);
