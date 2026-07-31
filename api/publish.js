import plan from "../content-plan.json" with { type: "json" };

const graphVersion = process.env.META_GRAPH_VERSION || "v23.0";

function jakartaDate() {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Jakarta",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${values.year}-${values.month}-${values.day}`;
}

async function graph(path, params = {}, method = "POST") {
  const body = new URLSearchParams(params);
  const response = await fetch(`https://graph.facebook.com/${graphVersion}/${path}`, {
    method,
    headers: method === "POST" ? { "content-type": "application/x-www-form-urlencoded" } : {},
    body: method === "POST" ? body : undefined,
  });
  const payload = await response.json();
  if (!response.ok || payload.error) {
    throw new Error(payload.error?.message || `Meta request failed with ${response.status}`);
  }
  return payload;
}

async function instagramAlreadyPublished(marker) {
  const id = process.env.INSTAGRAM_USER_ID;
  const token = process.env.META_ACCESS_TOKEN;
  const url = new URL(`https://graph.facebook.com/${graphVersion}/${id}/media`);
  url.searchParams.set("fields", "caption,timestamp");
  url.searchParams.set("limit", "50");
  url.searchParams.set("access_token", token);
  const response = await fetch(url);
  const payload = await response.json();
  return Array.isArray(payload.data) && payload.data.some((post) => post.caption?.includes(marker));
}

async function publishInstagram(item, imageUrl, caption, marker) {
  if (await instagramAlreadyPublished(marker)) return { status: "already_published" };
  const id = process.env.INSTAGRAM_USER_ID;
  const token = process.env.META_ACCESS_TOKEN;
  const container = await graph(`${id}/media`, {
    image_url: imageUrl,
    caption,
    access_token: token,
  });
  const published = await graph(`${id}/media_publish`, {
    creation_id: container.id,
    access_token: token,
  });
  return { status: "published", id: published.id };
}

async function facebookAlreadyPublished(marker) {
  const id = process.env.FACEBOOK_PAGE_ID;
  const token = process.env.META_ACCESS_TOKEN;
  const url = new URL(`https://graph.facebook.com/${graphVersion}/${id}/published_posts`);
  url.searchParams.set("fields", "message,created_time");
  url.searchParams.set("limit", "50");
  url.searchParams.set("access_token", token);
  const response = await fetch(url);
  const payload = await response.json();
  return Array.isArray(payload.data) && payload.data.some((post) => post.message?.includes(marker));
}

async function publishFacebook(item, imageUrl, caption, marker) {
  if (await facebookAlreadyPublished(marker)) return { status: "already_published" };
  const published = await graph(`${process.env.FACEBOOK_PAGE_ID}/photos`, {
    url: imageUrl,
    message: caption,
    published: "true",
    access_token: process.env.META_ACCESS_TOKEN,
  });
  return { status: "published", id: published.post_id || published.id };
}

async function publishTikTok(item, imageUrl, caption) {
  const response = await fetch("https://open.tiktokapis.com/v2/post/publish/content/init/", {
    method: "POST",
    headers: {
      authorization: `Bearer ${process.env.TIKTOK_ACCESS_TOKEN}`,
      "content-type": "application/json; charset=UTF-8",
    },
    body: JSON.stringify({
      post_info: {
        title: item.title.replaceAll("\n", " ").slice(0, 90),
        description: caption.slice(0, 4000),
        privacy_level: "PUBLIC_TO_EVERYONE",
        disable_comment: false,
        auto_add_music: true,
        brand_organic_toggle: true,
      },
      source_info: {
        source: "PULL_FROM_URL",
        photo_cover_index: 0,
        photo_images: [imageUrl],
      },
      post_mode: "DIRECT_POST",
      media_type: "PHOTO",
    }),
  });
  const payload = await response.json();
  if (!response.ok || payload.error?.code !== "ok") {
    throw new Error(payload.error?.message || `TikTok request failed with ${response.status}`);
  }
  return { status: "submitted", id: payload.data.publish_id };
}

function configuredChannels() {
  return (process.env.SOCIAL_CHANNELS || "")
    .split(",")
    .map((channel) => channel.trim().toLowerCase())
    .filter(Boolean);
}

function missingConfiguration(channel) {
  if (channel === "instagram") {
    return ["INSTAGRAM_USER_ID", "META_ACCESS_TOKEN"].filter((key) => !process.env[key]);
  }
  if (channel === "facebook") {
    return ["FACEBOOK_PAGE_ID", "META_ACCESS_TOKEN"].filter((key) => !process.env[key]);
  }
  if (channel === "tiktok") {
    return ["TIKTOK_ACCESS_TOKEN"].filter((key) => !process.env[key]);
  }
  return [`unsupported:${channel}`];
}

export default async function handler(req, res) {
  if (req.method !== "GET" && req.method !== "POST") {
    return res.status(405).json({ error: "method_not_allowed" });
  }
  if (process.env.CRON_SECRET) {
    const authorization = req.headers.authorization || "";
    if (authorization !== `Bearer ${process.env.CRON_SECRET}`) {
      return res.status(401).json({ error: "invalid_cron_secret" });
    }
  }

  const requestedDate = req.query.date || jakartaDate();
  const item = plan.find((entry) => entry.date === requestedDate);
  if (!item) return res.status(200).json({ status: "no_post_due", date: requestedDate });

  const channels = configuredChannels();
  if (!channels.length) {
    return res.status(200).json({
      status: "awaiting_account_connection",
      date: requestedDate,
      post: item.id,
    });
  }
  const missing = Object.fromEntries(
    channels
      .map((channel) => [channel, missingConfiguration(channel)])
      .filter(([, keys]) => keys.length),
  );
  if (Object.keys(missing).length) {
    return res.status(200).json({ status: "awaiting_account_connection", missing });
  }

  const origin = process.env.PUBLIC_ASSET_BASE_URL || `https://${req.headers.host}`;
  const imageUrl = `${origin}/${item.asset}`;
  const marker = `#Lajora30Hari${String(item.id).padStart(2, "0")}`;
  const caption = `${item.final_caption}\n${marker}`;
  const results = {};

  for (const channel of channels) {
    try {
      if (channel === "instagram") {
        results.instagram = await publishInstagram(item, imageUrl, caption, marker);
      } else if (channel === "facebook") {
        results.facebook = await publishFacebook(item, imageUrl, caption, marker);
      } else if (channel === "tiktok") {
        results.tiktok = await publishTikTok(item, imageUrl, caption);
      }
    } catch (error) {
      results[channel] = { status: "failed", error: error.message };
    }
  }

  const failed = Object.values(results).some((result) => result.status === "failed");
  return res.status(failed ? 502 : 200).json({
    status: failed ? "partial_failure" : "published",
    date: requestedDate,
    post: item.id,
    imageUrl,
    results,
  });
}
