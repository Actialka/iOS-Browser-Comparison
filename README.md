# iOS Mobile Browser Performance Benchmark

An interactive data dashboard evaluating client-side browser performance and hardware efficiency across **Nadir**, a custom lean iOS web browser, **Apple Safari**, and **Brave** on iOS 26.4.2.

🔗 **Live Dashboard:** [View Streamlit Application](https://sophiafan-portfolio.streamlit.app/)

## Motivation & Objective

Most iOS browsers suffer from feature creep and visual bloat, while Safari carries long-standing UX constraints. To address this, I built Nadir - a streamlined, lightweight iOS browser focused strictly on core browsing speed and hardware efficiency. 

---

## Executive Summary & Core Insights

* **Hardware Efficiency Advantage:** Nadir reduced memory footprint by **57.77%** compared to native Safari while delivering **7.77% faster** average page loads.
* **Architecture Trade-Off:** Brave demonstrated an efficiency penalty with ad-blocking disabled, incurring a **68.45% latency increase** in load times.
* **Workload-Specific Divergence:** On complex, script-heavy media sites (News), unblocked ad auctions caused significant latency spikes, while static content (Reference) loaded in under 200 ms across engines.

---

## Test Methodology

* **Device Hardware:** iPhone 13 Pro running iOS 26.4.2.
* **Network Environment:** Stable residential Wi-Fi under identical, unmetered network conditions.
* **Baseline Controls:** Ad-blocking and content shields were explicitly disabled across all browsers to establish a standardized baseline.
* **Data Collection:** Metrics extracted using Safari Web Inspector and Xcode Instruments via wired USB.

---

## Tech Stack & Architecture

* **Website Framework:** Streamlit
* **Data Processing & Analytics:** Python, Pandas, SQL
* **Visualization:** Plotly Express / Graph Objects
* **Data Collection:** Safari Web Inspector and Xcode Instruments

## Development & AI Workflow

* **AI-Assisted Prototyping:** Leveraged modern LLM developer tooling (Claude Code and OpenRouter) to assist in Swift code generation, bug fixes, and creating the website.
* **Manual User Testing and Bug Reporting**: Iterated on chat prompts to refine ideas and implementation. Tested the app manually on a physical device and Xcode iOS Simulators. Manually discovered bugs through daily use and worked with LLMs to fix them.
* Note: Nadir was developed as a private, bespoke research client for iOS and is not currently distributed on the App Store.
