#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const planPath = path.join(root, "content-plan.json");
const plan = JSON.parse(await fs.readFile(planPath, "utf8"));

const titles = [
  "Arrival Has a Color",
  "The First Signal",
  "Before the Door Opens",
  "Room for Wonder",
  "A Welcome in Form",
  "The Quiet Entrance",
  "Stay a Little Longer",
  "Threshold Language",
  "Courtyard After Light",
  "The View Begins Here",
  "Soft Geometry",
  "A Room Learns Your Rhythm",
  "The Key, Reimagined",
  "A Bedside Constellation",
  "Detail at Rest",
  "The Shape of Ease",
  "One Route, Many Moments",
  "The System Behind the Welcome",
  "The Page That Feels Like Place",
  "Navigation with Warmth",
  "A Clearer Way Through",
  "Flow Is a Feeling",
  "The Welcome in Motion",
  "Every Tap Has a Tone",
  "A Gateway with Grace",
  "The Quiet Confirmation",
  "Trust Has a Texture",
  "Payment, Made Human",
  "From Choice to Arrival",
  "A Journey That Holds",
  "The Center of Service",
  "One Signal, Many Hands",
  "The Shared Gateway",
  "A Better Kind of Seam",
  "The Room Remembers",
  "Service in the Details",
  "A Villa with a Point of View",
  "Architecture with a Voice",
  "Private, Not Invisible",
  "The Pool as a Pause",
  "A Landscape of Welcome",
  "The House Is the Brand",
  "Light Finds the Guest",
  "A Doorway to Belonging",
  "Color at Check-In",
  "The Brand You Can Walk Into",
  "A Little More Ease",
  "The Shape of Hospitality",
  "A Place to Return To",
  "Made for the Morning",
  "The Invisible Host",
  "Gesture Becomes Memory",
  "Small Things, Fully Considered",
  "The Care in the Curve",
  "A Signal Left On",
  "Service Has a Pulse",
  "The Space Between Moments",
  "The Good Kind of Familiar",
  "What Guests Carry With Them",
  "Memory Has a System",
  "One Living Language",
  "Every Touchpoint, One World",
  "Brand in the Background",
  "The Identity of Ease",
  "A System with Soul",
  "The Welcome, Repeated",
  "Designed to Stay",
  "More Than a Stay",
  "The Last Detail First",
  "An Atmosphere You Can Trust",
  "The Journey Keeps Opening",
  "Where the Flow Lands",
  "The House in the Hand",
  "One Key, Many Feelings",
  "A Better Arrival",
  "The Calm After Click",
  "The Light in the System",
  "Held by the Whole",
  "The Seamless Stay",
];

const chapters = [
  "Arrival Signals",
  "Rooms with a System",
  "The Digital Welcome",
  "The Trusted Gateway",
  "The Villa as a Brand",
  "Service as Memory",
  "One Living Identity",
  "The Stay Continues",
];

const pillars = [
  "Experience",
  "Distinctiveness",
  "Craft",
  "Consistency",
  "Personality",
  "Memory",
  "Process",
  "Attention",
];

const formats = [
  "image",
  "object",
  "image",
  "type",
  "image",
  "mixed",
  "image",
  "object",
  "image",
  "type",
];

const ctas = [
  "Which detail would you keep?",
  "Where does your eye land first?",
  "Save this for your next experience review.",
  "What would make the journey feel more human?",
  "Share this with someone designing a more thoughtful stay.",
  "Which signal would guests remember?",
  "What would you simplify first?",
  "Follow @lajora.brands for more visual thinking.",
];

const hashtags = [
  "#HospitalityDesign #BrandExperience",
  "#WebDesign #VisualIdentity",
  "#PaymentExperience #ExperienceDesign",
  "#VillaDesign #ArtDirection",
  "#BrandSystems #CreativeDirection",
  "#HotelDesign #HospitalityDesign",
];

function chapterFor(index) {
  if (index < 10) return chapters[0];
  if (index < 20) return chapters[1];
  if (index < 30) return chapters[2];
  if (index < 40) return chapters[3];
  if (index < 50) return chapters[4];
  if (index < 60) return chapters[5];
  if (index < 70) return chapters[6];
  return chapters[7];
}

