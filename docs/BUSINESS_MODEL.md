# PetOrbit — Business Model

## Value Proposition

> "Upload a short video of your pet → get an interactive 180° orbit that follows your mouse or phone tilt."

PetOrbit turns a universal emotional hook (pet owners love showing off their pets) into a shareable, high-novelty creation. The "magic moment" is free to experience; the high-quality creation is paid.

---

## Target Audience

| Segment | Description | Willingness to Pay |
|---|---|---|
| Pet parents (primary) | Dog/cat owners who post pet content on social | Medium–High |
| Pet KOLs | Instagram/TikTok pet accounts with 1K–500K followers | High |
| Pet brands | Shops, groomers wanting branded pet content | High |

---

## Pricing Model: Pay-per-Creation

No subscription. Users buy **credit packs** (consumable IAP) and spend 1 credit per HD generation.

### Credit Packs (Consumable IAP)

| Pack | Credits | Price | Per credit |
|---|---|---|---|
| Starter | 3 | $4.99 | $1.66 |
| Value | 10 | $12.99 | $1.30 |
| Creator | 30 | $29.99 | $1.00 |

### One-time Upgrades (Non-consumable IAP)

| Feature | Price | Description |
|---|---|---|
| HD Unlock | $2.99 | Permanent HD output + no watermark |
| Video Export | $3.99 | MP4/GIF orbit export for social media |
| Bundle | $5.99 | HD + Video Export together |

### Free Tier
- 1 free generation on signup (low-res, watermarked)
- Web viewer always free to use (shareable link)

---

## Unit Economics (Estimate)

```
Revenue per generation (Starter pack):  $1.66
GPU cost per generation (A10G ~60s):    ~$0.08–$0.15
CDN / storage:                           ~$0.02
App store cut (30%):                     ~$0.50
---
Net margin per generation:               ~$1.00
```

At 500 generations/day: ~$500/day gross → ~$15,000/month gross.
Break-even at approximately 300–400 generations/day given infra + team costs.

---

## Growth Strategy

### Viral Loop
1. User creates orbit → shares Web viewer link.
2. Friends open link → see the interactive pet → want to make their own.
3. Built-in "Powered by PetOrbit" badge + CTA on viewer.

### Content Marketing
- Seed with KOLs (free Creator Packs) to generate showcase content.
- Target #dogsofinstagram, #petsoftiktok communities.
- Demo video: creator's phone tilting, dog head following — naturally shareable.

### Platform
- Launch on iOS first (higher IAP conversion).
- Android 2–3 months later.
- Web as acquisition / sharing channel (not primary creation UX).

---

## Roadmap

### MVP (Month 1–3)
- iOS app: guided capture + upload + credit IAP + result viewer
- Backend: FastAPI + Redis + MockClient → swap to Higgsfield Angles API
- Web viewer v1

### V1.1 (Month 4–5)
- Quality gating: auto-retry on poor NVS output
- Orbit video MP4 export
- Referral credits (invite a friend → +1 free credit)

### V2 (Month 6–9)
- Android
- Themed overlays (holiday hats, name tags)
- Cat support + other pets
- Bulk generation for pet brands
- Evaluate: subscription tier for power users (10 credits/month)
