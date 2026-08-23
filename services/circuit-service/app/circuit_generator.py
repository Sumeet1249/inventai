"""
Circuit Generator
─────────────────
Reads the CAD spec (component_type, span_mm, motor_count, etc.) and produces:
  1. A structured Circuit Spec JSON  (power rails, components, nets)
  2. An SVG schematic diagram        (rendered deterministically — no LLM needed)
  3. A component BOM list
  4. A power analysis table

Architecture (from ChatGPT doc):
  CAD Spec
      ↓
  Electronics Agent  ← OpenAI extracts electrical requirements
      ↓
  Circuit Spec JSON  ← structured: rails, components, nets
      ↓
  Circuit Generator  ← deterministic Python → SVG schematic
      ↓
  SVG + BOM + Power Analysis

Component database (subset — real specs):
  Drone / UAV domain: ESC, FC, BEC, battery, receiver, GPS, telemetry, MCU
"""

from __future__ import annotations
import math
import os
import json
import logging
import httpx
import asyncio
from typing import Any

logger = logging.getLogger(__name__)

# ── Component database ────────────────────────────────────────────────────────

COMPONENT_DB = {
    # drone_frame / fpv_racing_frame components
    "drone_frame": [
        {"ref": "U1",  "name": "Pixhawk 6C",      "type": "flight_controller", "voltage": "5V",  "current_ma": 500,  "package": "Board 38×38mm"},
        {"ref": "U2",  "name": "ESC 4-in-1 35A",  "type": "esc",              "voltage": "3S-6S","current_ma": 35000,"package": "Board 30×30mm"},
        {"ref": "U3",  "name": "BEC 5V/3A",       "type": "bec",              "voltage": "5V",   "current_ma": 3000, "package": "Module"},
        {"ref": "BT1", "name": "4S LiPo 5000mAh", "type": "battery",          "voltage": "14.8V","current_ma": 50000,"package": "Pack"},
        {"ref": "U4",  "name": "FrSky R-XSR",     "type": "receiver",         "voltage": "3.3V-5V","current_ma": 100,"package": "Module"},
        {"ref": "U5",  "name": "GPS M9N",          "type": "gps",             "voltage": "3.3V", "current_ma": 25,   "package": "Module 25×25mm"},
        {"ref": "U6",  "name": "SiK Telemetry 433MHz","type": "telemetry",    "voltage": "5V",   "current_ma": 400,  "package": "Module"},
        {"ref": "M1-M4","name":"BLHeli32 Motor",   "type": "motor",           "voltage": "14.8V","current_ma": 20000,"package": "2207 Stator"},
    ],
    "fpv_racing_frame": [
        {"ref": "U1",  "name": "F7 Flight Controller","type": "flight_controller","voltage": "5V", "current_ma": 300,  "package": "20×20mm Stack"},
        {"ref": "U2",  "name": "ESC 4-in-1 45A",   "type": "esc",             "voltage": "3S-4S","current_ma": 45000,"package": "20×20mm Stack"},
        {"ref": "BT1", "name": "4S LiPo 1500mAh",  "type": "battery",         "voltage": "14.8V","current_ma": 40000,"package": "Pack"},
        {"ref": "U3",  "name": "FPV Camera",        "type": "camera",          "voltage": "5V",   "current_ma": 220,  "package": "19×19mm"},
        {"ref": "U4",  "name": "VTX 5.8GHz 800mW", "type": "vtx",             "voltage": "5V",   "current_ma": 600,  "package": "Module"},
        {"ref": "U5",  "name": "FrSky XM+",        "type": "receiver",        "voltage": "5V",   "current_ma": 80,   "package": "Module"},
        {"ref": "M1-M4","name":"2207 2450KV Motor", "type": "motor",           "voltage": "14.8V","current_ma": 25000,"package": "2207 Stator"},
    ],
    "enclosure": [
        {"ref": "U1",  "name": "ESP32-S3",         "type": "mcu",             "voltage": "3.3V", "current_ma": 240,  "package": "QFN-56"},
        {"ref": "U2",  "name": "BME280",           "type": "sensor",          "voltage": "3.3V", "current_ma": 3,    "package": "LGA-8"},
        {"ref": "U3",  "name": "AMS1117-3.3",      "type": "ldo",             "voltage": "3.3V", "current_ma": 800,  "package": "SOT-223"},
        {"ref": "BT1", "name": "Li-Ion 18650",     "type": "battery",         "voltage": "3.7V", "current_ma": 3000, "package": "Cylindrical"},
        {"ref": "U4",  "name": "TP4056",           "type": "charger",         "voltage": "5V",   "current_ma": 1000, "package": "SOP-8"},
        {"ref": "J1",  "name": "USB-C Connector",  "type": "connector",       "voltage": "5V",   "current_ma": 1000, "package": "SMD"},
        {"ref": "R1",  "name": "10kΩ Pull-up",     "type": "resistor",        "voltage": "",     "current_ma": 0,    "package": "0402"},
        {"ref": "C1",  "name": "100µF Bulk Cap",   "type": "capacitor",       "voltage": "10V",  "current_ma": 0,    "package": "0805"},
    ],
    "payload_bay": [
        {"ref": "U1",  "name": "STM32F4",          "type": "mcu",             "voltage": "3.3V", "current_ma": 168,  "package": "LQFP-100"},
        {"ref": "U2",  "name": "Servo Driver PCA9685","type": "servo_driver", "voltage": "3.3V", "current_ma": 10,   "package": "SSOP-28"},
        {"ref": "U3",  "name": "5V BEC",           "type": "bec",             "voltage": "5V",   "current_ma": 3000, "package": "Module"},
        {"ref": "M1",  "name": "SG90 Micro Servo", "type": "servo",           "voltage": "5V",   "current_ma": 500,  "package": "Servo"},
        {"ref": "U4",  "name": "CAN Bus SN65HVD230","type": "can_transceiver","voltage": "3.3V", "current_ma": 10,   "package": "SO-8"},
    ],
    "landing_gear": [
        {"ref": "U1",  "name": "ATmega328P",       "type": "mcu",             "voltage": "5V",   "current_ma": 40,   "package": "DIP-28"},
        {"ref": "M1-M4","name":"DS3218 Servo",      "type": "servo",           "voltage": "6V",   "current_ma": 1500, "package": "Servo"},
        {"ref": "U2",  "name": "L298N H-Bridge",   "type": "motor_driver",    "voltage": "5-35V","current_ma": 2000, "package": "Module"},
        {"ref": "R1",  "name": "Current Sense 0.1Ω","type":"resistor",        "voltage": "",     "current_ma": 0,    "package": "2512"},
    ],
    "default": [
        {"ref": "U1",  "name": "STM32F4",          "type": "mcu",             "voltage": "3.3V", "current_ma": 168,  "package": "LQFP-100"},
        {"ref": "U2",  "name": "3.3V LDO",         "type": "ldo",             "voltage": "3.3V", "current_ma": 500,  "package": "SOT-223"},
        {"ref": "U3",  "name": "5V Buck Converter", "type": "buck",           "voltage": "5V",   "current_ma": 2000, "package": "Module"},
        {"ref": "BT1", "name": "LiPo Battery",     "type": "battery",         "voltage": "11.1V","current_ma": 10000,"package": "Pack"},
        {"ref": "J1",  "name": "XT60 Connector",   "type": "connector",       "voltage": "",     "current_ma": 0,    "package": "XT60"},
    ],
}