function focusFor(index, chapter) {
  const focuses = {
    "Arrival Signals": [
      "arrival cues",
      "the first welcome",
      "thresholds",
      "guest anticipation",
      "warm wayfinding",
    ],
    "Rooms with a System": [
      "room rhythm",
      "tactile detail",
      "keys and thresholds",
      "quiet comfort",
      "the shape of ease",
    ],
    "The Digital Welcome": [
      "website pathways",
      "navigation",
      "clear choices",
      "digital atmosphere",
      "the moving guest journey",
    ],
    "The Trusted Gateway": [
      "payment moments",
      "confirmation",
      "trust signals",
      "frictionless movement",
      "secure hospitality",
    ],
    "The Villa as a Brand": [
      "villa character",
      "architectural voice",
      "privacy and presence",
      "landscape as identity",
      "a house guests remember",
    ],
    "Service as Memory": [
      "small gestures",
      "quiet care",
      "service rhythm",
      "familiar details",
      "the feeling guests carry",
    ],
    "One Living Identity": [
      "brand consistency",
      "one visual language",
      "touchpoint harmony",
      "identity in the background",
      "systems with soul",
    ],
    "The Stay Continues": [
      "the next welcome",
      "the flow after arrival",
      "a key with meaning",
      "calm interaction",
      "the complete experience",
    ],
  };
  return focuses[chapter][index % focuses[chapter].length];
}

function captionFor(index, title, chapter, pillar) {
  const focus = focusFor(index, chapter);
  const openings = [
    `A memorable stay starts with ${focus}.`,
    `${title} is a study in ${focus}.`,
    `The strongest hospitality systems make ${focus} feel effortless.`,
    `Good design gives ${focus} a clear emotional shape.`,
    `A guest may not name ${focus}, but they will feel it.`,
    `This chapter of The Seamless Stay looks at ${focus}.`,
    `The detail is small; the effect of ${focus} is not.`,
    `A thoughtful brand turns ${focus} into part of the welcome.`,
  ];
  const insights = [
    `Here, brand language moves through the hotel or villa, the website journey, and the payment gateway as one connected world.`,
    `The visual system uses portals, pathways, modular forms, and warm signals instead of literal interface diagrams.`,
    `The aim is a journey that feels clear enough to trust and distinctive enough to remember.`,
    `When service, space, and digital touchpoints share the same tone, consistency starts to feel like care.`,
    `A single visual code can make arrival, choice, confirmation, and return feel like parts of one experience.`,
    `The composition keeps the technology abstract so the human feeling stays in front.`,
    `This is where hospitality becomes a brand behaviour rather than a decorative layer.`,
    `The result is a system guests can move through without losing the sense of place.`,
  ];
  return `${openings[index % openings.length]} ${insights[(index * 3) % insights.length]}\n\n${ctas[index % ctas.length]}\n\n${hashtags[index % hashtags.length]}`;
}

const existing = plan.filter((item) => Number(item.id) <= 30);
const start = new Date("2026-08-22T00:00:00Z");
const added = titles.map((title, index) => {
  const id = 31 + index;
  const day = new Date(start);
  day.setUTCDate(day.getUTCDate() + index);
  const date = day.toISOString().slice(0, 10);
  const chapter = chapterFor(index);
  const format = formats[index % formats.length];
  return {
    id,
    date,
    time_wib: "09:00",
    timezone: "Asia/Jakarta",
    status: "queued_auto",
    approval_required: false,
    format,
    pillar: pillars[index % pillars.length],
    title,
    subtitle: chapter,
    caption: captionFor(index, title, chapter, pillars[index % pillars.length]),
    cta: ctas[index % ctas.length],
    hashtags: hashtags[index % hashtags.length],
    diagram: "the_seamless_stay",
    steps: [],
    asset: `posts/the-seamless-stay-100d/day-${String(id).padStart(3, "0")}.jpg`,
    public_asset_url: `PUBLIC_ASSET_BASE_URL/posts/the-seamless-stay-100d/day-${String(id).padStart(3, "0")}.jpg`,
    final_caption: captionFor(index, title, chapter, pillars[index % pillars.length]),
    contains_text: format === "type" || format === "mixed",
    language: "en",
    campaign_theme: "The Seamless Stay",
    chapter,
    visual_revision: "the_seamless_stay_100d_v1",
    asset_version: "the-seamless-stay-100d-v1",
  };
});

if (added.length !== 79) throw new Error(`Expected 79 new posts, got ${added.length}`);
const nextPlan = [...existing, ...added];
await fs.writeFile(planPath, `${JSON.stringify(nextPlan, null, 2)}\n`);

const captionFile = nextPlan
  .filter((item) => item.id >= 31)
  .map(
    (item) =>
      `POST ${String(item.id).padStart(3, "0")}\n` +
      `${item.date} — ${item.time_wib} WIB\n` +
      `${item.title}\n${item.chapter}\n\n${item.final_caption}`,
  )
  .join("\n\n");
await fs.writeFile(
  path.join(root, "editorial-30-en", "CAPTION-SEAMLESS-STAY-31-109.txt"),
  `${captionFile}\n`,
);

console.log(`Extended campaign to ${nextPlan.length} posts; added ${added.length} daily posts through ${added.at(-1).date}.`);
