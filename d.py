import re
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.path import Path
from matplotlib.patches import Circle, PathPatch, Polygon


# ============================================================
# LOGICGATE PRO - DIGITAL LOGIC GATE IDENTIFIER
# FILE: d.py
# ============================================================

st.set_page_config(
    page_title="LogicGate Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========================== CUSTOM CSS ==========================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background: #070a12;
    color: #edf4ff;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

/* HEADER */

header[data-testid="stHeader"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
.stAppHeader {
    background: #070a12 !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #090e19;
    border-right: 1px solid #202b40;
}

/* TEXT */

h1, h2, h3 {
    color: #f4f8ff !important;
}

p, label {
    color: #c4d0e2;
}

/* HEADINGS */

.hero {
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 800;
    line-height: 1.12;
    color: #f4f8ff;
}

.cyan {
    color: #43d9ff;
}

.subtitle {
    color: #91a4bd;
    font-size: .95rem;
    line-height: 1.7;
}

/* CARDS */

.panel {
    background: #0d1422;
    border: 1px solid #24334b;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
}

.metric-card {
    background: #101a2b;
    border: 1px solid #263750;
    border-radius: 14px;
    padding: 17px;
    min-height: 105px;
    width: 100%;
    box-sizing: border-box;
}

.metric-label {
    color: #91a4bd;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-value {
    color: #43d9ff;
    font-size: 25px;
    font-weight: 800;
    margin-top: 8px;
    overflow-wrap: anywhere;
}

/* BUTTONS */

.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(100deg, #147da7, #405fd0);
    color: white;
    border: 0;
    border-radius: 9px;
    font-weight: 700;
    min-height: 42px;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border: 1px solid #43d9ff;
    color: white;
}

/* TEXT AREA */

.stTextArea textarea {
    background: #0a1120 !important;
    color: #edf4ff !important;
    border: 1px solid #2a3a55 !important;
    border-radius: 10px !important;
}

/* SELECT BOX */

[data-baseweb="select"] > div {
    background: #0a1120;
}

/* DARK ALERTS */

[data-testid="stAlert"] {
    background: #101a2b !important;
    border: 1px solid #263750 !important;
    border-radius: 12px !important;
}

[data-testid="stAlert"] p {
    color: #dce8fa !important;
}

/* SIMULATOR STATUS */

.output-status {
    background: #101a2b;
    border: 1px solid #263750;
    border-radius: 10px;
    padding: 13px 17px;
    margin-top: 15px;
    color: #43d9ff;
    font-weight: 700;
}

/* DIVIDER */

hr {
    border-color: #202b40;
}

</style>
""", unsafe_allow_html=True)


# ========================== GATE DATA ==========================

GATES = {

    "AND": {
        "expression": "Y = A · B",
        "description": "The output is HIGH only when both inputs are HIGH.",
        "inputs": 2
    },

    "OR": {
        "expression": "Y = A + B",
        "description": "The output is HIGH when at least one input is HIGH.",
        "inputs": 2
    },

    "NOT": {
        "expression": "Y = A̅",
        "description": "The output is the complement of the input.",
        "inputs": 1
    },

    "NAND": {
        "expression": "Y = (A · B)̅",
        "description": "The output is LOW only when both inputs are HIGH.",
        "inputs": 2
    },

    "NOR": {
        "expression": "Y = (A + B)̅",
        "description": "The output is HIGH only when both inputs are LOW.",
        "inputs": 2
    },

    "XOR": {
        "expression": "Y = A ⊕ B",
        "description": "The output is HIGH when the two inputs are different.",
        "inputs": 2
    },

    "XNOR": {
        "expression": "Y = (A ⊕ B)̅",
        "description": "The output is HIGH when the two inputs are equal.",
        "inputs": 2
    }

}


SAMPLES = {

    "AND": "Output is HIGH only when both inputs are HIGH.",
    "OR": "Output is HIGH when at least one input is HIGH.",
    "NOT": "Output is opposite to the input.",
    "NAND": "Output is LOW only when both inputs are HIGH.",
    "NOR": "Output is HIGH only when both inputs are LOW.",
    "XOR": "Output is HIGH when inputs are different.",
    "XNOR": "Output is HIGH when inputs are equal."

}


# ========================== LOGIC FUNCTIONS ==========================

def gate_output(gate, a, b=0):

    a = int(bool(a))
    b = int(bool(b))

    if gate == "AND":
        return int(a and b)

    elif gate == "OR":
        return int(a or b)

    elif gate == "NOT":
        return int(not a)

    elif gate == "NAND":
        return int(not (a and b))

    elif gate == "NOR":
        return int(not (a or b))

    elif gate == "XOR":
        return int(a != b)

    elif gate == "XNOR":
        return int(a == b)

    raise ValueError("Unsupported logic gate")


def make_truth_table(gate):

    if gate == "NOT":

        return pd.DataFrame([
            {"A": a, "Y": gate_output("NOT", a)}
            for a in (0, 1)
        ])

    return pd.DataFrame([
        {
            "A": a,
            "B": b,
            "Y": gate_output(gate, a, b)
        }
        for a, b in [
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1)
        ]
    ])


# ========================== IDENTIFICATION ==========================

def identify_gate(description):

    text = re.sub(r"[-_]", " ", description.lower())
    text = " ".join(text.split())

    for name in ("xnor", "nand", "nor", "xor"):

        if re.search(r"\b" + name + r"\b", text):
            return name.upper(), "Explicit gate name detected."

    for name in ("and", "or", "not"):

        if (
            re.search(r"\b" + name + r"\s+gate\b", text)
            or re.search(r"\bgate\s+" + name + r"\b", text)
        ):
            return name.upper(), "Explicit gate name detected."

    rules = [

        ("XNOR", [
            "inputs are equal",
            "both inputs are equal",
            "inputs are the same",
            "same inputs",
            "inputs match",
            "inputs are identical"
        ]),

        ("XOR", [
            "inputs are different",
            "different inputs",
            "inputs differ",
            "inputs are unequal",
            "either input but not both"
        ]),

        ("NAND", [
            "output is low only when both inputs are high",
            "output is low when both inputs are high",
            "low only when both inputs are high",
            "complement of and",
            "opposite of and"
        ]),

        ("NOR", [
            "output is high only when both inputs are low",
            "output is high when both inputs are low",
            "high only when both inputs are low",
            "complement of or",
            "opposite of or"
        ]),

        ("NOT", [
            "opposite of the input",
            "opposite to the input",
            "complement of the input",
            "inverts the input",
            "inverted input",
            "reverses the input"
        ]),

        ("AND", [
            "output is high only when both inputs are high",
            "only when both inputs are high",
            "both inputs are high",
            "all inputs are high",
            "logical multiplication"
        ]),

        ("OR", [
            "output is high when at least one input is high",
            "at least one input is high",
            "either input is high",
            "one or more inputs are high",
            "logical addition"
        ])

    ]

    for gate, phrases in rules:

        if any(phrase in text for phrase in phrases):
            return gate, "Matched a known input/output behaviour."

    return None, "No supported gate pattern was found. Try one of the examples."


# ========================== CIRCUIT DIAGRAMS ==========================

def draw_gate(gate):

    fig, ax = plt.subplots(figsize=(7.4, 3.35), dpi=150)

    background = "#0b1220"
    white = "#d9e8ff"
    cyan = "#43d9ff"

    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    lw = 2.5

    # NOT GATE

    if gate == "NOT":

        ax.plot([0.65, 3.0], [2.5, 2.5], color=white, lw=lw)

        ax.text(
            0.42, 2.5, "A",
            color=cyan, fontsize=13,
            ha="right", va="center", weight="bold"
        )

        triangle = Polygon(
            [(3.0, 1.5), (3.0, 3.5), (5.65, 2.5)],
            closed=True,
            fill=False,
            edgecolor=white,
            linewidth=lw
        )

        ax.add_patch(triangle)

        ax.add_patch(
            Circle(
                (5.86, 2.5), 0.17,
                fill=False,
                edgecolor=cyan,
                linewidth=lw
            )
        )

        ax.plot([6.03, 8.75], [2.5, 2.5], color=white, lw=lw)

    else:

        ax.plot([0.65, 2.4], [3.35, 3.35], color=white, lw=lw)
        ax.plot([0.65, 2.4], [1.65, 1.65], color=white, lw=lw)

        ax.text(
            0.42, 3.35, "A",
            color=cyan, fontsize=13,
            ha="right", va="center", weight="bold"
        )

        ax.text(
            0.42, 1.65, "B",
            color=cyan, fontsize=13,
            ha="right", va="center", weight="bold"
        )

        # AND / NAND

        if gate in ("AND", "NAND"):

            and_path = Path(
                [
                    (2.4, 1.15),
                    (2.4, 3.85),
                    (4.4, 3.85),
                    (6.0, 3.25),
                    (6.0, 2.5),
                    (6.0, 1.75),
                    (4.4, 1.15),
                    (2.4, 1.15),
                    (2.4, 1.15)
                ],
                [
                    Path.MOVETO,
                    Path.LINETO,
                    Path.CURVE4,
                    Path.CURVE4,
                    Path.CURVE4,
                    Path.CURVE4,
                    Path.CURVE4,
                    Path.CURVE4,
                    Path.CLOSEPOLY
                ]
            )

            ax.add_patch(
                PathPatch(
                    and_path,
                    fill=False,
                    edgecolor=white,
                    linewidth=lw,
                    capstyle="round",
                    joinstyle="round"
                )
            )

            output_start = 6.0

        # OR / NOR / XOR / XNOR

        else:

            or_path = Path(
                [
                    (2.25, 1.15),

                    (3.4, 1.2),
                    (5.2, 1.5),
                    (6.0, 2.5),

                    (5.2, 3.5),
                    (3.4, 3.8),
                    (2.25, 3.85),

                    (2.9, 3.1),
                    (2.9, 1.9),
                    (2.25, 1.15),

                    (2.25, 1.15)
                ],
                [
                    Path.MOVETO,
                    Path.CURVE4, Path.CURVE4, Path.CURVE4,
                    Path.CURVE4, Path.CURVE4, Path.CURVE4,
                    Path.CURVE4, Path.CURVE4, Path.CURVE4,
                    Path.CLOSEPOLY
                ]
            )

            ax.add_patch(
                PathPatch(
                    or_path,
                    fill=False,
                    edgecolor=white,
                    linewidth=lw
                )
            )

            if gate in ("XOR", "XNOR"):

                xor_extra = Path(
                    [
                        (1.85, 1.15),
                        (2.5, 1.55),
                        (2.75, 2.0),
                        (2.75, 2.5),
                        (2.75, 3.0),
                        (2.5, 3.45),
                        (1.85, 3.85)
                    ],
                    [
                        Path.MOVETO,
                        Path.CURVE4,
                        Path.CURVE4,
                        Path.CURVE4,
                        Path.CURVE4,
                        Path.CURVE4,
                        Path.CURVE4
                    ]
                )

                ax.add_patch(
                    PathPatch(
                        xor_extra,
                        fill=False,
                        edgecolor=cyan,
                        linewidth=1.8
                    )
                )

            output_start = 6.0

        # INVERSION BUBBLES

        if gate in ("NAND", "NOR", "XNOR"):

            bubble_x = output_start + 0.20

            ax.add_patch(
                Circle(
                    (bubble_x, 2.5),
                    0.17,
                    fill=False,
                    edgecolor=cyan,
                    linewidth=lw
                )
            )

            ax.plot(
                [bubble_x + 0.17, 8.75],
                [2.5, 2.5],
                color=white,
                lw=lw
            )

        else:

            ax.plot(
                [output_start, 8.75],
                [2.5, 2.5],
                color=white,
                lw=lw
            )

    ax.text(
        8.90, 2.5, "Y",
        color=cyan,
        fontsize=13,
        ha="left",
        va="center",
        weight="bold"
    )

    ax.text(
        5.0, 0.35,
        f"{gate} GATE",
        color="#91a4bd",
        fontsize=9,
        ha="center",
        va="center",
        family="monospace"
    )

    fig.tight_layout(pad=0.25)

    return fig


def show_gate_diagram(gate):

    fig = draw_gate(gate)

    st.pyplot(fig, use_container_width=True)

    plt.close(fig)


# ========================== SESSION STATE ==========================

if "history" not in st.session_state:
    st.session_state.history = []

if "identified_gate" not in st.session_state:
    st.session_state.identified_gate = None

if "description_input" not in st.session_state:
    st.session_state.description_input = ""

if "identify_reason" not in st.session_state:
    st.session_state.identify_reason = ""


def clear_description():

    st.session_state.description_input = ""
    st.session_state.identified_gate = None
    st.session_state.identify_reason = ""


# ========================== SIDEBAR ==========================

with st.sidebar:

    st.markdown("## ⚡ LogicGate Pro")

    st.caption("Digital Electronics Workspace")

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Gate Identifier",
            "Gate Library",
            "Truth Table",
            "About Project"
        ]
    )

    st.markdown("---")

    st.markdown("**SUPPORTED GATES**")

    st.markdown("""
    `AND`  `OR`  `NOT`

    `NAND`  `NOR`

    `XOR`  `XNOR`
    """)

    st.markdown("---")

    st.caption("Built with Python, Streamlit, Matplotlib and Pandas")


# ========================== DASHBOARD ==========================

if page == "Dashboard":

    st.markdown(
        '<div class="hero">Welcome to '
        '<span class="cyan">LogicGate Pro</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">A digital logic gate identification and simulation platform.</p>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    cards = [
        (c1, "Supported gates", "07"),
        (c2, "Interactive simulator", "ACTIVE"),
        (c3, "Project status", "READY")
    ]

    for col, label, value in cards:

        with col:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.markdown("### Project Overview")

    st.write(
        "LogicGate Pro identifies fundamental digital logic gates "
        "from natural-language descriptions. It also displays circuit "
        "diagrams, Boolean expressions, truth tables and an interactive "
        "logic simulator."
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Recent Identification History")

    if st.session_state.history:

        st.dataframe(
            pd.DataFrame(st.session_state.history),
            hide_index=True,
            use_container_width=True
        )

    else:

        st.info("No identification history available yet.")


# ========================== GATE IDENTIFIER ==========================

elif page == "Gate Identifier":

    st.markdown(
        '<div class="hero">Digital Logic Gate '
        '<span class="cyan">Identifier</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">Describe the circuit behaviour and identify its logic gate.</p>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1.2, 0.8], gap="large")

    with left:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### Describe Your Circuit")

        sample = st.selectbox(
            "Choose an example",
            [
                "Choose a sample...",
                "AND",
                "OR",
                "NOT",
                "NAND",
                "NOR",
                "XOR",
                "XNOR"
            ],
            key="sample_choice"
        )

        if sample in SAMPLES:
            st.session_state.description_input = SAMPLES[sample]

        st.text_area(
            "Enter circuit description",
            key="description_input",
            height=125,
            placeholder="Example: Output is HIGH only when both inputs are HIGH."
        )

        b1, b2 = st.columns(2)

        with b1:

            identify_clicked = st.button(
                "⚡ Identify Gate",
                use_container_width=True
            )

        with b2:

            st.button(
                "Clear Input",
                on_click=clear_description,
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### How to use")

        st.write("1. Enter a circuit description.")
        st.write("2. Click Identify Gate.")
        st.write("3. View the circuit diagram.")
        st.write("4. Check the truth table.")
        st.write("5. Test the inputs using the simulator.")

        st.markdown("</div>", unsafe_allow_html=True)

    if identify_clicked:

        current_description = st.session_state.description_input.strip()

        if not current_description:

            st.warning("Please enter a circuit description.")

        else:

            detected, reason = identify_gate(current_description)

            st.session_state.identified_gate = detected
            st.session_state.identify_reason = reason

            if detected:

                st.session_state.history.insert(
                    0,
                    {
                        "Gate": detected,
                        "Description": current_description,
                        "Time": datetime.now().strftime("%d-%m-%Y %H:%M")
                    }
                )

                st.session_state.history = st.session_state.history[:10]

    gate = st.session_state.identified_gate

    if gate:

        st.write("")

        st.markdown("## Identification Result")

        c1, c2, c3 = st.columns(3)

        result_cards = [
            (c1, "Detected gate", gate),
            (c2, "Boolean expression", GATES[gate]["expression"]),
            (c3, "Number of inputs", str(GATES[gate]["inputs"]))
        ]

        for col, label, value in result_cards:

            with col:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.write("")

        d1, d2 = st.columns([1.1, 0.9], gap="large")

        with d1:

            st.markdown('<div class="panel">', unsafe_allow_html=True)

            st.markdown("### Circuit Diagram")

            show_gate_diagram(gate)

            st.markdown("</div>", unsafe_allow_html=True)

        with d2:

            st.markdown('<div class="panel">', unsafe_allow_html=True)

            st.markdown("### Working Principle")

            st.write(GATES[gate]["description"])

            st.caption(st.session_state.identify_reason)

            st.markdown("### Truth Table")

            table = make_truth_table(gate)

            st.dataframe(
                table,
                hide_index=True,
                use_container_width=True
            )

            st.download_button(
                "Download Truth Table CSV",
                table.to_csv(index=False).encode("utf-8"),
                file_name=f"{gate.lower()}_truth_table.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

        # ====================================================
        # INTERACTIVE SIMULATOR - ALIGNED OUTPUT CARDS
        # ====================================================

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### Interactive Logic Simulator")

        st.caption("Change the input switches to calculate the output.")

        # FIRST ROW: INPUT SWITCHES

        if gate == "NOT":

            a = st.toggle(
                "Input A",
                key="sim_input_a"
            )

            output = gate_output(gate, a)

            # SECOND ROW: TWO ALIGNED CARDS

            st.write("")

            col_a, col_y = st.columns(2, gap="medium")

            with col_a:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">INPUT A</div>
                        <div class="metric-value">{int(a)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_y:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">OUTPUT Y</div>
                        <div class="metric-value">{output}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            switch_a, switch_b = st.columns(2, gap="medium")

            with switch_a:

                a = st.toggle(
                    "Input A",
                    key="sim_input_a"
                )

            with switch_b:

                b = st.toggle(
                    "Input B",
                    key="sim_input_b"
                )

            output = gate_output(gate, a, b)

            # SECOND ROW: ALL THREE CARDS IN ONE ROW

            st.write("")

            col_a, col_b, col_y = st.columns(3, gap="medium")

            with col_a:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">INPUT A</div>
                        <div class="metric-value">{int(a)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_b:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">INPUT B</div>
                        <div class="metric-value">{int(b)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_y:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">OUTPUT Y</div>
                        <div class="metric-value">{output}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # DARK OUTPUT STATUS

        if output == 1:

            st.markdown(
                """
                <div class="output-status">
                    ● OUTPUT STATUS: HIGH (1)
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="output-status">
                    ● OUTPUT STATUS: LOW (0)
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    elif identify_clicked and st.session_state.description_input.strip():

        st.error("Gate could not be identified.")

        st.caption(st.session_state.identify_reason)

    # IDENTIFICATION HISTORY

    if st.session_state.history:

        with st.expander("Identification History"):

            st.dataframe(
                pd.DataFrame(st.session_state.history),
                hide_index=True,
                use_container_width=True
            )

            if st.button("Clear History"):

                st.session_state.history = []

                st.rerun()


# ========================== GATE LIBRARY ==========================

elif page == "Gate Library":

    st.markdown(
        '<div class="hero">Logic Gate '
        '<span class="cyan">Library</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">Explore all seven fundamental digital logic gates.</p>',
        unsafe_allow_html=True
    )

    selected = st.selectbox(
        "Select a logic gate",
        list(GATES.keys())
    )

    left, right = st.columns([1.1, 0.9], gap="large")

    with left:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown(f"### {selected} Gate")

        show_gate_diagram(selected)

        st.write(GATES[selected]["description"])

        st.markdown(
            f"**Boolean Expression:** `{GATES[selected]['expression']}`"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("### Truth Table")

        table = make_truth_table(selected)

        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True
        )

        st.download_button(
            "Download CSV",
            table.to_csv(index=False).encode("utf-8"),
            file_name=f"{selected.lower()}_truth_table.csv",
            mime="text/csv"
        )

        st.markdown("</div>", unsafe_allow_html=True)


# ========================== TRUTH TABLE ==========================

elif page == "Truth Table":

    st.markdown(
        '<div class="hero">Truth Table '
        '<span class="cyan">Generator</span></div>',
        unsafe_allow_html=True
    )

    selected = st.selectbox(
        "Choose a gate",
        list(GATES.keys()),
        key="truth_gate"
    )

    table = make_truth_table(selected)

    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.markdown(f"### {selected} Gate Truth Table")

    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        "Download Truth Table",
        table.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected.lower()}_truth_table.csv",
        mime="text/csv"
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ========================== ABOUT PROJECT ==========================

elif page == "About Project":

    st.markdown(
        '<div class="hero">About '
        '<span class="cyan">LogicGate Pro</span></div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.markdown("### Project Overview")

    st.write(
        "LogicGate Pro is a Python-based educational application "
        "that identifies digital logic gates from natural-language descriptions."
    )

    st.markdown("### Technologies Used")

    st.write("- Python")
    st.write("- Streamlit")
    st.write("- Matplotlib")
    st.write("- Pandas")

    st.markdown("### Supported Logic Gates")

    st.write("AND, OR, NOT, NAND, NOR, XOR and XNOR.")

    st.markdown("### Working Method")

    st.write(
        "The application uses predefined keyword and behaviour rules "
        "to identify a gate. It generates truth tables and calculates "
        "outputs using Boolean logic."
    )

    st.info(
        "The current identifier is rule-based. It is not a trained AI "
        "or machine-learning model. Clear descriptions give the most reliable results."
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ========================== FOOTER ==========================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#71839e;font-size:12px;">
        LOGICGATE PRO | DIGITAL ELECTRONICS PROJECT
        <br><br>
        BUILT WITH PYTHON AND STREAMLIT
    </div>
    """,
    unsafe_allow_html=True
)