# Power rails by component type
POWER_RAILS = {
    "drone_frame":      ["VBAT (14.8V)", "5V Rail (BEC)", "3.3V Rail"],
    "fpv_racing_frame": ["VBAT (14.8V)", "5V Rail (BEC)"],
    "enclosure":        ["VUSB (5V)", "3.3V Rail (LDO)"],
    "payload_bay":      ["VBAT (12V)", "5V Rail", "3.3V Rail"],
    "landing_gear":     ["6V Rail", "5V Logic"],
    "default":          ["VBAT", "5V Rail", "3.3V Rail"],
}


# ── Electronics Agent (OpenAI) ────────────────────────────────────────────────

async def _electronics_agent(cad_spec: dict) -> dict:
    """
    Use OpenAI to extract additional electrical requirements from the CAD spec.
    Falls back to deterministic rules if OpenAI unavailable.
    """
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    ctype      = cad_spec.get("component_type", "default")
    span       = cad_spec.get("span_mm", 300)
    motors     = cad_spec.get("motor_count", 4)

    if openai_key and not openai_key.startswith("sk-your"):
        try:
            prompt = f"""You are an electronics engineer specialising in drones and UAV electronics.
Given this mechanical CAD spec, produce an electronics circuit specification as JSON.

CAD Spec:
{json.dumps({k: v for k, v in cad_spec.items() if not k.startswith("_")}, indent=2)}

Return ONLY valid JSON with these fields:
{{
  "power_input_v": float,       // main battery voltage
  "motor_count": int,
  "total_current_a": float,     // estimated peak draw
  "flight_time_min": int,       // estimated flight time
  "mcu": string,                // recommended flight controller / MCU
  "communication": [string],    // e.g. ["UART", "I2C", "SPI", "CAN"]
  "sensors": [string],          // e.g. ["IMU", "GPS", "Barometer"]
  "protection": [string],       // e.g. ["Reverse polarity", "Overcurrent"]
  "notes": string
}}"""

            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}",
                             "Content-Type": "application/json"},
                    json={
                        "model": "gpt-4o-mini",
                        "temperature": 0,
                        "response_format": {"type": "json_object"},
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                r.raise_for_status()
                content = r.json()["choices"][0]["message"]["content"]
                result = json.loads(content)
                logger.info("Electronics agent (OpenAI) produced spec: %s", result)
                return result
        except Exception as exc:
            logger.warning("Electronics agent OpenAI failed: %s — using rules", exc)

    # Deterministic fallback
    v_map    = {"drone_frame": 14.8, "fpv_racing_frame": 14.8,
                "enclosure": 3.7, "payload_bay": 11.1, "default": 11.1}
    curr_map = {"drone_frame": motors * 25, "fpv_racing_frame": motors * 30,
                "enclosure": 1.5, "payload_bay": 10, "default": 8}
    return {
        "power_input_v":  v_map.get(ctype, 11.1),
        "motor_count":    motors,
        "total_current_a": curr_map.get(ctype, 8),
        "flight_time_min": max(5, int(5000 / max(1, curr_map.get(ctype, 8)) / 60 * 60)),
        "mcu":            "Pixhawk 6C" if "drone" in ctype else "STM32F4",
        "communication":  ["UART", "I2C", "SPI"],
        "sensors":        ["IMU (ICM42688)", "Barometer (BMP388)", "GPS (U-blox M9N)"],
        "protection":     ["Reverse polarity diode", "Fuse 60A"],
        "notes":          f"Auto-generated for {ctype} {span}mm",
    }


# ── SVG Schematic Renderer ────────────────────────────────────────────────────

def _render_svg(components: list[dict], rails: list[str], elec_spec: dict) -> str:
    """
    Renders a clean block-diagram style SVG schematic.
    Layout: power rail at top → components in rows → ground at bottom.
    """
    W, H = 900, 700
    pad  = 40
    col_w = 160
    row_h = 90

    # Group components by type for layout
    type_order = ["battery", "bec", "ldo", "buck", "charger",
                  "flight_controller", "mcu", "esc", "motor_driver",
                  "motor", "servo", "servo_driver",
                  "receiver", "gps", "telemetry", "vtx", "camera",
                  "sensor", "can_transceiver",
                  "connector", "resistor", "capacitor"]

    sorted_comps = sorted(
        components,
        key=lambda c: type_order.index(c["type"]) if c["type"] in type_order else 99
    )

    cols = 5
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'style="font-family:Inter,Arial,sans-serif;background:#0F172A;">',
        # Background
        f'<rect width="{W}" height="{H}" fill="#0F172A"/>',
        # Title
        f'<text x="{W//2}" y="28" text-anchor="middle" fill="#F1F5F9" '
        f'font-size="15" font-weight="700">Circuit Schematic</text>',
    ]

    # Power rails bar
    rail_colors = ["#EF4444", "#F97316", "#22C55E", "#3B82F6", "#8B5CF6"]
    rail_y = 55
    rail_slot_w = (W - pad * 2) / max(len(rails), 1)
    for ri, rail in enumerate(rails):
        rx = pad + ri * rail_slot_w
        svg_parts.append(
            f'<rect x="{rx:.0f}" y="{rail_y}" width="{rail_slot_w - 8:.0f}" '
            f'height="28" rx="6" fill="{rail_colors[ri % len(rail_colors)]}" opacity="0.9"/>'
        )
        svg_parts.append(
            f'<text x="{rx + (rail_slot_w - 8) / 2:.0f}" y="{rail_y + 18}" '
            f'text-anchor="middle" fill="white" font-size="11" font-weight="700">'
            f'{rail}</text>'
        )

    # Component boxes
    comp_start_y = rail_y + 56
    COLORS = {
        "battery": "#EF4444", "bec": "#F97316", "ldo": "#F97316", "buck": "#F97316",
        "flight_controller": "#3B82F6", "mcu": "#3B82F6",
        "esc": "#8B5CF6", "motor_driver": "#8B5CF6",
        "motor": "#EC4899", "servo": "#EC4899",
        "receiver": "#10B981", "gps": "#10B981", "telemetry": "#10B981",
        "vtx": "#06B6D4", "camera": "#06B6D4",
        "sensor": "#A3E635", "charger": "#F59E0B",
        "connector": "#94A3B8", "resistor": "#94A3B8", "capacitor": "#94A3B8",
        "can_transceiver": "#F59E0B", "servo_driver": "#A78BFA",
    }

    drawn_wires = []

    for idx, comp in enumerate(sorted_comps):
        col = idx % cols
        row = idx // cols
        cx  = pad + col * ((W - pad * 2) / cols)
        cy  = comp_start_y + row * row_h
        bw, bh = col_w - 10, row_h - 16
        color = COLORS.get(comp["type"], "#64748B")

        # Box
        svg_parts.append(
            f'<rect x="{cx:.0f}" y="{cy:.0f}" width="{bw}" height="{bh}" '
            f'rx="8" fill="{color}" opacity="0.15" stroke="{color}" stroke-width="1.5"/>'
        )
        # Ref label
        svg_parts.append(
            f'<text x="{cx + bw/2:.0f}" y="{cy + 16:.0f}" text-anchor="middle" '
            f'fill="{color}" font-size="10" font-weight="700">{comp["ref"]}</text>'
        )
        # Name
        name_short = comp["name"][:18]
        svg_parts.append(
            f'<text x="{cx + bw/2:.0f}" y="{cy + 30:.0f}" text-anchor="middle" '
            f'fill="#F1F5F9" font-size="9.5">{name_short}</text>'
        )
        # Voltage badge
        if comp.get("voltage"):
            svg_parts.append(
                f'<text x="{cx + bw/2:.0f}" y="{cy + 44:.0f}" text-anchor="middle" '
                f'fill="{color}" font-size="9" opacity="0.9">{comp["voltage"]}</text>'
            )
        # Current badge
        if comp.get("current_ma", 0) > 0:
            cur = comp["current_ma"]
            cur_str = f"{cur/1000:.1f}A" if cur >= 1000 else f"{cur}mA"
            svg_parts.append(
                f'<text x="{cx + bw/2:.0f}" y="{cy + 57:.0f}" text-anchor="middle" '
                f'fill="#94A3B8" font-size="8.5">{cur_str}</text>'
            )

        # Wire from rail to first row components
        if row == 0 and comp["type"] in ("battery", "bec", "ldo", "buck", "mcu",
                                          "flight_controller", "esc"):
            wire_x = cx + bw / 2
            svg_parts.append(
                f'<line x1="{wire_x:.0f}" y1="{rail_y + 28}" '
                f'x2="{wire_x:.0f}" y2="{cy:.0f}" '
                f'stroke="{color}" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.6"/>'
            )

    # Ground rail at bottom
    last_row  = (len(sorted_comps) - 1) // cols
    gnd_y     = comp_start_y + (last_row + 1) * row_h + 8
    if gnd_y < H - 40:
        svg_parts.append(
            f'<rect x="{pad}" y="{gnd_y}" width="{W - pad*2}" height="22" '
            f'rx="4" fill="#1E293B" stroke="#334155" stroke-width="1"/>'
        )
        svg_parts.append(
            f'<text x="{W//2}" y="{gnd_y + 15}" text-anchor="middle" '
            f'fill="#64748B" font-size="11" font-weight="600">GND ⏚</text>'
        )

    # Power stats footer
    stats_y = H - 48
    svg_parts.append(
        f'<rect x="{pad}" y="{stats_y}" width="{W - pad*2}" height="36" '
        f'rx="8" fill="#1E293B" stroke="#334155" stroke-width="1"/>'
    )
    stats_text = (
        f'Battery: {elec_spec.get("power_input_v", "?")}V  │  '
        f'Peak Draw: {elec_spec.get("total_current_a", "?")}A  │  '
        f'Est. Flight: {elec_spec.get("flight_time_min", "?")} min  │  '
        f'MCU: {elec_spec.get("mcu", "?")}  │  '
        f'Bus: {", ".join(elec_spec.get("communication", []))}'
    )
    svg_parts.append(
        f'<text x="{W//2}" y="{stats_y + 22}" text-anchor="middle" '
        f'fill="#94A3B8" font-size="10">{stats_text}</text>'
    )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# ── Public entry point ────────────────────────────────────────────────────────

