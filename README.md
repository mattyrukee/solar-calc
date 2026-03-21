# Solar System Sizing Calculator — Nigeria

A free, instant solar system sizing calculator designed specifically for Nigerian residential homes. Calculate the right battery bank, inverter, and solar panel requirements based on your actual appliances and daily usage.

## Features

- **70+ Appliance Database**: Pre-configured Nigerian household appliances across 7 categories — Lighting, Cooling, Kitchen, Laundry, Entertainment, Water & Pumps, and Utilities
- **Smart Auto-Voltage**: System voltage is automatically selected based on your total daily energy (12V for ≤1.5kWh, 24V for ≤4kWh, 48V above)
- **Battery Sizing**: Recommends battery bank capacity (kWh and Ah) rounded up to standard sizes, with a detailed breakdown of batteries needed
- **Inverter Sizing**: Recommends inverter capacity (kVA) based on peak load, rounded up to the next standard inverter size
- **Solar Panel Sizing**: Calculates total solar wattage required, with 9 panel size options (250W–650W) you can tap to compare
- **Oversizing Toggle**: Optional 1.2x buffer (enabled by default) applied to battery, inverter, and panel calculations
- **Voltage Badges**: Both battery and inverter result cards display the system voltage
- **Appliance Breakdown**: Sorted table showing each appliance's load, daily energy consumption, and percentage share with visual bars
- **WhatsApp Contact**: Direct link to chat for pricing, availability, and installation
- **Responsive Design**: Full mobile support with adapted layouts for screens under 620px
- **Animated Transitions**: Smooth page transitions between the calculator and results pages

## How to Use

1. Click **"Add appliance"** to open the dropdown
2. Browse by category (Lighting, Cooling, Kitchen, etc.) or search by name
3. Tap an appliance to add it — tap again to remove
4. Adjust **Quantity** and **Hours/Day** for each appliance in the table
5. Toggle the **Oversizing** switch if you want to add/remove the 20% buffer
6. Click **"Calculate My Solar System"**
7. Review your results — battery bank, inverter, and solar panels
8. Tap different **panel size options** (250W–650W) to compare configurations
9. Click **"Edit appliances"** or **"Recalculate"** to go back and adjust

## Appliance Categories

| Category | Examples |
|----------|----------|
| Lighting | LED bulbs, CFL bulbs, tube lights, floodlights, security lights |
| Cooling | Ceiling/standing/table fans, air conditioners (1–3 HP) |
| Kitchen | Refrigerators, deep freezers, microwaves, kettles, cookers, blenders |
| Laundry | Washing machines, tumble dryers, pressing irons |
| Entertainment | TVs (24"–65"), decoders, sound systems, laptops, desktops, phone chargers |
| Water & Pumps | Pumping machines, borehole pumps, water heaters |
| Utilities | Security cameras, CCTV DVR, Wi-Fi routers, hair dryers, vacuum cleaners |

## System Assumptions

| Parameter | Value |
|-----------|-------|
| Peak sun hours | 4 hours (Nigerian average) |
| Oversizing factor | 1.2x (toggleable) |
| Auto-voltage thresholds | ≤1,500 Wh → 12V, ≤4,000 Wh → 24V, >4,000 Wh → 48V |
| Standard battery sizes | 1.8, 2.5, 3.8, 5, 7.5, 10, 15, 20, 25, 30, 40, 50 kWh |
| Standard inverter sizes | 1.8, 3.6, 4, 6, 10, 12 kVA |
| Panel size options | 250, 300, 350, 400, 450, 500, 550, 600, 650 W |

## Project Structure

```
solar-calc/
├── index.html    — Page structure and markup
├── styles.css    — All styles, animations, and responsive breakpoints
├── script.js     — Appliance database, calculations, and UI logic
└── README.md
```

## Technologies

- Vanilla HTML, CSS, and JavaScript — no frameworks or build tools
- Google Fonts: [Outfit](https://fonts.google.com/specimen/Outfit) (UI text) and [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) (data/mono elements)
- No external dependencies beyond fonts

## Deployment

Deploy to any static hosting service:

- GitHub Pages
- Netlify
- Vercel
- Any web server or CDN

Upload all three files (`index.html`, `styles.css`, `script.js`) to your hosting provider. No build step needed.

## License

Free to use and modify.