async def generate_circuit(cad_spec: dict) -> dict:
    """
    Main entry point called by the FastAPI route.

    Returns:
      svg          — SVG schematic string
      components   — list of component dicts (BOM)
      power_rails  — list of rail name strings
      elec_spec    — electrical requirements dict
      bom          — formatted BOM for display
    """
    ctype = cad_spec.get("component_type", "default")

    # 1. Electronics Agent
    elec_spec = await _electronics_agent(cad_spec)

    # 2. Select component set
    comps = COMPONENT_DB.get(ctype, COMPONENT_DB["default"])

    # Scale motor count from CAD spec
    motor_count = int(cad_spec.get("motor_count", 4))
    scaled_comps = []
    for c in comps:
        if "-" in c["ref"] and c["type"] in ("motor", "servo"):
            # Expand M1-M4 → M1, M2, M3, M4
            base = c["ref"].split("-")[0][0]
            for i in range(1, motor_count + 1):
                scaled_comps.append({**c, "ref": f"{base}{i}"})
        else:
            scaled_comps.append(c)

    # 3. Power rails
    rails = POWER_RAILS.get(ctype, POWER_RAILS["default"])

    # 4. SVG schematic
    svg = _render_svg(scaled_comps, rails, elec_spec)

    # 5. BOM
    bom = []
    total_cost = 0.0
    cost_map = {
        "flight_controller": 89.0, "mcu": 12.0, "esc": 45.0,
        "bec": 8.0, "ldo": 1.5, "buck": 6.0, "battery": 35.0,
        "motor": 18.0, "servo": 12.0, "servo_driver": 5.0,
        "receiver": 22.0, "gps": 48.0, "telemetry": 35.0,
        "vtx": 28.0, "camera": 25.0, "sensor": 4.0,
        "charger": 2.5, "connector": 1.0,
        "resistor": 0.05, "capacitor": 0.2,
        "can_transceiver": 3.0, "motor_driver": 8.0,
    }
    for c in scaled_comps:
        cost = cost_map.get(c["type"], 2.0)
        total_cost += cost
        bom.append({
            "ref":      c["ref"],
            "name":     c["name"],
            "type":     c["type"],
            "voltage":  c.get("voltage", ""),
            "current":  (f"{c['current_ma']/1000:.1f}A"
                         if c.get("current_ma", 0) >= 1000
                         else f"{c.get('current_ma', 0)}mA"),
            "package":  c.get("package", ""),
            "est_cost": f"${cost:.2f}",
        })

    return {
        "svg":        svg,
        "components": scaled_comps,
        "bom":        bom,
        "bom_total":  f"${total_cost:.2f}",
        "power_rails": rails,
        "elec_spec":  elec_spec,
    }
